import { computed, inject } from '@angular/core';
import { patchState, signalStore, withComputed, withMethods, withState } from '@ngrx/signals';
import type { PageEvent } from '@angular/material/paginator';
import type { Sort } from '@angular/material/sort';
import { Receipts } from '../../shared/services/receipts';
import { ReceiptModel } from '../../shared/models/receipt.model';
import { UsersStore } from '../../shared/stores/users.store';

type SubmissionsStatus = 'idle' | 'loading' | 'success' | 'error';

interface SubmissionsState {
  submissions: ReceiptModel[];
  totalData: number;
  limit: number;
  skip: number;
  pageIndex: number;
  sort: string;
  order: 'asc' | 'desc';
  status: SubmissionsStatus;
}

const initialState: SubmissionsState = {
  submissions: [],
  totalData: 0,
  limit: 15,
  skip: 0,
  pageIndex: 0,
  sort: 'created_at',
  order: 'desc',
  status: 'idle',
};

export const SubmissionsStore = signalStore(
  { providedIn: 'root' },
  withState(initialState),
  withComputed((store) => ({
    isLoading: computed(() => store.status() === 'loading'),
    isError: computed(() => store.status() === 'error'),
  })),
  withMethods((store, receiptsService = inject(Receipts), usersStore = inject(UsersStore)) => {
    const fetchSubmissions = async () => {
      const submitterId = usersStore.currentUser()?.id;
      if (!submitterId) {
        patchState(store, { submissions: [], totalData: 0, status: 'error' });
        return;
      }

      patchState(store, { status: 'loading' });
      try {
        const response = await receiptsService.list({
          limit: store.limit(),
          skip: store.skip(),
          sort: store.sort(),
          order: store.order(),
          submitter_id: submitterId,
        });
        patchState(store, {
          submissions: response.data.map((receipt) => new ReceiptModel(receipt)),
          totalData: response.count,
          status: 'success',
        });
      } catch {
        patchState(store, { submissions: [], totalData: 0, status: 'error' });
      }
    };

    return {
      listSubmissions: fetchSubmissions,
      loadPage: async (pageEvent: PageEvent) => {
        patchState(store, {
          pageIndex: pageEvent.pageIndex,
          limit: pageEvent.pageSize,
          skip: pageEvent.pageIndex * pageEvent.pageSize,
        });
        await fetchSubmissions();
      },
      sortChanged: async (sort: Sort) => {
        patchState(store, {
          sort: sort.active,
          order: (sort.direction || 'desc') as 'asc' | 'desc',
        });
        await fetchSubmissions();
      },
    };
  }),
);
