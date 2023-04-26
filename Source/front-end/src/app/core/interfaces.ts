export interface IProcessEndpointRequestBody {
    filesToProcess: IFile[];
    pipelines: ProcessingPluginType[];
}

export interface IFile {
    data: string;
    mediaType: string;
}

export enum ProcessingPluginType {
    FaceRecognition = 'face_recognition',
}
