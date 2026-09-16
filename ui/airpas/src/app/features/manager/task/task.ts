import { Component, effect, inject, input, output, signal } from '@angular/core';
import { CurrencyPipe, DatePipe } from '@angular/common';
import { FormBuilder, ReactiveFormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { ApiReceipt, Receipts } from '../../../shared/services/receipts';

@Component({
  selector: 'app-task',
  imports: [MatButtonModule, MatIconModule, MatFormFieldModule, MatInputModule, ReactiveFormsModule, CurrencyPipe, DatePipe],
  templateUrl: './task.html',
  styleUrl: './task.scss',
})
export class Task {
  private receiptsService = inject(Receipts);
  private fb = inject(FormBuilder);

  id = input.required<string>();
  closeRequested = output<void>();
  taskUpdated = output<void>();

  receipt = signal<ApiReceipt | null>(null);
  isLoading = signal(false);
  isSaving = signal(false);
  errorMessage = signal<string | null>(null);

  reviewForm = this.fb.group({
    notes: [''],
  });

  constructor() {
    effect(() => {
      this.load(this.id());
    });
  }

  private async load(id: string) {
    this.isLoading.set(true);
    this.errorMessage.set(null);
    try {
      const receipt = await this.receiptsService.getById(id);
      this.receipt.set(receipt);
      this.reviewForm.patchValue({ notes: receipt.notes ?? '' });
    } finally {
      this.isLoading.set(false);
    }
  }

  /** Approve or reject the receipt, completing the manager's review. Rejecting requires review notes. */
  async decide(status: 'approved' | 'rejected') {
    const receipt = this.receipt();
    if (!receipt) {
      return;
    }

    const notes = this.reviewForm.value.notes?.trim() ?? '';
    if (status === 'rejected' && !notes) {
      this.errorMessage.set('Notes are required to reject a receipt.');
      return;
    }

    this.isSaving.set(true);
    this.errorMessage.set(null);
    try {
      await this.receiptsService.update(receipt.id, { status, notes });
      await this.load(receipt.id);
      this.taskUpdated.emit();
    } catch {
      this.errorMessage.set('Could not update the receipt. Please try again.');
    } finally {
      this.isSaving.set(false);
    }
  }

  close() {
    this.closeRequested.emit();
  }
}
