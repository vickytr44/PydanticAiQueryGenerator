import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { ChatRequest, ChatResponse } from '../../model/chat-bot.model';

@Injectable({ providedIn: 'root' })
export class ChatService {
  private readonly API_URL = 'https://localhost:7036/ChatBot';

  constructor(private http: HttpClient) {}

  sendMessage(request: ChatRequest): Observable<ChatResponse> {
    return this.http.post<ChatResponse>(this.API_URL, request);
  }
}
