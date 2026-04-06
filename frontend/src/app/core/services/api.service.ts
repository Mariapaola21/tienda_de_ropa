/**
 * ApiService — Capa de abstracción sobre HttpClient.
 *
 * Centraliza todas las llamadas HTTP de la aplicación.
 * Todos los servicios de features (ProductoService, PedidoService, etc.)
 * usan este servicio en lugar de inyectar HttpClient directamente,
 * lo que facilita cambiar la URL base o agregar lógica global en un solo lugar.
 *
 * La URL base se lee de environment.apiUrl (configurada por entorno).
 */
import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

@Injectable({ providedIn: 'root' })
export class ApiService {
  private readonly http = inject(HttpClient);
  private readonly base = environment.apiUrl;

  /**
   * Realiza una petición GET.
   * @param path  Ruta relativa al base URL (ej: '/productos').
   * @param params Objeto de query params opcionales. Los valores undefined/null se omiten.
   */
  get<T>(path: string, params?: Record<string, string | number | boolean>): Observable<T> {
    let httpParams = new HttpParams();
    if (params) {
      Object.entries(params).forEach(([k, v]) => {
        if (v !== undefined && v !== null) httpParams = httpParams.set(k, String(v));
      });
    }
    return this.http.get<T>(`${this.base}${path}`, { params: httpParams });
  }

  /** Realiza una petición POST con body JSON. */
  post<T>(path: string, body: unknown): Observable<T> {
    return this.http.post<T>(`${this.base}${path}`, body);
  }

  /** Realiza una petición PUT con body JSON (reemplazo completo). */
  put<T>(path: string, body: unknown): Observable<T> {
    return this.http.put<T>(`${this.base}${path}`, body);
  }

  /** Realiza una petición PATCH con body JSON (actualización parcial). */
  patch<T>(path: string, body: unknown): Observable<T> {
    return this.http.patch<T>(`${this.base}${path}`, body);
  }

  /** Realiza una petición DELETE. */
  delete<T>(path: string): Observable<T> {
    return this.http.delete<T>(`${this.base}${path}`);
  }
}
