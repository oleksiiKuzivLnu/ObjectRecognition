import { HttpClientModule, HTTP_INTERCEPTORS } from '@angular/common/http';
import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { AboutUsComponent } from './routes/about-us/about-us.component';
import { ContactUsComponent } from './routes/contact-us/contact-us.component';
import { MainComponent } from './routes/main/main.component';
import { UploadFilesComponent } from './routes/upload-files/upload-files.component';
import { WebcamComponent } from './routes/webcam/webcam.component';
import { ButtonComponent } from './shared/components/button/button.component';
import { HeaderComponent } from './shared/components/header/header.component';
import { GalleryComponent } from './shared/components/gallery/gallery.component';
import { ThreeObjLoaderComponent } from './three-obj-loader/three-obj-loader.component';
import { SpinnerInterceptor } from './interceptors/spinner.interceptor';
import { SpinnerComponent } from './shared/components/spinner/spinner.component';

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
        GalleryComponent,
        ThreeObjLoaderComponent,
        SpinnerComponent,
    ],
    imports: [BrowserModule, AppRoutingModule, HttpClientModule],
    bootstrap: [AppComponent],
    providers: [
        { provide: HTTP_INTERCEPTORS, useClass: SpinnerInterceptor, multi: true }
      ]
})
export class AppModule {}
