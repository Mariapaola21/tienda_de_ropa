import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { ProductoListItem } from '../../../core/models/producto.model';

@Component({
  selector: 'app-product-card',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './product-card.component.html',
})
export class ProductCardComponent {
  @Input({ required: true }) producto!: ProductoListItem;
  @Output() agregarCarrito = new EventEmitter<ProductoListItem>();

  get tieneOferta(): boolean {
    return !!this.producto.precio_oferta && this.producto.precio_oferta < this.producto.precio;
  }

  get descuento(): number {
    if (!this.tieneOferta) return 0;
    return Math.round((1 - this.producto.precio_oferta! / this.producto.precio) * 100);
  }
}
