/**
 * authInterceptor — Interceptor HTTP funcional para autenticación JWT.
 *
 * Se ejecuta automáticamente en cada petición HTTP saliente.
 * Lee el token JWT de localStorage y lo adjunta en el header Authorization
 * con el esquema Bearer, requerido por la API de FastAPI.
 *
 * Lee directamente de localStorage (en lugar de inyectar AuthService)
 * para evitar dependencias circulares, ya que AuthService también usa ApiService.
 *
 * Registrado en app.config.ts junto con errorInterceptor.
 */
import { HttpInterceptorFn } from '@angular/common/http';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const token = localStorage.getItem('token');

  if (token) {
    // Clona la request y agrega el header — las requests HTTP son inmutables
    req = req.clone({ setHeaders: { Authorization: `Bearer ${token}` } });
  }

  return next(req);
};
