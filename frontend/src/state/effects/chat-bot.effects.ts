import { Injectable } from '@angular/core';
import { Actions, createEffect, ofType } from '@ngrx/effects';
import { ChatService } from '../services/chat-bot.service';
import * as ChatActions from '../actions/chat-bot.actions';
import { catchError, map, mergeMap, of } from 'rxjs';
import { HttpErrorResponse } from '@angular/common/http';

@Injectable()
export class ChatEffects {
  sendMessage$;

  constructor(private actions$: Actions, private chatService: ChatService) {
    this.sendMessage$ = createEffect(() =>
        this.actions$.pipe(
          ofType(ChatActions.sendMessage),
          mergeMap(({ request }) =>
            this.chatService.sendMessage(request).pipe(
              map((response) => ChatActions.sendMessageSuccess({ response })),
              catchError((error:HttpErrorResponse) => {
                let fallbackMessage = 'An error occurred. Please try again later.';
                if (error.status === 500) {
                  fallbackMessage = 'Something went wrong. Please try again later.';
                }
                return of(ChatActions.sendMessageFailure({ error: fallbackMessage }));
              }))
          )
        )
      );
  }
}
