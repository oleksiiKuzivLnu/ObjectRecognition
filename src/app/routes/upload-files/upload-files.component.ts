import { Component, OnDestroy, OnInit } from '@angular/core';
import { Subscription, fromEvent, switchMap, tap } from 'rxjs';
import { IFile, ProcessingPluginType } from 'src/app/core/interfaces';
import { ProcessService } from 'src/app/services/process.service';

@Component({
    selector: 'app-upload-files',
    templateUrl: './upload-files.component.html',
    styleUrls: ['./upload-files.component.scss'],
})
export class UploadFilesComponent implements OnInit, OnDestroy {
    public get processAvailable(): boolean {
        return this.filesToProcess.length > 0;
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
                switchMap(this.onFilesUpload.bind(this)),
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

    public onProcess(): void {
        this.processService
            .process({
                filesToProcess: this.filesToProcess,
                pipelines: [ProcessingPluginType.FaceRecognition],
            })
            .subscribe();
    }

    private async onFilesUpload(event: Event): Promise<IFile[]> {
        const files: File[] = Array.from(
            (event.target as HTMLInputElement).files as FileList
        );

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

    public ngOnDestroy(): void {
        this.subscription.unsubscribe();
    }
}
