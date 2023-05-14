import { Location } from '@angular/common';
import { Component, OnDestroy, OnInit } from '@angular/core';
import { Subscription, fromEvent, map, switchMap, tap } from 'rxjs';
import {
    IFile,
    IProcessEndpointResponseBody,
    ProcessingPluginType,
} from 'src/app/core/interfaces';
import { ProcessService } from 'src/app/services/process.service';

@Component({
    selector: 'app-upload-files',
    templateUrl: './upload-files.component.html',
    styleUrls: ['./upload-files.component.scss'],
})
export class UploadFilesComponent implements OnInit, OnDestroy {
    public readonly filesToProcessPreviewURLs: string[] = [];
    public readonly processedFilesPreviewURLs: string[] = [];

    public get processAvailable(): boolean {
        return this.filesToProcess.length > 0;
    }

    private readonly filesInput: HTMLInputElement =
        document.createElement('input');

    private readonly filesToProcess: IFile[] = [];
    private readonly processedFiles: Blob[] = [];

    private readonly subscription: Subscription = new Subscription();

    constructor(
        private readonly processService: ProcessService,
        private readonly location: Location
    ) {
        const locationState: {
            filePreviewURL?: string;
            fileToProcess?: IFile;
        } = this.location.getState() as {
            filePreviewURL?: string;
            fileToProcess?: IFile;
        };

        if (locationState.filePreviewURL && locationState.fileToProcess) {
            this.filesToProcessPreviewURLs.push(locationState.filePreviewURL);
            this.filesToProcess.push(locationState.fileToProcess);
        }

        this.filesInput.type = 'file';
        this.filesInput.multiple = true;
    }

    public ngOnInit(): void {
        const filesUploadSub: Subscription = fromEvent(
            this.filesInput,
            'change'
        )
            .pipe(
                map(this.extractFilesFromEvent.bind(this)),
                map(this.filterOutUnsupportedFiles.bind(this)),
                tap(async (files: File[]) => {
                    this.filesToProcessPreviewURLs.push(
                        ...(await this.extractFilesPreviewURLs(files))
                    );
                }),
                switchMap(this.convertFilesToBase64.bind(this)),
                tap((base64Files: IFile[]) =>
                    this.filesToProcess.push(...base64Files)
                )
            )
            .subscribe();

        this.subscription.add(filesUploadSub);
    }

    public onRemoveFile(index: number): void {
        this.filesToProcessPreviewURLs.splice(index, 1);
        this.filesToProcess.splice(index, 1);

        this.filesInput.files = this.getFileListFromFiles(
            Array.from(this.filesInput.files as FileList).filter(
                (_, i) => i !== index
            )
        );
    }

    public onUpload(): void {
        this.filesInput.click();
    }

    public onDownload(index: number): void {
        const link: HTMLAnchorElement = document.createElement('a');

        link.href = URL.createObjectURL(this.processedFiles[index]);
        link.download = `${index + 1}`;
        link.click();
    }

    public onProcess(): void {
        this.processedFilesPreviewURLs.splice(
            0,
            this.processedFilesPreviewURLs.length
        );
        this.processedFiles.splice(0, this.processedFiles.length);

        this.processService
            .process({
                filesToProcess: this.filesToProcess,
                pipelines: [ProcessingPluginType.FaceRecognition],
            })
            .pipe(
                tap((response: IProcessEndpointResponseBody) =>
                    this.processedFilesPreviewURLs.push(
                        ...this.extractResponsesPreviewURLs(response.images)
                    )
                ),
                tap((response: IProcessEndpointResponseBody) =>
                    this.processedFiles.push(
                        ...response.images.map((currentFileData: string) =>
                            this.convertBase64ToBlob(currentFileData)
                        )
                    )
                )
            )
            .subscribe();
    }

    public ngOnDestroy(): void {
        this.subscription.unsubscribe();
    }

    private extractFilesFromEvent(event: Event): File[] {
        return Array.from((event.target as HTMLInputElement).files as FileList);
    }

    private filterOutUnsupportedFiles(files: File[]): File[] {
        const filteredFiles: File[] = files.filter(
            (currentFile: File) =>
                currentFile.type.includes('image/jpg') ||
                currentFile.type.includes('image/jpeg') ||
                currentFile.type.includes('video/mp4')
        );

        this.filesInput.files = this.getFileListFromFiles(filteredFiles);

        return filteredFiles;
    }

    private extractFilesPreviewURLs(files: File[]): Promise<string[]> {
        return Promise.all(
            files.map(
                (currentFile: File) =>
                    new Promise((resolve) => {
                        if (currentFile.type.includes('video/mp4')) {
                            resolve(this.getVideoPreviewUrl(currentFile));

                            return;
                        }

                        resolve(this.getImagePreviewUrl(currentFile));
                    })
            ) as Promise<string>[]
        );
    }

    private extractResponsesPreviewURLs(responseData: string[]): string[] {
        return responseData.map((currentFileData: string) => {
            if (currentFileData.includes('video/mp4')) {
                return '/assets/icons/video.png';
            }

            const file: Blob = this.convertBase64ToBlob(currentFileData);

            return this.getImagePreviewUrl(file);
        });
    }

    private getImagePreviewUrl(file: File | Blob): string {
        return URL.createObjectURL(
            new Blob([file], {
                type: file.type,
            })
        );
    }

    private getVideoPreviewUrl(file: File | Blob): Promise<string> {
        return new Promise((resolve) => {
            const videoURL: string = URL.createObjectURL(file);

            const videoElement: HTMLVideoElement =
                document.createElement('video');

            const canvasElement: HTMLCanvasElement =
                document.createElement('canvas');

            videoElement.src = videoURL;
            videoElement.muted = true;

            videoElement.play();

            videoElement.addEventListener('loadeddata', () => {
                canvasElement.width = videoElement.videoWidth;
                canvasElement.height = videoElement.videoHeight;

                canvasElement
                    .getContext('2d')!
                    .drawImage(
                        videoElement,
                        0,
                        0,
                        videoElement.videoWidth,
                        videoElement.videoHeight
                    );

                videoElement.pause();

                canvasElement.toBlob((blob: Blob | null) => {
                    resolve(URL.createObjectURL(blob as Blob));
                }, 'image/jpeg');
            });
        });
    }

    private convertFilesToBase64(files: File[]): Promise<IFile[]> {
        const base64Promises: Promise<IFile>[] = [];

        files.forEach((currentFile: File) => {
            base64Promises.push(this.getFileData(currentFile));
        });

        return Promise.all(base64Promises);
    }

    private getFileData(file: File): Promise<IFile> {
        const fileReader: FileReader = new FileReader();

        return new Promise((resolve, reject) => {
            fileReader.addEventListener('load', () => {
                resolve({
                    data: fileReader.result as string,
                    mediaType: file.type,
                });
            });

            fileReader.readAsDataURL(file);
        });
    }

    private getFileListFromFiles(files: File[]): FileList {
        return files.reduce((dataTransferObject: DataTransfer, file: File) => {
            dataTransferObject.items.add(file);

            return dataTransferObject;
        }, new DataTransfer()).files;
    }

    private convertBase64ToBlob(base64: string): Blob {
        const byteCharacters: string = atob(base64.split(',')[1]);
        const byteArrays: number[] = [];

        for (let i = 0; i < byteCharacters.length; i++) {
            byteArrays.push(byteCharacters.charCodeAt(i));
        }

        const byteArray = new Uint8Array(byteArrays);

        return new Blob([byteArray], {
            type: this.getFileTypeFromBase64(base64),
        });
    }

    private getFileTypeFromBase64(base64: string): string {
        return base64.split(';')[0].split(':')[1];
    }
}
