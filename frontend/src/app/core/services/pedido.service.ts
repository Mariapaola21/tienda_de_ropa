/**
 * PedidoService — Comunicación con los endpoints de pedidos de la API.
 *
 * Expone métodos para crear pedidos y consultar el historial del usuario.
 * Usa ApiService como capa de transporte HTTP.
 *
 * Interfaces exportadas:
 *   ItemPedidoPayload — Estructura de un ítem al crear un pedido.
 *   PedidoPayload     — Body completo para POST /pedidos.
 *   ItemPedidoOut     — Ítem de pedido tal como lo retorna la API.
 *   PedidoOut         — Pedido completo tal como lo retorna la API.
 */
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';

/** Ítem enviado al crear un pedido desde el carrito. */
export interface ItemPedidoPayload {
  producto_id: number;
  variante_id?: number;
  cantidad: number;
}

/** Payload completo para crear un pedido. */
export interface PedidoPayload {
  direccion_envio?: string;
  notas?: string;
  items: ItemPedidoPayload[];
}

/** Ítem de pedido tal como lo retorna la API (con precios calculados). */
export interface ItemPedidoOut {
  producto_id: number;
  variante_id?: number;
  cantidad: number;
  precio_unitario: number;
  subtotal: number;
}

/** Pedido completo retornado por la API. */
export interface PedidoOut {
  id: number;
  estado: string;
  total: number;
  fecha_pedido: string;
  items: ItemPedidoOut[];
}

@Injectable({ providedIn: 'root' })
export class PedidoService {
  private readonly api = inject(ApiService);

  /**
   * Crea un nuevo pedido en la API a partir del contenido del carrito.
   * @param payload Items del carrito con cantidades y variantes.
   */
  crearPedido(payload: PedidoPayload): Observable<PedidoOut> {
    return this.api.post<PedidoOut>('/pedidos', payload);
  }

  /** Retorna el historial de pedidos del usuario autenticado. */
  misPedidos(): Observable<PedidoOut[]> {
    return this.api.get<PedidoOut[]>('/pedidos/mis-pedidos');
  }
}
