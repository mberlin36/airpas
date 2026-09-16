import { Component, computed, effect, inject, signal } from '@angular/core';
import { MatTableDataSource } from '@angular/material/table';
import { Sort } from '@angular/material/sort';
import { MatSidenavModule } from '@angular/material/sidenav';
import { TasksStore } from '../tasks.store';
import { ReceiptModel } from '../../../shared/models/receipt.model';
import { PageHeader, Highlight } from '../../../shared/components/page-header/page-header';
import { TaskTable } from '../task-table/task-table';
import { Task } from '../task/task';

@Component({
  selector: 'app-task-list',
  imports: [PageHeader, TaskTable, MatSidenavModule, Task],
  templateUrl: './task-list.html',
  styleUrl: './task-list.scss',
})
export class TaskList {
  readonly store = inject(TasksStore);

  dataSource = new MatTableDataSource<ReceiptModel>();

  pageSizes = [15, 50, 100];
  displayColumns = ['position', 'vendorName', 'status', 'lineCount', 'totalValue', 'createdAt'];

  selectedReceiptId = signal<string | null>(null);

  highlights = computed<Highlight[]>(() => [
    {
      title: 'Receipts Awaiting Review',
      value: this.store.totalData(),
      level: 'info',
    },
  ]);

  constructor() {
    effect(() => {
      this.dataSource.data = this.store.tasks();
    });
    this.store.listTasks();
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
}
