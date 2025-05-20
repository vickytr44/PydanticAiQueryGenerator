import { createAction, props } from '@ngrx/store';
import { ChatRequest, ChatResponse } from '../../model/chat-bot.model';

export const sendMessage = createAction('[Chat] Send Message', props<{ request: ChatRequest }>());
export const sendMessageSuccess = createAction('[Chat] Send Message Success', props<{ response: ChatResponse }>());
export const sendMessageFailure = createAction('[Chat] Send Message Failure', props<{ error: string }>());