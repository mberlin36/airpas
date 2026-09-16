import { ApiReceipt, ReceiptStatus } from '../services/receipts';

export class ReceiptModel {
  id: string;
  vendorName: string;
  notes: string | null;
  submitterId: string;
  reviewerId: string | null;
  status: ReceiptStatus;
  lineCount: number;
  totalValue: number;
  createdAt: Date;
  updatedAt: Date;

  constructor(data: ApiReceipt) {
    this.id = data.id;
    this.vendorName = data.vendor_name;
    this.notes = data.notes;
    this.submitterId = data.submitter_id;
    this.reviewerId = data.reviewer_id;
    this.status = data.status;
    this.lineCount = data.receipt_lines?.length ?? 0;
    this.totalValue = (data.receipt_lines ?? []).reduce((sum, line) => sum + Number(line.value), 0);
    this.createdAt = new Date(data.created_at);
    this.updatedAt = new Date(data.updated_at);
  }
}
