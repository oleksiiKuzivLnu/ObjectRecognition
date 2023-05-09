import { Component, EventEmitter, Input, Output } from '@angular/core';

@Component({
    selector: 'app-gallery',
    templateUrl: './gallery.component.html',
    styleUrls: ['./gallery.component.scss'],
})
export class GalleryComponent {
    @Input() public imagesUrls: string[] = [];
    @Input() public allowImagesDeletion: boolean = false;

    @Output() public onPhotoDelete: EventEmitter<number> = new EventEmitter<number>();
}
