import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ProductoService } from '../../../core/services/producto.service';
import { CarritoService } from '../../../core/services/carrito.service';
import { ProductoListItem, ProductoFiltros } from '../../../core/models/producto.model';
import { ProductCardComponent } from '../product-card/product-card.component';

@Component({
  selector: 'app-product-list',
  standalone: true,
  imports: [CommonModule, FormsModule, ProductCardComponent],
  templateUrl: './product-list.component.html',
})
export class ProductListComponent implements OnInit {
  private readonly productoService = inject(ProductoService);
  readonly carrito = inject(CarritoService);

  productos = signal<ProductoListItem[]>([]);
  cargando = signal(true);
  error = signal<string | null>(null);
  filtros: ProductoFiltros = { limit: 20, skip: 0 };
  marcaFiltro = '';
  categoriaFiltro = '';

  metodosPago = [
    { nombre: 'Visa', logo: 'https://logodownload.org/wp-content/uploads/2016/10/visa-logo.png' },
    { nombre: 'Mastercard', logo: 'https://brandemia.org/sites/default/files/sites/default/files/mastercard_pentagram_press-4.jpg' },
    { nombre: 'Amex', logo: 'https://tse3.mm.bing.net/th/id/OIP.IA_1lpSH6tyfzQU-8KqhAAHaCm?r=0&rs=1&pid=ImgDetMain&o=7&rm=3' },
    { nombre: 'Diners', logo: 'https://tse2.mm.bing.net/th/id/OIP.iUD20gtafeILdJXudWyinAHaEJ?r=0&w=500&h=280&rs=1&pid=ImgDetMain&o=7&rm=3' },
    { nombre: 'PSE', logo: 'https://tse1.mm.bing.net/th/id/OIP.3lPbh6dPUClu40P7IdLBKwAAAA?r=0&w=474&h=243&rs=1&pid=ImgDetMain&o=7&rm=3' },
    { nombre: 'PayPal', logo: 'https://logodownload.org/wp-content/uploads/2014/10/paypal-logo.png' },
  ];

  porQueElegirnos = [
    { titulo: 'Calidad Garantizada', descripcion: 'Todas nuestras prendas son de alta calidad y marcas reconocidas.', icono: 'M10 2a8 8 0 100 16 8 8 0 000-16zm-1.293 8.293a1 1 0 011.414 0l.707.707 3-3a1 1 0 011.414 1.414l-4 4a1 1 0 01-1.414 0l-1.5-1.5a1 1 0 011.414-1.414z' },
    { titulo: 'Envío Rápido', descripcion: 'Recibe tu pedido en tiempo récord directamente en tu puerta.', icono: 'M3 10a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3-4a1 1 0 011-1h8a1 1 0 110 2H7a1 1 0 01-1-1zm0 8a1 1 0 011-1h8a1 1 0 110 2H7a1 1 0 01-1-1z' },
    { titulo: 'Devoluciones Fáciles', descripcion: 'Si no quedas satisfecho, te hacemos la devolución sin complicaciones.', icono: 'M10 18a8 8 0 100-16 8 8 0 000 16zM6 10a4 4 0 118 0 4 4 0 01-8 0z' },
  ];

  ngOnInit(): void { this.cargarProductos(); }

  cargarProductos(): void {
    this.cargando.set(true);
    this.error.set(null);
    const params: ProductoFiltros = {
      ...this.filtros,
      ...(this.marcaFiltro && { marca: this.marcaFiltro }),
      ...(this.categoriaFiltro && { categoria: this.categoriaFiltro }),
    };
    this.productoService.getProductos(params).subscribe({
      next: (data) => { this.productos.set(data); this.cargando.set(false); },
      error: () => { this.error.set('No se pudieron cargar los productos.'); this.cargando.set(false); },
    });
  }

  aplicarFiltros(): void { this.filtros.skip = 0; this.cargarProductos(); }
  limpiarFiltros(): void { this.marcaFiltro = ''; this.categoriaFiltro = ''; this.cargarProductos(); }
  agregarAlCarrito(producto: ProductoListItem): void { this.carrito.agregar(producto, 1); }
}
