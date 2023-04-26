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
    public uploadedImagesURLs: string[] = [];
    public processedImagesURLs: string[] = [];

    public get processAvailable(): boolean {
        return this.filesToProcess.length > 0;
    }

    public get downloadAvailable(): boolean {
        return this.processedImagesURLs.length > 0;
    }

    private readonly filesInput: HTMLInputElement =
        document.createElement('input');

    private readonly filesToProcess: IFile[] = [];

    private readonly subscription: Subscription = new Subscription();

    constructor(private readonly processService: ProcessService) {}

    public ngOnInit(): void {
        const filesUploadSub: Subscription = fromEvent(
            this.filesInput,
            'change'
        )
            .pipe(
                map(this.extractFilesFromEvent.bind(this)),
                tap((files: File[]) => {
                    this.uploadedImagesURLs.push(
                        ...this.extractFilesBlobURLs(files)
                    );
                }),
                switchMap(this.convertFilesToBase64.bind(this)),
                tap((base64Files: IFile[]) =>
                    this.filesToProcess.push(...base64Files)
                )
            )
            .subscribe();

        this.filesInput.type = 'file';
        this.filesInput.multiple = true;

        this.subscription.add(filesUploadSub);
    }

    public onUpload(): void {
        this.filesInput.click();
    }

    public onPhotoDelete(index: number): void {
        this.uploadedImagesURLs.splice(index, 1);
        this.filesToProcess.splice(index, 1);

        this.filesInput.files = Array.from(this.filesInput.files as FileList)
            .filter((_, i) => i !== index)
            .reduce((dataTransferObject, file: File) => {
                dataTransferObject.items.add(file);

                return dataTransferObject;
            }, new DataTransfer()).files;
    }

    public onDownload(): void {
        this.processedImagesURLs.forEach(
            (imageURL: string, currentImageIndex: number) => {
                const link: HTMLAnchorElement = document.createElement('a');

                link.href = imageURL;
                link.download = `${currentImageIndex + 1}.jpg`;
                link.click();
            }
        );
    }

    public onProcess(): void {
        this.processedImagesURLs = [];

        this.processService
            .process({
                filesToProcess: this.filesToProcess,
                pipelines: [ProcessingPluginType.FaceRecognition],
            })
            .pipe(
                tap((response: IProcessEndpointResponseBody) => {
                    this.processedImagesURLs.push(...response.images);
                })
            )
            .subscribe();
    }

    public ngOnDestroy(): void {
        this.subscription.unsubscribe();
    }

    private extractFilesFromEvent(event: Event): File[] {
        return Array.from((event.target as HTMLInputElement).files as FileList);
    }

    private extractFilesBlobURLs(files: File[]): string[] {
        return files.map((currentFile: File) =>
            URL.createObjectURL(
                new Blob([currentFile], {
                    type: currentFile.type,
                })
            )
        );
    }

    private async convertFilesToBase64(files: File[]): Promise<IFile[]> {
        const base64Promises: Promise<IFile>[] = [];

        files.forEach((currentFile: File) => {
            base64Promises.push(this.getFileData(currentFile));
        });

        return Promise.all(base64Promises);
    }

    private async getFileData(file: File): Promise<IFile> {
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
}
