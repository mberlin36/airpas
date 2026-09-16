import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { UsersStore } from '../stores/users.store';

/** Redirect to login if there is no authenticated user (e.g. after a page refresh with no saved session). */
export const authGuard: CanActivateFn = () => {
  const usersStore = inject(UsersStore);
  const router = inject(Router);

  if (usersStore.isAuthenticated()) {
    return true;
  }

  return router.parseUrl('/login');
};
