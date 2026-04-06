import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../../../core/services/auth.service';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './register.component.html',
})
export class RegisterComponent {
  private readonly auth = inject(AuthService);
  private readonly router = inject(Router);

  form = { nombre: '', apellido: '', documento: '', correo: '', password: '' };
  error = signal<string | null>(null);
  cargando = signal(false);

  submit(): void {
    this.error.set(null);
    this.cargando.set(true);
    this.auth.register(this.form).subscribe({
      next: () => this.router.navigate(['/auth/login']),
      error: () => { this.error.set('Error al registrar. Verifica los datos.'); this.cargando.set(false); },
    });
  }
}
