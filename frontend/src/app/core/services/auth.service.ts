import { Injectable, inject, signal } from '@angular/core';
import { Router } from '@angular/router';
import { tap } from 'rxjs/operators';
import { ApiService } from './api.service';

interface LoginPayload { correo: string; password: string; }
interface TokenResponse { access_token: string; token_type: string; }

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly api = inject(ApiService);
  private readonly router = inject(Router);

  readonly isLoggedIn = signal<boolean>(!!localStorage.getItem('token'));

  login(payload: LoginPayload) {
    return this.api.post<TokenResponse>('/auth/login', payload).pipe(
      tap((res) => {
        localStorage.setItem('token', res.access_token);
        this.isLoggedIn.set(true);
      })
    );
  }

  register(payload: unknown) {
    return this.api.post('/auth/register', payload);
  }

  logout(): void {
    localStorage.removeItem('token');
    this.isLoggedIn.set(false);
    this.router.navigate(['/']);
  }

  getToken(): string | null {
    return localStorage.getItem('token');
  }
}
