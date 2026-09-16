import { Routes } from '@angular/router';
import { SubmissionList } from './submission-list/submission-list';
import { Submission } from './submission/submission';

export const EMPLOYEE_ROUTES: Routes = [
  { path: '', pathMatch: 'full', component: SubmissionList },
  { path: 'submissions/:id', component: Submission },
];
