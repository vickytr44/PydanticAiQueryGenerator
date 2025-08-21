import { Pipe, PipeTransform } from '@angular/core';
import { marked } from 'marked';
import DOMPurify from 'dompurify';

@Pipe({ name: 'linkifyBeautify' })
export class LinkifyBeautifyPipe implements PipeTransform {
  transform(text: string): string {
    if (!text) return text;

    let parsedText: string;
    try {
      parsedText = JSON.parse(text);
      if (typeof parsedText !== 'string') {
        parsedText = JSON.stringify(parsedText, null, 2);
      }
    } catch {
      parsedText = text;
    }

    // Use marked to parse markdown to HTML
    let html = '';
    // marked may return a Promise in some configurations, so handle both cases
    const result = marked(parsedText, { breaks: true });
    if (typeof result === 'string') {
      html = result;
    } else if (result && typeof result.then === 'function') {
      // If marked returns a Promise, this pipe should not handle async, so fallback to raw text
      html = parsedText;
    }
    html = DOMPurify.sanitize(html);
    return html;
  }
}
