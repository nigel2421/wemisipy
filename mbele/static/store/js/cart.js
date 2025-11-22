console.debug('static cart.js loaded');

document.addEventListener('DOMContentLoaded', function() {
	// --- TOAST NOTIFICATION FUNCTION ---
	function showToast(message) {
		const container = document.getElementById('toast-container');
		if (!container) return;
		const toast = document.createElement('div');
		toast.className = 'toast-message';
		toast.innerText = message;
		container.appendChild(toast);
		setTimeout(() => { toast.classList.add('show'); }, 100);
		setTimeout(() => {
			toast.classList.remove('show');
			toast.addEventListener('transitionend', () => toast.remove());
		}, 3000);
	}

	// This function will handle the AJAX call to add a product to the cart
	function addToCart(productId, button) {
		console.debug('addToCart called for', productId, 'from', button);
		const url = `/add-to-cart/${encodeURIComponent(productId)}/`;
		const csrftoken = getCsrfToken();

		const headers = {
			'Accept': 'application/json',
			'X-Requested-With': 'XMLHttpRequest',
			'Content-Type': 'application/json'
		};
		if (csrftoken) { headers['X-CSRFToken'] = csrftoken; }

		fetch(url, {
			method: 'POST',
			headers: headers,
			credentials: 'same-origin',
			body: JSON.stringify({ product_id: productId })
		})
		.then(response => {
			console.debug('addToCart response status:', response.status, response.statusText);
			if (!response.ok) {
				return response.text().then(text => { throw new Error(text || 'Request failed'); });
			}
			return response.json().catch(() => ({ message: 'Added (no JSON response)', cart_count: undefined }));
		})
		.then(data => {
			console.debug('addToCart response data:', data);
			const badge = document.getElementById('cart-badge');
			if (badge && typeof data.cart_count !== 'undefined') {
				badge.innerText = data.cart_count;
				badge.style.display = data.cart_count > 0 ? 'inline-block' : 'none';
			}
			const msg = (data && data.message) ? data.message : 'Product added to cart!';
			showToast(msg);
		})
		.catch(error => {
			console.error('Error adding to cart:', error);
			showToast('Unable to add product to cart. Try again.');
		});
	}

	(function() {
		function interactionHandler(event) {
			const selectorTargets = ['.btn-add-cart', '[data-add-to-cart]', '[data-action="add-to-cart"]', '[data-product-id]', '[data-id]', '[data-product]'];
			let button = null;
			for (const sel of selectorTargets) {
				button = event.target.closest(sel);
				if (button) break;
			}
			if (!button) {
				const possibleAnchor = event.target.closest('a[href]');
				if (possibleAnchor && /\/add-to-cart\/([^\/]+)\/?$/.test(possibleAnchor.getAttribute('href'))) {
					button = possibleAnchor;
				}
			}
			if (!button) return;
			if (typeof event.preventDefault === 'function') event.preventDefault();
			event.stopPropagation();

			let productId = button.dataset.productId || button.getAttribute('data-product-id') || button.dataset.id || button.getAttribute('data-id') || button.dataset.product || button.getAttribute('data-product');

			if (!productId) {
				const href = button.getAttribute && button.getAttribute('href');
				if (href) {
					const m = href.match(/\/add-to-cart\/([^\/]+)\/?$/);
					if (m) productId = decodeURIComponent(m[1]);
				}
			}

			if (!productId) {
				const ancestor = button.closest('[data-product-id],[data-id],[data-product]');
				if (ancestor) {
					productId = ancestor.dataset.productId || ancestor.getAttribute('data-product-id') || ancestor.dataset.id || ancestor.getAttribute('data-id') || ancestor.dataset.product || ancestor.getAttribute('data-product');
				}
			}

			if (productId) {
				console.debug('addToCart triggered for productId=', productId, 'from element=', button);
				addToCart(productId, button);
			} else {
				console.warn('Add to cart clicked but no product id found on element:', button);
				showToast('Could not find product identifier.');
			}
		}

		document.addEventListener('click', interactionHandler, true);
		document.addEventListener('pointerdown', interactionHandler, true);

		document.addEventListener('submit', function(event) {
			const form = event.target;
			if (!form || !form.getAttribute) return;
			const action = form.getAttribute('action') || '';
			const m = action.match(/\/add-to-cart\/([^\/]+)\/?$/);
			if (!m) return;
			event.preventDefault();
			event.stopPropagation();
			const productId = decodeURIComponent(m[1]);
			console.debug('form submit intercepted for add-to-cart productId=', productId);
			addToCart(productId, form);
		}, true);
	})();

	function getCsrfToken() {
		const cookieNames = ['csrftoken', 'csrf_token', 'csrf'];
		for (let name of cookieNames) {
			const v = getCookie(name);
			if (v) return v;
		}
		const meta = document.querySelector('meta[name="csrf-token"], meta[name="csrfmiddlewaretoken"], meta[name="csrf"]');
		if (meta) return meta.getAttribute('content');
		const input = document.querySelector('input[name="csrfmiddlewaretoken"], input[name="csrf-token"], input[name="csrf"]');
		if (input) return input.value;
		return null;
	}

	function getCookie(name) {
		let cookieValue = null;
		if (document.cookie && document.cookie !== '') {
			const cookies = document.cookie.split(';');
			for (let i = 0; i < cookies.length; i++) {
				const cookie = cookies[i].trim();
				if (cookie.substring(0, name.length + 1) === (name + '=')) {
					cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
					break;
				}
			}
		}
		return cookieValue;
	}
});