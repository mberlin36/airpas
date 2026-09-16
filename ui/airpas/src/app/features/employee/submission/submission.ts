import { Component, effect, inject, input, output, signal } from '@angular/core';
import { CurrencyPipe, DatePipe } from '@angular/common';
import { FormArray, FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { ApiReceipt, Receipts } from '../../../shared/services/receipts';
import { ReceiptLines } from '../../../shared/services/receipt-lines';

@Component({
  selector: 'app-submission',
  imports: [
    MatButtonModule,
    MatIconModule,
    MatFormFieldModule,
    MatInputModule,
    ReactiveFormsModule,
    CurrencyPipe,
    DatePipe,
  ],
  templateUrl: './submission.html',
  styleUrl: './submission.scss',
})
export class Submission {
  private receiptsService = inject(Receipts);
  private receiptLinesService = inject(ReceiptLines);
  private fb = inject(FormBuilder);

  id = input.required<string>();
  closeRequested = output<void>();
  submissionUpdated = output<void>();

  receipt = signal<ApiReceipt | null>(null);
  isLoading = signal(false);
  isProcessing = signal(false);
  isSaving = signal(false);
  errorMessage = signal<string | null>(null);

  form = this.fb.group({
    vendorName: ['', Validators.required],
    lines: this.fb.array<ReturnType<typeof this.buildLineGroup>>([]),
  });

  get lines() {
    return this.form.controls.lines;
  }

  constructor() {
    effect(() => {
      this.load(this.id());
    });
  }

  private buildLineGroup(line?: { id?: string; item: string; value: number; note: string | null }) {
    return this.fb.group({
      id: [line?.id ?? null],
      item: [line?.item ?? '', Validators.required],
      value: [line?.value ?? 0, [Validators.required, Validators.min(0)]],
      note: [line?.note ?? ''],
    });
  }

  private async load(id: string) {
    this.isLoading.set(true);
    this.errorMessage.set(null);
    try {
      const receipt = await this.receiptsService.getById(id);
      this.receipt.set(receipt);
      this.form.setControl(
        'lines',
        this.fb.array(receipt.receipt_lines.map((line) => this.buildLineGroup(line))),
      );
      this.form.patchValue({ vendorName: receipt.vendor_name });
    } finally {
      this.isLoading.set(false);
    }
  }

  addLine() {
    this.lines.push(this.buildLineGroup());
  }

  removeLine(index: number) {
    this.lines.removeAt(index);
  }

  /** Kick off the mock AI extraction pipeline for the receipt's uploaded file. */
  async processReceipt() {
    const receipt = this.receipt();
    const fileId = receipt?.files[0]?.id;
    if (!receipt || !fileId) {
      this.errorMessage.set('No uploaded file found to process.');
      return;
    }

    this.isProcessing.set(true);
    this.errorMessage.set(null);
    try {
      await this.receiptsService.process(receipt.id, fileId);
      await this.load(receipt.id);
      this.submissionUpdated.emit();
    } catch {
      this.errorMessage.set('Could not process the receipt. Please try again.');
    } finally {
      this.isProcessing.set(false);
    }
  }

  /** Persist any edits to the vendor field and line items (notes is reserved for manager review). */
  async saveChanges(): Promise<boolean> {
    const receipt = this.receipt();
    if (!receipt || this.form.invalid) {
      return false;
    }

    this.isSaving.set(true);
    this.errorMessage.set(null);
    try {
      const { vendorName } = this.form.getRawValue();
      await this.receiptsService.update(receipt.id, { vendor_name: vendorName ?? '' });

      const originalLineIds = new Set(receipt.receipt_lines.map((line) => line.id));
      const currentLineIds = new Set<string>();

      for (const lineGroup of this.lines.controls) {
        const { id: lineId, item, value, note } = lineGroup.getRawValue();
        if (lineId) {
          currentLineIds.add(lineId);
          await this.receiptLinesService.update(receipt.id, lineId, { item: item ?? '', value: value ?? 0, note });
        } else {
          await this.receiptLinesService.create(receipt.id, { item: item ?? '', value: value ?? 0, note });
        }
      }

      for (const removedId of originalLineIds) {
        if (!currentLineIds.has(removedId)) {
          await this.receiptLinesService.delete(receipt.id, removedId);
        }
      }

      await this.load(receipt.id);
      this.submissionUpdated.emit();
      return true;
    } catch {
      this.errorMessage.set('Could not save changes. Please try again.');
      return false;
    } finally {
      this.isSaving.set(false);
    }
  }

  /** Save any pending edits, then submit the receipt for manager review. */
  async submitForReview() {
    const receipt = this.receipt();
    if (!receipt) {
      return;
    }

    const saved = await this.saveChanges();
    if (!saved) {
      return;
    }

    this.isSaving.set(true);
    this.errorMessage.set(null);
    try {
      await this.receiptsService.update(receipt.id, { status: 'submitted' });
      await this.load(receipt.id);
      this.submissionUpdated.emit();
    } catch {
      this.errorMessage.set('Could not submit for review. Please try again.');
    } finally {
      this.isSaving.set(false);
    }
  }

  close() {
    this.closeRequested.emit();
  }
}
