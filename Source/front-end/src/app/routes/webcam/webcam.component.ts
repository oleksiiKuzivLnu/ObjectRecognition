import {
    AfterViewInit,
    Component,
    ElementRef,
    NgZone,
    OnDestroy,
    ViewChild,
} from '@angular/core';
import { Router } from '@angular/router';
import { Subscription, from, tap } from 'rxjs';
import { IFile } from 'src/app/core/interfaces';

@Component({
    selector: 'app-webcam',
    templateUrl: './webcam.component.html',
    styleUrls: ['./webcam.component.scss'],
})
export class WebcamComponent implements AfterViewInit, OnDestroy {
    private webcamStreamObject!: MediaStream;

    @ViewChild('cameraOutput')
    private readonly cameraOutputElement!: ElementRef<HTMLVideoElement>;

    private readonly subscription: Subscription = new Subscription();

    constructor(
        private readonly router: Router,
        private readonly ngZone: NgZone
    ) {}

    public ngAfterViewInit(): void {
        const userMediaPromise: Promise<MediaStream> =
            navigator.mediaDevices.getUserMedia({
                audio: false,
                video: true,
            });

        const webcamSub: Subscription = from(userMediaPromise)
            .pipe(
                tap((stream: MediaStream) => {
                    this.cameraOutputElement.nativeElement.srcObject = stream;
                    this.cameraOutputElement.nativeElement.play();

                    this.webcamStreamObject = stream;
                })
            )
            .subscribe();

        this.subscription.add(webcamSub);
    }

    public onProcess(): void {
        const canvas: HTMLCanvasElement = document.createElement('canvas');
        const context: CanvasRenderingContext2D = canvas.getContext(
            '2d'
        ) as CanvasRenderingContext2D;

        canvas.width = this.cameraOutputElement.nativeElement.videoWidth;
        canvas.height = this.cameraOutputElement.nativeElement.videoHeight;

        context.drawImage(
            this.cameraOutputElement.nativeElement,
            0,
            0,
            canvas.width,
            canvas.height
        );

        canvas.toBlob(async (blob: Blob | null) => {
            this.ngZone.run(() =>
                this.router.navigate(['upload-files'], {
                    state: {
                        filePreviewURL: URL.createObjectURL(blob as Blob),
                        fileToProcess: {
                            data: canvas.toDataURL('image/jpeg'),
                            mediaType: 'image/jpeg',
                        } as IFile,
                    },
                })
            );
        });
    }

    public ngOnDestroy(): void {
        this.webcamStreamObject
            .getTracks()
            .forEach((track: MediaStreamTrack) => track.stop());

        this.subscription.unsubscribe();
    }
}
