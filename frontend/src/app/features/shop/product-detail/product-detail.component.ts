import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { ProductoService } from '../../../core/services/producto.service';
import { CarritoService } from '../../../core/services/carrito.service';
import { Producto, Variante } from '../../../core/models/producto.model';

@Component({
  selector: 'app-product-detail',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './product-detail.component.html',
})
export class ProductDetailComponent implements OnInit {
  private readonly route = inject(ActivatedRoute);
  private readonly productoService = inject(ProductoService);
  readonly carrito = inject(CarritoService);

  producto = signal<Producto | null>(null);
  cargando = signal(true);
  varianteSeleccionada = signal<Variante | null>(null);
  agregado = signal(false);

  ngOnInit(): void {
    const id = Number(this.route.snapshot.paramMap.get('id'));
    this.productoService.getProducto(id).subscribe({
      next: (p) => { this.producto.set(p); this.cargando.set(false); },
      error: () => this.cargando.set(false),
    });
  }

  seleccionarVariante(v: Variante): void {
    this.varianteSeleccionada.set(v);
  }

  agregar(): void {
    const p = this.producto();
    if (!p) return;
    this.carrito.agregar(
      { id: p.id, nombre: p.nombre, precio: p.precio, precio_oferta: p.precio_oferta, marca: p.marca, imagen_url: p.imagen_url, destacado: p.destacado },
      1,
      this.varianteSeleccionada() ?? undefined
    );
    this.agregado.set(true);
    setTimeout(() => this.agregado.set(false), 2000);
  }
}
