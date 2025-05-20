import { Component } from '@angular/core';
import { ChatBotComponent } from './chat-bot/chat-bot.component';

@Component({
  selector: 'app-root',
  imports: [ChatBotComponent],
  standalone: true,
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss'
})
export class AppComponent {
  title = 'chat-bot-app';
}
