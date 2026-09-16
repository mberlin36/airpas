import { computed, inject } from '@angular/core';
import { patchState, signalStore, withComputed, withMethods, withState } from '@ngrx/signals';
import type { PageEvent } from '@angular/material/paginator';
import type { Sort } from '@angular/material/sort';
import { Receipts } from '../../shared/services/receipts';
import { ReceiptModel } from '../../shared/models/receipt.model';
import { UsersStore } from '../../shared/stores/users.store';

type TasksStatus = 'idle' | 'loading' | 'success' | 'error';

interface TasksState {
  tasks: ReceiptModel[];
  totalData: number;
  limit: number;
  skip: number;
  pageIndex: number;
  sort: string;
  order: 'asc' | 'desc';
  status: TasksStatus;
}

const initialState: TasksState = {
  tasks: [],
  totalData: 0,
  limit: 15,
  skip: 0,
  pageIndex: 0,
  sort: 'created_at',
  order: 'desc',
  status: 'idle',
};

export const TasksStore = signalStore(
  { providedIn: 'root' },
  withState(initialState),
  withComputed((store) => ({
    isLoading: computed(() => store.status() === 'loading'),
    isError: computed(() => store.status() === 'error'),
  })),
  withMethods((store, receiptsService = inject(Receipts), usersStore = inject(UsersStore)) => {
    const fetchTasks = async () => {
      const reviewerId = usersStore.currentUser()?.id;
      if (!reviewerId) {
        patchState(store, { tasks: [], totalData: 0, status: 'error' });
        return;
      }

      patchState(store, { status: 'loading' });
      try {
        const response = await receiptsService.list({
          limit: store.limit(),
          skip: store.skip(),
          sort: store.sort(),
          order: store.order(),
          // A manager's tasks are receipts assigned to them that the employee has submitted for review.
          reviewer_id: reviewerId,
          status: 'submitted',
        });
        patchState(store, {
          tasks: response.data.map((receipt) => new ReceiptModel(receipt)),
          totalData: response.count,
          status: 'success',
        });
      } catch {
        patchState(store, { tasks: [], totalData: 0, status: 'error' });
      }
    };

    return {
      listTasks: fetchTasks,
      loadPage: async (pageEvent: PageEvent) => {
        patchState(store, {
          pageIndex: pageEvent.pageIndex,
          limit: pageEvent.pageSize,
          skip: pageEvent.pageIndex * pageEvent.pageSize,
        });
        await fetchTasks();
      },
      sortChanged: async (sort: Sort) => {
        patchState(store, {
          sort: sort.active,
          order: (sort.direction || 'desc') as 'asc' | 'desc',
        });
        await fetchTasks();
      },
    };
  }),
);
