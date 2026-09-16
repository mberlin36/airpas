import { Component, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatDialogModule, MatDialogRef } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSelectModule } from '@angular/material/select';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { UsersStore } from '../../../shared/stores/users.store';
import { Receipts } from '../../../shared/services/receipts';

@Component({
  selector: 'app-submission-upload-dialog',
  imports: [
    ReactiveFormsModule,
    MatDialogModule,
    MatFormFieldModule,
    MatSelectModule,
    MatButtonModule,
    MatIconModule,
  ],
  templateUrl: './submission-upload-dialog.html',
  styleUrl: './submission-upload-dialog.scss',
})
export class SubmissionUploadDialog {
  private dialogRef = inject(MatDialogRef<SubmissionUploadDialog>);
  private fb = inject(FormBuilder);
  private usersStore = inject(UsersStore);
  private receiptsService = inject(Receipts);

  readonly admins = this.usersStore.admins;

  selectedFile = signal<File | null>(null);
  isSubmitting = signal(false);
  errorMessage = signal<string | null>(null);

  form = this.fb.group({
    reviewerId: ['', Validators.required],
  });

  constructor() {
    this.usersStore.loadAdmins();
  }

  onFileSelected(event: Event) {
    const input = event.target as HTMLInputElement;
    this.selectedFile.set(input.files?.[0] ?? null);
  }

  async submit() {
    const file = this.selectedFile();
    const reviewerId = this.form.value.reviewerId;
    const submitterId = this.usersStore.currentUser()?.id;

    if (!file || !reviewerId || !submitterId || this.form.invalid) {
      return;
    }

    this.isSubmitting.set(true);
    this.errorMessage.set(null);
    try {
      // vendor_name is required by the API but unknown until AI extraction processes the upload.
      const receipt = await this.receiptsService.create({
        vendor_name: 'Pending Review',
        submitter_id: submitterId,
        reviewer_id: reviewerId,
      });
      await this.receiptsService.uploadFile(receipt.id, file, submitterId);
      this.dialogRef.close(true);
    } catch {
      this.errorMessage.set('Could not submit receipt. Please try again.');
    } finally {
      this.isSubmitting.set(false);
    }
  }

  cancel() {
    this.dialogRef.close(false);
  }
}
