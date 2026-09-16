import { Routes } from '@angular/router';
import { TaskList } from './task-list/task-list';
import { Task } from './task/task';

export const MANAGER_ROUTES: Routes = [
  { path: '', pathMatch: 'full', component: TaskList },
  { path: 'tasks/:id', component: Task },
];
