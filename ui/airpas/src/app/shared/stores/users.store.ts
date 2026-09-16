import { patchState, signalStore, withComputed, withMethods, withState } from '@ngrx/signals';
import { computed, inject } from '@angular/core';
import { ApiUser, Users } from '../services/users';

const SESSION_STORAGE_KEY = 'airpas_current_user_email';

interface UsersState {
  currentUser: ApiUser | null;
  authStatus: 'idle' | 'loading' | 'authenticated' | 'error';
  admins: ApiUser[];
}

const initialState: UsersState = {
  currentUser: null,
  authStatus: 'idle',
  admins: [],
};

export const UsersStore = signalStore(
  { providedIn: 'root' },
  withState(initialState),
  withComputed((store) => ({
    isLoading: computed(() => store.authStatus() === 'loading'),
    isAuthenticated: computed(() => store.authStatus() === 'authenticated'),
    isError: computed(() => store.authStatus() === 'error'),
  })),
  withMethods((store, usersService = inject(Users)) => ({
    /** Look up a user by email and set them as the current user; used by the login page. */
    getUser: async (email: string) => {
      patchState(store, { authStatus: 'loading' });

      try {
        const user = await usersService.getByEmail(email);
        if (!user) {
          patchState(store, { currentUser: null, authStatus: 'error' });
          return;
        }

        localStorage.setItem(SESSION_STORAGE_KEY, email);
        patchState(store, { currentUser: user, authStatus: 'authenticated' });
      } catch {
        patchState(store, { currentUser: null, authStatus: 'error' });
      }
    },
    /** Restore the session from a prior login after a full page reload; a no-op if none was saved. */
    restoreSession: async () => {
      const savedEmail = localStorage.getItem(SESSION_STORAGE_KEY);
      if (!savedEmail) {
        return;
      }

      patchState(store, { authStatus: 'loading' });
      try {
        const user = await usersService.getByEmail(savedEmail);
        if (!user) {
          localStorage.removeItem(SESSION_STORAGE_KEY);
          patchState(store, { currentUser: null, authStatus: 'idle' });
          return;
        }
        patchState(store, { currentUser: user, authStatus: 'authenticated' });
      } catch {
        patchState(store, { currentUser: null, authStatus: 'idle' });
      }
    },
    /** Route for the current user based on role: manager for admins, employee otherwise. */
    getRouteForCurrentUser: (): string | null => {
      const currentUser = store.currentUser();
      if (!currentUser) {
        return null;
      }
      return currentUser.is_admin ? '/manager' : '/employee';
    },
    /** Load all admin users; used to populate a reviewer picker dropdown. */
    loadAdmins: async () => {
      try {
        const response = await usersService.list({ is_admin: true, limit: 200 });
        patchState(store, { admins: response.data });
      } catch {
        patchState(store, { admins: [] });
      }
    },
    logout: () => {
      localStorage.removeItem(SESSION_STORAGE_KEY);
      patchState(store, { currentUser: null, authStatus: 'idle' });
    },
  })),
);

