import { Component, input } from '@angular/core';
import { MatCardModule } from '@angular/material/card';
import { MatDividerModule } from '@angular/material/divider';

export interface Highlight {
  title: string;
  value: number | string;
  level?: 'info' | 'warning' | 'error';
}

@Component({
  selector: 'app-page-header',
  imports: [MatCardModule, MatDividerModule],
  templateUrl: './page-header.html',
  styleUrl: './page-header.scss',
})
export class PageHeader {
  title = input.required<string>();
  highlights = input<Highlight[]>();
}
