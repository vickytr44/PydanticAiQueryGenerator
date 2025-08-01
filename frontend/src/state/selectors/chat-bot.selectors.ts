import { createFeatureSelector, createSelector } from '@ngrx/store';
import { ChatState } from '../reducer/chat-bot.reducer';

export const selectChatFeature = createFeatureSelector<ChatState>('chat');
export const selectChatMessages = createSelector(selectChatFeature, state => state.messages);
export const selectTypingStatus = createSelector(
  selectChatFeature,
  (state: ChatState) => state.typing
);