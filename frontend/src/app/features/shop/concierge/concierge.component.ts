import { Component } from '@angular/core';

@Component({
  selector: 'app-concierge',
  standalone: true,
  templateUrl: './concierge.component.html'
})
export class ConciergeComponent {
  requestSubmitted = false;
  
  submitRequest() {
    this.requestSubmitted = true;
    setTimeout(() => this.requestSubmitted = false, 5000);
  }
}
