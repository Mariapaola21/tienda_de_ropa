import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { CarritoService } from '../../../core/services/carrito.service';

@Component({
  selector: 'app-editorial',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './editorial.component.html'
})
export class EditorialComponent {
  carrito = inject(CarritoService);
  mensajeExito = signal<string | null>(null);

  looks = [
    {
      id: 1,
      title: 'The Autumn Almanac',
      description: 'A study in layered organic textures and sharp silhouettes.',
      imageUrl: 'https://images.unsplash.com/photo-1544441893-675973e31985?q=80&w=1000&auto=format&fit=crop',
      pieces: [
        { id: 901, nombre: 'Oversized Camel Coat', precio: 1200 },
        { id: 902, nombre: 'Silk Turtleneck', precio: 450 }
      ]
    },
    {
      id: 2,
      title: 'Midnight Atelier',
      description: 'Embracing the void with charcoal wools and onyx silks.',
      imageUrl: 'https://images.unsplash.com/photo-1490481651871-ab68de25d43d?q=80&w=1000&auto=format&fit=crop',
      pieces: [
        { id: 903, nombre: 'Structured Evening Blazer', precio: 1850 },
        { id: 904, nombre: 'Wide-Leg Trousers', precio: 890 }
      ]
    },
    {
      id: 3,
      title: 'Sartorial Dawn',
      description: 'Crisp whites and muted champagnes for the modern renaissance.',
      imageUrl: 'https://images.unsplash.com/photo-1539109136881-3be0616acf4b?q=80&w=1000&auto=format&fit=crop',
      pieces: [
        { id: 905, nombre: 'Cashmere V-Neck', precio: 650 },
        { id: 906, nombre: 'Pleated Chinos', precio: 320 }
      ]
    }
  ];

  agregarLookAlCarrito(look: any) {
    for (const piece of look.pieces) {
      this.carrito.agregar({
        id: piece.id,
        nombre: piece.nombre,
        precio: piece.precio,
        imagen_url: look.imageUrl, // Use the look image as fallback
        marca: 'Aurelian Silk'
      } as any, 1);
    }
    this.mensajeExito.set(`The ${look.title} pieces have been added to your bag.`);
    setTimeout(() => this.mensajeExito.set(null), 4000);
  }
}
