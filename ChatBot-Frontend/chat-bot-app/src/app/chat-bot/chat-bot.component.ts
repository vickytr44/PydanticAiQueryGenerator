import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Store } from '@ngrx/store';
import * as ChatActions from '../../state/actions/chat-bot.actions';
import { selectChatMessages, selectTypingStatus } from '../../state/selectors/chat-bot.selectors';
import { LinkifyPipe } from '../../helper/linkify.pipe';

@Component({
  selector: 'app-chat-bot',
  imports: [CommonModule, FormsModule, LinkifyPipe],
  standalone: true,
  templateUrl: './chat-bot.component.html',
  styleUrl: './chat-bot.component.scss'
})
export class ChatBotComponent {
  message = '';
  messages$;
  typing$;

  constructor(private store: Store) {
    this.messages$ = this.store.select(selectChatMessages);
    this.typing$ = this.store.select(selectTypingStatus);
  }

  sendMessage(): void {
    const trimmedMessage = this.message.trim();
    if (trimmedMessage) {
      this.store.dispatch(ChatActions.sendMessage({ request: { message: trimmedMessage } }));
      this.message = '';
    }
  }
}
