import { Component, input, output } from '@angular/core';
import { MatPaginator, PageEvent } from '@angular/material/paginator';
import { MatSortModule, Sort } from '@angular/material/sort';
import { MatTableDataSource, MatTableModule } from '@angular/material/table';
import { CurrencyPipe, DatePipe } from '@angular/common';
import { ReceiptModel } from '../../../shared/models/receipt.model';

@Component({
  selector: 'app-submission-table',
  imports: [MatTableModule, MatPaginator, MatSortModule, CurrencyPipe, DatePipe],
  templateUrl: './submission-table.html',
  styleUrl: './submission-table.scss',
})
export class SubmissionTable {
  dataSource = input.required<MatTableDataSource<ReceiptModel>>();
  displayedColumns = input.required<string[]>();
  length = input.required<number>();
  pageSizes = input.required<number[]>();
  pageSize = input.required<number>();
  pageIndex = input.required<number>();

  pageChanged = output<PageEvent>();
  rowClicked = output<ReceiptModel>();
  sortChanged = output<Sort>();

  sortChange(event: Sort) {
    this.sortChanged.emit(event);
  }

  rowClick(element: ReceiptModel) {
    if (element) {
      this.rowClicked.emit(element);
    }
  }

  pageChange(event: PageEvent) {
    this.pageChanged.emit(event);
  }
}

