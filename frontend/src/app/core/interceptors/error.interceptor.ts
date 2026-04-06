/**
 * errorInterceptor — Interceptor HTTP funcional para manejo global de errores.
 *
 * Captura todos los errores HTTP de la aplicación en un solo lugar,
 * evitando que cada componente tenga que manejar casos como 401 o 403.
 *
 * Comportamiento por código de estado:
 *   401 — Token inválido o expirado: limpia el token y redirige al login.
 *   403 — Sin permisos: redirige al catálogo principal.
 *   0   — Error de red (servidor caído o sin conexión): loguea el error.
 *   Otros — Loguea el error con código y mensaje para debugging.
 *
 * Después de manejar el error, lo re-lanza con throwError para que
 * los componentes puedan reaccionar si necesitan lógica adicional.
 *
 * Registrado en app.config.ts junto con authInterceptor.
 */
import { HttpInterceptorFn, HttpErrorResponse } from '@angular/common/http';
import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { catchError, throwError } from 'rxjs';

export const errorInterceptor: HttpInterceptorFn = (req, next) => {
  const router = inject(Router);

  return next(req).pipe(
    catchError((error: HttpErrorResponse) => {
      switch (error.status) {
        case 401:
          // Token expirado o inválido — limpiar sesión y redirigir al login
          localStorage.removeItem('token');
          router.navigate(['/auth/login']);
          break;
        case 403:
          // Sin permisos — redirigir al catálogo
          router.navigate(['/shop']);
          break;
        case 0:
          // Error de red — el servidor no responde
          console.error('Error de red: no se pudo conectar al servidor');
          break;
        default:
          console.error(`Error ${error.status}: ${error.message}`);
      }
      // Re-lanza el error para que los componentes puedan manejarlo si lo necesitan
      return throwError(() => error);
    })
  );
};
