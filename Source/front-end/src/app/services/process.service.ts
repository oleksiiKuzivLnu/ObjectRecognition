import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { IProcessEndpointRequestBody } from '../core/interfaces';

@Injectable({
    providedIn: 'root',
})
export class ProcessService {
    private readonly baseUrl: string = 'http://localhost:5000';

    constructor(private readonly httpClient: HttpClient) {}

    public process(payload: IProcessEndpointRequestBody): Observable<unknown> {
        return this.httpClient.post(`${this.baseUrl}/process`, payload);
    }
}
