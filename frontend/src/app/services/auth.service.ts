import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, map } from 'rxjs';

interface TokenResponse {
  access_token: string;
  token_type?: string;
}

@Injectable({ providedIn: 'root' })
export class AuthService {
  private base = '/api/v1/auth';

  constructor(private http: HttpClient) {}

  login(payload: { email: string; password: string }): Observable<TokenResponse> {
    return this.http.post<TokenResponse>(`${this.base}/login`, payload).pipe(
      map((res) => {
        if (res?.access_token) {
          localStorage.setItem('access_token', res.access_token);
        }
        return res;
      })
    );
  }

  register(payload: { email: string; password: string; full_name?: string }): Observable<any> {
    return this.http.post<any>(`${this.base}/register`, payload);
  }

  logout() {
    localStorage.removeItem('access_token');
  }

  getToken(): string | null {
    return localStorage.getItem('access_token');
  }
}
