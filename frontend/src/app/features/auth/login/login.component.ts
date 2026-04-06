import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../../../core/services/auth.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './login.component.html',
})
export class LoginComponent {
  private readonly auth = inject(AuthService);
  private readonly router = inject(Router);

  correo = '';
  password = '';
  error = signal<string | null>(null);
  cargando = signal(false);

  submit(): void {
    this.error.set(null);
    this.cargando.set(true);
    this.auth.login({ correo: this.correo, password: this.password }).subscribe({
      next: () => this.router.navigate(['/shop']),
      error: () => { this.error.set('Credenciales incorrectas'); this.cargando.set(false); },
    });
  }
}
