import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';
import { Producto, ProductoListItem, ProductoFiltros } from '../models/producto.model';

@Injectable({ providedIn: 'root' })
export class ProductoService {
  private readonly api = inject(ApiService);

  getProductos(filtros?: ProductoFiltros): Observable<ProductoListItem[]> {
    return this.api.get<ProductoListItem[]>('/productos', filtros as Record<string, string | number | boolean>);
  }

  getProducto(id: number): Observable<Producto> {
    return this.api.get<Producto>(`/productos/${id}`);
  }

  crearProducto(data: Partial<Producto>): Observable<Producto> {
    return this.api.post<Producto>('/productos', data);
  }

  actualizarProducto(id: number, data: Partial<Producto>): Observable<Producto> {
    return this.api.put<Producto>(`/productos/${id}`, data);
  }

  eliminarProducto(id: number): Observable<void> {
    return this.api.delete<void>(`/productos/${id}`);
  }
}
