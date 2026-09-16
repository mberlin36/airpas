import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { firstValueFrom } from 'rxjs';

export interface ApiUser {
  id: string;
  first_name: string;
  last_name: string;
  email: string;
  is_admin: boolean;
  created_at: string;
  updated_at: string;
  deleted_at: string | null;
}

export interface UserListResponse {
  data: ApiUser[];
  count: number;
}

@Injectable({
  providedIn: 'root',
})
export class Users {
  private http = inject(HttpClient);
  private readonly baseUrl = '/api/users';

  list(
    params: { skip?: number; limit?: number; sort?: string; order?: string; is_admin?: boolean } = {},
  ): Promise<UserListResponse> {
    return firstValueFrom(this.http.get<UserListResponse>(`${this.baseUrl}/`, { params }));
  }

  getById(id: string): Promise<ApiUser> {
    return firstValueFrom(this.http.get<ApiUser>(`${this.baseUrl}/${id}`));
  }

  async getByEmail(email: string): Promise<ApiUser | undefined> {
    const response = await firstValueFrom(this.http.get<UserListResponse>(`${this.baseUrl}/`, { params: { email } }));
    return response.data[0];
  }
}

