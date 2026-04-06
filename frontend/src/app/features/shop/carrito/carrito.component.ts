import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink, Router } from '@angular/router';
import { CarritoService } from '../../../core/services/carrito.service';
import { PedidoService } from '../../../core/services/pedido.service';
import { AuthService } from '../../../core/services/auth.service';

@Component({
  selector: 'app-carrito',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './carrito.component.html',
})
export class CarritoComponent {
  readonly carrito = inject(CarritoService);
  private readonly pedidoService = inject(PedidoService);
  private readonly auth = inject(AuthService);
  private readonly router = inject(Router);

  procesando = signal(false);
  mensaje = signal<{ tipo: 'ok' | 'error'; texto: string } | null>(null);
  ordenConfirmada = signal<{ id: number; items: any[]; total: number; fecha: Date } | null>(null);

  confirmarPedido(): void {
    if (!this.auth.isLoggedIn()) {
      this.mensaje.set({ tipo: 'error', texto: 'You must log in to secure your checkout.' });
      setTimeout(() => this.router.navigate(['/auth/login']), 2000);
      return;
    }

    this.procesando.set(true);
    this.mensaje.set(null);
    this.ordenConfirmada.set(null);

    const snapshotItems = [...this.carrito.items()];
    const snapshotTotal = this.carrito.total();

    const payload = {
      items: snapshotItems.map(i => ({
        producto_id: i.producto.id,
        variante_id: i.variante?.id,
        cantidad: i.cantidad,
      })),
    };

    this.pedidoService.crearPedido(payload).subscribe({
      next: (pedido) => {
        this.carrito.vaciar();
        this.procesando.set(false);
        this.ordenConfirmada.set({
          id: pedido.id,
          items: snapshotItems,
          total: snapshotTotal,
          fecha: new Date()
        });
      },
      error: (err) => {
        this.procesando.set(false);
        this.mensaje.set({ tipo: 'error', texto: 'Error processing order. Network or Server issue.' });
      },
    });
  }

  imprimirFactura(): void {
    window.print();
  }
}
