import { Pipe, PipeTransform } from '@angular/core';

@Pipe({ name: 'linkifyBeautify' })
export class LinkifyBeautifyPipe implements PipeTransform {
  transform(text: string): string {
    if (!text) return text;

    let parsedText: string;

    try {
      parsedText = JSON.parse(text); // handle escaped characters
    } catch {
      parsedText = text;
    }

    parsedText = parsedText.replace(/```(\w+)?\n([\s\S]*?)```/g, (_match, lang, code) => {
      const cleanCode = code.replace(/</g, '&lt;').replace(/>/g, '&gt;'); // escape HTML
      return `<pre><code class="language-${lang || 'plaintext'}">${cleanCode}</code></pre>`;
    });

    const urlRegex = /((https?:\/\/)[^\s]+)/g;
    parsedText = parsedText.replace(urlRegex, (url) => {
      let actualUrl = url;
      let suffix = '';

      const punctuationMatch = url.match(/[\)\.\,\!\?]+$/);
      if (punctuationMatch) {
        suffix = punctuationMatch[0];
        actualUrl = url.slice(0, -suffix.length);
      }

      return `<a href="${actualUrl}" target="_blank" rel="noopener noreferrer">${actualUrl}</a>${suffix}`;
    });

    parsedText = parsedText.replace(/\n/g, '<br>');

    return parsedText;
  }
}
