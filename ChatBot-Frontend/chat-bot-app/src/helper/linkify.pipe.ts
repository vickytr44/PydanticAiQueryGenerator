import { Pipe, PipeTransform } from '@angular/core';

@Pipe({ name: 'linkify' })
export class LinkifyPipe implements PipeTransform {
  transform(text: string): string {
    if (!text) return text;

    const urlRegex = /((https?:\/\/)[^\s]+)/g;
    return text.replace(urlRegex, (url) => {
      const hyperlink = `<a href="${url}" target="_blank" rel="noopener noreferrer">${url}</a>`;
      return hyperlink;
    });
  }
}
