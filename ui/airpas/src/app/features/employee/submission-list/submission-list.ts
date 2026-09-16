import { Component, computed, effect, inject, signal } from '@angular/core';
import { MatTableDataSource } from '@angular/material/table';
import { Sort } from '@angular/material/sort';
import { MatDialog } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatSidenavModule } from '@angular/material/sidenav';
import { SubmissionsStore } from '../submissions.store';
import { ReceiptModel } from '../../../shared/models/receipt.model';
import { PageHeader, Highlight } from '../../../shared/components/page-header/page-header';
import { SubmissionTable } from '../submission-table/submission-table';
import { SubmissionUploadDialog } from '../submission-upload-dialog/submission-upload-dialog';
import { Submission } from '../submission/submission';

@Component({
  selector: 'app-submission-list',
  imports: [PageHeader, SubmissionTable, MatButtonModule, MatIconModule, MatSidenavModule, Submission],
  templateUrl: './submission-list.html',
  styleUrl: './submission-list.scss',
})
export class SubmissionList {
  readonly store = inject(SubmissionsStore);
  private dialog = inject(MatDialog);

  dataSource = new MatTableDataSource<ReceiptModel>();

  pageSizes = [15, 50, 100];
  displayColumns = ['position', 'vendorName', 'status', 'lineCount', 'totalValue', 'createdAt'];

  selectedReceiptId = signal<string | null>(null);

  highlights = computed<Highlight[]>(() => [
    {
      title: 'Total Submissions',
      value: this.store.totalData(),
      level: 'info',
    },
  ]);

  constructor() {
    effect(() => {
      this.dataSource.data = this.store.submissions();
    });
    this.store.listSubmissions();
  }

  rowClick(row: ReceiptModel) {
    this.selectedReceiptId.set(row.id);
  }

  closeDetail() {
    this.selectedReceiptId.set(null);
  }

  sortChanged(event: Sort) {
    this.store.sortChanged(event);
  }

  openUploadDialog() {
    const dialogRef = this.dialog.open(SubmissionUploadDialog);
    dialogRef.afterClosed().subscribe((didSubmit) => {
      if (didSubmit) {
        this.store.listSubmissions();
      }
    });
  }
}
