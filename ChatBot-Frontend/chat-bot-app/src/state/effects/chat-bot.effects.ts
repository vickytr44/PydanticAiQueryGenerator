import { Injectable } from '@angular/core';
import { Actions, createEffect, ofType } from '@ngrx/effects';
import { ChatService } from '../services/chat-bot.service';
import * as ChatActions from '../actions/chat-bot.actions';
import { catchError, map, mergeMap, of } from 'rxjs';

@Injectable()
export class ChatEffects {
  sendMessage$;

  constructor(private actions$: Actions, private chatService: ChatService) {
    this.sendMessage$ = createEffect(() =>
        this.actions$.pipe(
          ofType(ChatActions.sendMessage),
          mergeMap(({ request }) =>
            this.chatService.sendMessage(request).pipe(
              map(response => ChatActions.sendMessageSuccess({ response })),
              catchError(error => of(ChatActions.sendMessageFailure({ error: error.message || 'Error occurred' })))
            )
          )
        )
      );
  }
}
