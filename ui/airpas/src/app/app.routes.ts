import { Routes } from '@angular/router';
import { Login } from './features/login/login';
import { authGuard } from './shared/guards/auth.guard';

export const routes: Routes = [
  { path: '', pathMatch: 'full', redirectTo: 'login' },
  { path: 'login', component: Login },
  {
    path: 'manager',
    canActivate: [authGuard],
    loadChildren: () => import('./features/manager/manager.routes').then((m) => m.MANAGER_ROUTES),
  },
  {
    path: 'employee',
    canActivate: [authGuard],
    loadChildren: () => import('./features/employee/employee.routes').then((m) => m.EMPLOYEE_ROUTES),
  },
  { path: '**', redirectTo: 'login' },
];
