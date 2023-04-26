import {
    Component,
    EventEmitter,
    HostBinding,
    HostListener,
    Input,
    Output,
} from '@angular/core';

@Component({
    selector: 'app-button',
    templateUrl: './button.component.html',
    styleUrls: ['./button.component.scss'],
})
export class ButtonComponent {
    @Output() private readonly onClick: EventEmitter<void> =
        new EventEmitter<void>();

    @HostBinding('class.disabled') @Input() disabled: boolean = false;

    @HostListener('click', ['$event']) private onClickCallback(): void {
        if (this.disabled) {
            return;
        }

        this.onClick.emit();
    }
}
