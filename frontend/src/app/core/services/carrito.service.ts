/**
 * CarritoService — Estado reactivo del carrito de compras.
 *
 * Maneja el carrito completamente en el frontend usando Angular Signals.
 * El estado se persiste en localStorage para sobrevivir recargas de página.
 *
 * Señales expuestas:
 *   items         — Lista de ítems en el carrito (readonly).
 *   total         — Suma de (precio * cantidad) para todos los ítems.
 *   cantidadItems — Total de unidades en el carrito.
 *   estado        — Snapshot completo del carrito (items + total + cantidad).
 *
 * Cada cambio llama a persistir() para sincronizar con localStorage.
 */
import { Injectable, signal, computed } from '@angular/core';
import { ItemCarrito, EstadoCarrito } from '../models/carrito.model';
import { ProductoListItem, Variante } from '../models/producto.model';

/** Clave usada para guardar el carrito en localStorage. */
const STORAGE_KEY = 'tienda_carrito';

@Injectable({ providedIn: 'root' })
export class CarritoService {
  /** Estado interno mutable — solo se modifica a través de los métodos del servicio. */
  private readonly _items = signal<ItemCarrito[]>(this.cargarDesdeStorage());

  /** Vista pública de los ítems (solo lectura). */
  readonly items = this._items.asReadonly();

  /** Total calculado reactivamente. Usa precio_oferta si está disponible. */
  readonly total = computed(() =>
    this._items().reduce((acc, item) => {
      const precio = item.producto.precio_oferta ?? item.producto.precio;
      return acc + precio * item.cantidad;
    }, 0)
  );

  /** Número total de unidades en el carrito (suma de cantidades). */
  readonly cantidadItems = computed(() =>
    this._items().reduce((acc, item) => acc + item.cantidad, 0)
  );

  /** Snapshot completo del estado del carrito. */
  readonly estado = computed<EstadoCarrito>(() => ({
    items: this._items(),
    total: this.total(),
    cantidadItems: this.cantidadItems(),
  }));

  /**
   * Agrega un producto al carrito.
   * Si ya existe el mismo producto+variante, incrementa la cantidad.
   * Si es nuevo, lo agrega como ítem nuevo.
   *
   * @param producto  Producto a agregar.
   * @param cantidad  Unidades a agregar (default: 1).
   * @param variante  Variante de talla/color (opcional).
   */
  agregar(producto: ProductoListItem, cantidad: number = 1, variante?: Variante): void {
    const items = [...this._items()];
    const idx = items.findIndex(
      (i) => i.producto.id === producto.id && i.variante?.id === variante?.id
    );

    if (idx >= 0) {
      // Producto ya existe — incrementar cantidad
      items[idx] = { ...items[idx], cantidad: items[idx].cantidad + cantidad };
    } else {
      // Producto nuevo — agregar al carrito
      items.push({ producto, variante, cantidad });
    }

    this._items.set(items);
    this.persistir();
  }

  /**
   * Actualiza la cantidad de un ítem específico.
   * Si la cantidad es 0 o menor, elimina el ítem del carrito.
   *
   * @param productoId  ID del producto.
   * @param varianteId  ID de la variante (undefined si no tiene variante).
   * @param cantidad    Nueva cantidad.
   */
  actualizar(productoId: number, varianteId: number | undefined, cantidad: number): void {
    if (cantidad <= 0) {
      this.eliminar(productoId, varianteId);
      return;
    }
    this._items.update((items) =>
      items.map((i) =>
        i.producto.id === productoId && i.variante?.id === varianteId
          ? { ...i, cantidad }
          : i
      )
    );
    this.persistir();
  }

  /**
   * Elimina un ítem del carrito por productoId y varianteId.
   *
   * @param productoId  ID del producto a eliminar.
   * @param varianteId  ID de la variante (null/undefined si no tiene variante).
   */
  eliminar(productoId: number, varianteId: number | undefined | null): void {
    this._items.update((items) =>
      items.filter(
        (i) => !(i.producto.id === productoId && i.variante?.id == varianteId)
      )
    );
    this.persistir();
  }

  /**
   * Elimina un ítem del carrito por referencia directa al objeto.
   * Útil cuando se tiene la referencia del ítem pero no sus IDs por separado.
   */
  removerItem(itemARemover: ItemCarrito): void {
    this._items.update(items => items.filter(i => i !== itemARemover));
    this.persistir();
  }

  /** Vacía completamente el carrito y elimina la persistencia en localStorage. */
  vaciar(): void {
    this._items.set([]);
    localStorage.removeItem(STORAGE_KEY);
  }

  /** Serializa el estado actual del carrito en localStorage. */
  private persistir(): void {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(this._items()));
  }

  /**
   * Carga el carrito desde localStorage al inicializar el servicio.
   * Retorna un array vacío si no hay datos o si el JSON está corrupto.
   */
  private cargarDesdeStorage(): ItemCarrito[] {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      return raw ? JSON.parse(raw) : [];
    } catch {
      return [];
    }
  }
}
