import { ProductoListItem, Variante } from './producto.model';

export interface ItemCarrito {
  producto: ProductoListItem;
  variante?: Variante;
  cantidad: number;
}

export interface EstadoCarrito {
  items: ItemCarrito[];
  total: number;
  cantidadItems: number;
}
