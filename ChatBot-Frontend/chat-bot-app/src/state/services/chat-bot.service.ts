import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { ChatRequest, ChatResponse } from '../../model/chat-bot.model';

@Injectable({ providedIn: 'root' })
export class ChatService {
  private readonly API_URL =  'http://localhost:8080/chat'; //'https://localhost:7036/ChatBot';

  constructor(private http: HttpClient) {}

  sendMessage(request: ChatRequest): Observable<ChatResponse> {
    const headers = new HttpHeaders({
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    });
    return this.http.post<ChatResponse>(this.API_URL, request, { headers });
  }
}
