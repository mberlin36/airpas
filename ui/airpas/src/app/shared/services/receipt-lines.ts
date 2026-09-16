import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { firstValueFrom } from 'rxjs';
import { ApiReceiptLine } from './receipts';

export interface ReceiptLineUpsertParams {
  item: string;
  value: number;
  note?: string | null;
}

@Injectable({
  providedIn: 'root',
})
export class ReceiptLines {
  private http = inject(HttpClient);

  private linesUrl(receiptId: string) {
    return `/api/receipts/${receiptId}/lines`;
  }

  create(receiptId: string, params: ReceiptLineUpsertParams): Promise<ApiReceiptLine> {
    return firstValueFrom(this.http.post<ApiReceiptLine>(`${this.linesUrl(receiptId)}/`, params));
  }

  update(receiptId: string, lineId: string, params: Partial<ReceiptLineUpsertParams>): Promise<ApiReceiptLine> {
    return firstValueFrom(this.http.patch<ApiReceiptLine>(`${this.linesUrl(receiptId)}/${lineId}`, params));
  }

  delete(receiptId: string, lineId: string): Promise<void> {
    return firstValueFrom(this.http.delete<void>(`${this.linesUrl(receiptId)}/${lineId}`));
  }
}
