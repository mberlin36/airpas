import { Component, inject } from '@angular/core';
import { MatError, MatFormField, MatLabel, MatPrefix } from '@angular/material/form-field';
import { MatIcon } from '@angular/material/icon';
import { MatInput } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { FormBuilder, ReactiveFormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { UsersStore } from '../../shared/stores/users.store';

@Component({
  selector: 'app-login',
  imports: [
    MatFormField,
    MatIcon,
    MatInput,
    MatLabel,
    MatPrefix,
    ReactiveFormsModule,
    MatButtonModule,
    MatError,],
  templateUrl: './login.html',
  styleUrl: './login.scss',
})
export class Login {

  public usersStore = inject(UsersStore);
  private fb = inject(FormBuilder);
  private router = inject(Router);
  loginForm = this.fb.group({
    username: [''],
  });

  async logIn() {
    if (this.loginForm.valid) {
      const { username } = this.loginForm.value;
      if (!username) {
        return;
      }

      await this.usersStore.getUser(username);

      const route = this.usersStore.getRouteForCurrentUser();
      if (route) {
        await this.router.navigateByUrl(route);
      }
    }
  }
}
