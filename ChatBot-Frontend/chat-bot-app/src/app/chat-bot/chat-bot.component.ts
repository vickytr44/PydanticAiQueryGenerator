import { CommonModule } from '@angular/common';
import { Component, ElementRef, ViewChild } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Store } from '@ngrx/store';
import * as ChatActions from '../../state/actions/chat-bot.actions';
import { selectChatMessages, selectTypingStatus } from '../../state/selectors/chat-bot.selectors';
import { LinkifyBeautifyPipe } from '../../helper/linkifyBeautify.pipe';

@Component({
  selector: 'app-chat-bot',
  imports: [CommonModule, FormsModule, LinkifyBeautifyPipe],
  standalone: true,
  templateUrl: './chat-bot.component.html',
  styleUrl: './chat-bot.component.scss'
})
export class ChatBotComponent {
  message = '';
  messages$;
  typing$;

  @ViewChild('scrollContainer') private scrollContainer!: ElementRef;

  constructor(private store: Store) {
    this.messages$ = this.store.select(selectChatMessages);
    this.typing$ = this.store.select(selectTypingStatus);
  }

  ngAfterViewInit() {
    this.messages$.subscribe(() => {
      setTimeout(() => this.scrollToBottom(), 100);
    });
  }


  sendMessage(): void {
    const trimmedMessage = this.message.trim();
    if (trimmedMessage) {
      this.store.dispatch(ChatActions.sendMessage({ request: { message: trimmedMessage } }));
      this.message = '';
    }
  }

  adjustHeight(event: Event): void {
    const textarea = event.target as HTMLTextAreaElement;
    textarea.style.height = 'auto';
    textarea.style.height = textarea.scrollHeight + 'px';
  }

  handleKeyDown(event: KeyboardEvent): void {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault(); // prevent newline
      this.sendMessage();     // your existing method
    }
  }

  private scrollToBottom(): void {
    try {
      this.scrollContainer.nativeElement.scroll({
        top: this.scrollContainer.nativeElement.scrollHeight,
        behavior: 'smooth'
      });
    } catch (err) {
      console.warn('Scroll error:', err);
    }
  }

}

