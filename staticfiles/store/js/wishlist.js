console.debug('static wishlist.js loaded');

// Minimal placeholder to avoid 404; implement wishlist handlers here later
(function() {
	document.addEventListener('DOMContentLoaded', function() {
		const wishlistButtons = document.querySelectorAll('.btn-wishlist');

		wishlistButtons.forEach(button => {
			button.addEventListener('click', function () {
				const productId = this.dataset.productId;
				const action = this.dataset.action;
				const url = `/wishlist/${action}/${productId}/`;

				fetch(url, {
					method: 'POST',
					headers: {
						'X-CSRFToken': getCookie('csrftoken'),
						'Content-Type': 'application/json'
					},
				})
				.then(response => response.json())
				.then(data => {
					console.log('Success:', data);
					updateWishlistCount(data.wishlist_count);
					// Toggle the heart icon
					toggleWishlistIcon(this, data.wishlist_count);
				})
				.catch((error) => {
					console.error('Error:', error);
					alert('Error updating wishlist.');
				});
			});
		});

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

		function updateWishlistCount(count) {
			const wishlistCountElement = document.getElementById('wishlist-badge');
			if (wishlistCountElement) {
				wishlistCountElement.textContent = count;
				if (count > 0) {
					wishlistCountElement.style.display = 'inline-block';
				} else {
					wishlistCountElement.style.display = 'none';
				}
			}
		}

		function toggleWishlistIcon(button, count) {
			const icon = button.querySelector('i');
			if (icon) {
				if (count > 0) {
					icon.classList.remove('bi-heart');
					icon.classList.add('bi-heart-fill');
				} else {
					icon.classList.remove('bi-heart-fill');
					icon.classList.add('bi-heart');
				}
			}
		}

		// Example debug: click on elements with .btn-wishlist will log product id
		document.body.addEventListener('click', function(e) {
			const btn = e.target.closest && e.target.closest('.btn-wishlist, [data-wishlist]');
			if (!btn) return;
			e.preventDefault();
			const id = btn.dataset.productId || btn.getAttribute('data-product-id') || btn.dataset.id || btn.getAttribute('data-id');
			console.debug('wishlist clicked for', id, 'element=', btn);
		});
	});
})();