import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { HeaderComponent } from './shared/components/header/header.component';
import { MainComponent } from './routes/main/main.component';
import { ButtonComponent } from './shared/components/button/button.component';
import { WebcamComponent } from './routes/webcam/webcam.component';
import { UploadFilesComponent } from './routes/upload-files/upload-files.component';
import { AboutUsComponent } from './routes/about-us/about-us.component';
import { ContactUsComponent } from './routes/contact-us/contact-us.component';

// TODO: Organize modules in lazy manner
@NgModule({
    declarations: [
        AppComponent,
        HeaderComponent,
        MainComponent,
        ButtonComponent,
        WebcamComponent,
        UploadFilesComponent,
        AboutUsComponent,
        ContactUsComponent,
    ],
    imports: [BrowserModule, AppRoutingModule],
    bootstrap: [AppComponent],
})
export class AppModule {}
