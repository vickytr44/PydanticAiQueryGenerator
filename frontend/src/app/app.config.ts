import { ApplicationConfig, provideZoneChangeDetection } from '@angular/core';
import { provideRouter } from '@angular/router';

import { routes } from './app.routes';
import { provideHttpClient } from '@angular/common/http';
import { provideStore } from '@ngrx/store';
import { chatReducer } from '../state/reducer/chat-bot.reducer';
import { provideEffects } from '@ngrx/effects';
import { ChatEffects } from '../state/effects/chat-bot.effects';
import { ChatService } from '../state/services/chat-bot.service';

export const appConfig: ApplicationConfig = {
  providers: [
    provideHttpClient(),
    provideZoneChangeDetection({ eventCoalescing: true }), 
    provideRouter(routes),
    provideStore({ chat: chatReducer }),
    provideEffects(ChatEffects),
    ChatService
  ]
};
