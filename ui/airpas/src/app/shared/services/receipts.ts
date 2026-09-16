import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { firstValueFrom } from 'rxjs';

export type ReceiptStatus = 'uploaded' | 'processing' | 'review' | 'submitted' | 'approved' | 'rejected';

export interface ApiReceiptLine {
  id: string;
  item: string;
  value: number;
  note: string | null;
  receipt_id: string;
}

export interface ApiReceiptFile {
  id: string;
  name: string;
  type: string;
  url: string;
  receipt_id: string;
  uploaded_by_id: string;
}

export interface ApiReceipt {
  id: string;
  vendor_name: string;
  notes: string | null;
  submitter_id: string;
  reviewer_id: string | null;
  total_amount: number;
  currency: string;
  tax: number;
  status: ReceiptStatus;
  created_at: string;
  updated_at: string;
  deleted_at: string | null;
  receipt_lines: ApiReceiptLine[];
  files: ApiReceiptFile[];
}

export interface ReceiptListResponse {
  data: ApiReceipt[];
  count: number;
}

export interface ReceiptListParams {
  skip?: number;
  limit?: number;
  sort?: string;
  order?: 'asc' | 'desc';
  submitter_id?: string;
  reviewer_id?: string;
  status?: ReceiptStatus;
}

export interface ReceiptCreateParams {
  vendor_name: string;
  notes?: string;
  submitter_id: string;
  reviewer_id: string;
}

export interface ReceiptUpdateParams {
  vendor_name?: string;
  notes?: string | null;
  reviewer_id?: string;
  total_amount?: number;
  currency?: string;
  tax?: number;
  status?: ReceiptStatus;
}

@Injectable({
  providedIn: 'root',
})
export class Receipts {
  private http = inject(HttpClient);
  private readonly baseUrl = '/api/receipts';

  list(params: ReceiptListParams = {}): Promise<ReceiptListResponse> {
    const httpParams: Record<string, string> = {};
    for (const [key, value] of Object.entries(params)) {
      if (value !== undefined && value !== null) {
        httpParams[key] = String(value);
      }
    }
    return firstValueFrom(this.http.get<ReceiptListResponse>(`${this.baseUrl}/`, { params: httpParams }));
  }

  getById(id: string): Promise<ApiReceipt> {
    return firstValueFrom(this.http.get<ApiReceipt>(`${this.baseUrl}/${id}`));
  }

  create(params: ReceiptCreateParams): Promise<ApiReceipt> {
    return firstValueFrom(this.http.post<ApiReceipt>(`${this.baseUrl}/`, params));
  }

  uploadFile(receiptId: string, file: File, uploadedById: string): Promise<ApiReceiptFile> {
    const formData = new FormData();
    formData.append('upload', file);
    formData.append('uploaded_by_id', uploadedById);
    return firstValueFrom(
      this.http.post<ApiReceiptFile>(`${this.baseUrl}/${receiptId}/files/upload`, formData),
    );
  }

  update(id: string, params: ReceiptUpdateParams): Promise<ApiReceipt> {
    return firstValueFrom(this.http.patch<ApiReceipt>(`${this.baseUrl}/${id}`, params));
  }

  /** Send an uploaded file through the (mock) AI extraction pipeline, moving the receipt to "review". */
  process(receiptId: string, fileId: string): Promise<ApiReceipt> {
    return firstValueFrom(
      this.http.post<ApiReceipt>(`${this.baseUrl}/${receiptId}/files/${fileId}/process`, {}),
    );
  }
}
