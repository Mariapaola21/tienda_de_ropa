import { Routes } from '@angular/router';

export const routes: Routes = [
  { path: '', redirectTo: 'shop', pathMatch: 'full' },
  {
    path: 'shop',
    loadComponent: () =>
      import('./features/shop/product-list/product-list.component').then(m => m.ProductListComponent),
  },
  {
    path: 'shop/:id',
    loadComponent: () =>
      import('./features/shop/product-detail/product-detail.component').then(m => m.ProductDetailComponent),
  },
  {
    path: 'carrito',
    loadComponent: () =>
      import('./features/shop/carrito/carrito.component').then(m => m.CarritoComponent),
  },
  {
    path: 'auth/login',
    loadComponent: () =>
      import('./features/auth/login/login.component').then(m => m.LoginComponent),
  },
  {
    path: 'auth/register',
    loadComponent: () =>
      import('./features/auth/register/register.component').then(m => m.RegisterComponent),
  },
  {
    path: 'profile',
    loadComponent: () =>
      import('./features/auth/profile/profile.component').then(m => m.ProfileComponent),
  },
  {
    path: 'editorial',
    loadComponent: () =>
      import('./features/shop/editorial/editorial.component').then(m => m.EditorialComponent),
  },
  {
    path: 'heritage',
    loadComponent: () =>
      import('./features/shop/heritage/heritage.component').then(m => m.HeritageComponent),
  },
  {
    path: 'concierge',
    loadComponent: () =>
      import('./features/shop/concierge/concierge.component').then(m => m.ConciergeComponent),
  },
  { path: '**', redirectTo: 'shop' },
];
