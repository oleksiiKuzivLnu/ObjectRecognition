import {
    AfterViewInit,
    Component,
    ElementRef,
    OnDestroy,
    ViewChild,
} from '@angular/core';
import { Subscription, from, tap } from 'rxjs';

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

    public ngOnDestroy(): void {
        this.webcamStreamObject
            .getTracks()
            .forEach((track: MediaStreamTrack) => track.stop());

        this.subscription.unsubscribe();
    }
}
