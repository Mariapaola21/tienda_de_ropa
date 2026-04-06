import { Component, inject, signal, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { PedidoService, PedidoOut } from '../../../core/services/pedido.service';
import { AuthService } from '../../../core/services/auth.service';

@Component({
  selector: 'app-profile',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './profile.component.html'
})
export class ProfileComponent implements OnInit {
  private readonly pedidoService = inject(PedidoService);
  readonly auth = inject(AuthService);

  orders = signal<PedidoOut[]>([]);
  cargando = signal(true);
  error = signal<string | null>(null);
  valetServiceEnabled = false;

  wishlist = [
    { name: 'Oversized Camel Coat', price: 1200, category: 'Outerwear', imageUrl: 'https://images.unsplash.com/photo-1539109136881-3be0616acf4b?q=80&w=600&auto=format&fit=crop' },
    { name: 'Structured Evening Blazer', price: 1850, category: 'Tailoring', imageUrl: 'https://images.unsplash.com/photo-1490481651871-ab68de25d43d?q=80&w=600&auto=format&fit=crop' },
  ];

  ngOnInit(): void {
    this.pedidoService.misPedidos().subscribe({
      next: (pedidos) => {
        this.orders.set(pedidos);
        this.cargando.set(false);
      },
      error: () => {
        this.error.set('No se pudieron cargar los pedidos.');
        this.cargando.set(false);
      },
    });
  }

  toggleValet(): void {
    this.valetServiceEnabled = !this.valetServiceEnabled;
  }
}
