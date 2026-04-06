export interface Categoria {
  id: number;
  nombre: string;
  slug: string;
  imagen_url?: string;
}

export interface Variante {
  id: number;
  talla: 'XS' | 'S' | 'M' | 'L' | 'XL' | 'XXL' | 'UNICA';
  color?: string;
  sku?: string;
  stock: number;
}

export interface Producto {
  id: number;
  nombre: string;
  descripcion?: string;
  precio: number;
  precio_oferta?: number;
  marca?: string;
  material?: string;
  genero?: string;
  imagen_url?: string;
  destacado: boolean;
  activo: boolean;
  categorias: Categoria[];
  variantes: Variante[];
}

export interface ProductoListItem {
  id: number;
  nombre: string;
  precio: number;
  precio_oferta?: number;
  marca?: string;
  imagen_url?: string;
  destacado: boolean;
}

export interface ProductoFiltros {
  categoria?: string;
  marca?: string;
  destacado?: boolean;
  skip?: number;
  limit?: number;
}
