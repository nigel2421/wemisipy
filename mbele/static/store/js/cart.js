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
			refreshMiniCart();
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

	// --- MINI CART + INLINE QUANTITY ---

	function refreshMiniCart() {
		const drawerBody = document.getElementById('mini-cart-body');
		const drawer = document.getElementById('mini-cart-drawer');
		if (!drawerBody || !drawer) return;

		fetch('/cart/')
			.then(response => response.text())
			.then(html => {
				const parser = new DOMParser();
				const doc = parser.parseFromString(html, 'text/html');
				const content = doc.getElementById('cart-items-table');
				const total = doc.getElementById('cart-total-amount');

				if (content) {
					drawerBody.innerHTML = content.outerHTML + (total ? `<div class="mt-3 fw-bold">${total.textContent}</div>` : '');
				} else {
					drawerBody.innerHTML = '<p class="mb-0">Your cart is empty.</p>';
				}

				openMiniCart();
			})
			.catch(err => console.error('Error refreshing mini cart:', err));
	}

	function openMiniCart() {
		const drawer = document.getElementById('mini-cart-drawer');
		const overlay = document.getElementById('mini-cart-overlay');
		if (!drawer || !overlay) return;
		drawer.classList.add('show');
		overlay.classList.add('show');
	}

	function closeMiniCart() {
		const drawer = document.getElementById('mini-cart-drawer');
		const overlay = document.getElementById('mini-cart-overlay');
		if (!drawer || !overlay) return;
		drawer.classList.remove('show');
		overlay.classList.remove('show');
	}

	document.addEventListener('click', function (e) {
		if (e.target.matches('#mini-cart-close') || e.target.closest('#mini-cart-close')) {
			e.preventDefault();
			closeMiniCart();
		}
		if (e.target.matches('#mini-cart-overlay')) {
			closeMiniCart();
		}
	});

	document.addEventListener('click', function (e) {
		const minusBtn = e.target.closest('.btn-qty-minus');
		const plusBtn = e.target.closest('.btn-qty-plus');
		if (!minusBtn && !plusBtn) return;

		const row = (minusBtn || plusBtn).closest('tr[data-product-id]');
		if (!row) return;

		const productId = row.getAttribute('data-product-id');
		const action = plusBtn ? 'inc' : 'dec';
		const csrftoken = getCsrfToken();

		fetch(`/cart/update/${productId}/`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				'X-Requested-With': 'XMLHttpRequest',
				...(csrftoken ? { 'X-CSRFToken': csrftoken } : {})
			},
			credentials: 'same-origin',
			body: JSON.stringify({ action })
		})
		.then(res => res.json())
		.then(data => {
			if (data.error) return;

			// Update header cart badge
			const badge = document.getElementById('cart-badge');
			if (badge && typeof data.cart_count !== 'undefined') {
				badge.innerText = data.cart_count;
				badge.style.display = data.cart_count > 0 ? 'inline-block' : 'none';
			}

			// Update quantity & line total on full cart page
			const qtyInput = row.querySelector('.cart-item-qty');
			const lineTotalCell = row.querySelector('.cart-item-total');
			if (data.quantity <= 0) {
				row.remove();
			} else {
				if (qtyInput) qtyInput.value = data.quantity;
				if (lineTotalCell) lineTotalCell.textContent = `Ksh ${data.line_total}`;
			}

			// Update cart total
			const totalAmount = document.getElementById('cart-total-amount');
			if (totalAmount) totalAmount.textContent = `Ksh ${data.cart_total}`;
		})
		.catch(err => console.error('Error updating cart item:', err));
	});
});