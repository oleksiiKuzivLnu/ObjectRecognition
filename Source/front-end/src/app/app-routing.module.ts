import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { MainComponent } from './routes/main/main.component';
import { WebcamComponent } from './routes/webcam/webcam.component';
import { UploadFilesComponent } from './routes/upload-files/upload-files.component';
import { AboutUsComponent } from './routes/about-us/about-us.component';
import { ContactUsComponent } from './routes/contact-us/contact-us.component';

const routes: Routes = [
    {
        path: 'main',
        component: MainComponent,
    },
    {
        path: 'webcam',
        component: WebcamComponent,
    },
    {
        path: 'upload-files',
        component: UploadFilesComponent,
    },
    {
        path: 'about-us',
        component: AboutUsComponent,
    },
    {
        path: 'contact-us',
        component: ContactUsComponent,
    },
    { path: '**', redirectTo: 'main' },
];

@NgModule({
    imports: [RouterModule.forRoot(routes)],
    exports: [RouterModule],
})
export class AppRoutingModule {}
