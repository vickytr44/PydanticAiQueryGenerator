import { createReducer, on } from '@ngrx/store';
import * as ChatActions from '../actions/chat-bot.actions';
import { ChatResponse } from '../../model/chat-bot.model';

export interface ChatState {
  messages: { from: 'user' | 'ai', text: string }[];
  typing: boolean;
  error: string | null;
}

export const initialState: ChatState = {
  messages: [],
  typing: false,
  error: null
};

export const chatReducer = createReducer(
  initialState,
  on(ChatActions.sendMessage, (state, { request }) => ({
    ...state,
    messages: [...state.messages, { from: 'user' as const, text: request.message }],
    typing: true,
    error: null
  })),
  on(ChatActions.sendMessageSuccess, (state, { response }) => ({
    ...state,
    messages: [...state.messages, { from: 'ai' as const, text: response.response }],
    typing: false,
  })),
  on(ChatActions.sendMessageFailure, (state, { error }) => ({
    ...state,
    typing: false,
    messages: [...state.messages, { from: 'ai' as const, text: error }],
    error
  })),
  on(ChatActions.resetChat, () => ({
    ...initialState
  })),
  on(ChatActions.addMessage, (state, { message }) => ({
    ...state,
    messages: [...state.messages, message]
  }))
);