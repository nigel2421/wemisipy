console.debug('static wishlist.js loaded');

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

    // --- WISHLIST ADD/REMOVE --- 
    function handleWishlistAction(productId, action, button) {
        const url = `/wishlist/${action}/${encodeURIComponent(productId)}/`;
        const csrftoken = getCsrfToken();

        fetch(url, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest',
            },
            credentials: 'same-origin',
            body: JSON.stringify({ product_id: productId })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            updateWishlistCount(data.wishlist_count);
            toggleWishlistIcon(button, data.added);
            const msg = data.added ? 'Added to wishlist!' : 'Removed from wishlist.';
            showToast(msg);
        })
        .catch(error => {
            console.error('Error updating wishlist:', error);
            showToast('Error updating wishlist.');
        });
    }

    document.body.addEventListener('click', function(e) {
        const button = e.target.closest('.btn-wishlist, [data-wishlist-btn]');
        if (!button) return;
        e.preventDefault();

        const productId = button.dataset.productId || button.getAttribute('data-product-id');
        const isAdded = button.classList.contains('active') || (button.querySelector('i') && button.querySelector('i').classList.contains('bi-heart-fill'));
        const action = isAdded ? 'remove' : 'add';

        if (productId) {
            handleWishlistAction(productId, action, button);
        } else {
            console.error('No product ID found on wishlist button.');
        }
    });

    function updateWishlistCount(count) {
        const badge = document.getElementById('wishlist-badge');
        if (badge) {
            badge.textContent = count;
            badge.style.display = count > 0 ? 'inline-block' : 'none';
        }
    }

    function toggleWishlistIcon(button, isAdded) {
        const icon = button.querySelector('i');
        if (icon) {
            if (isAdded) {
                icon.classList.remove('bi-heart');
                icon.classList.add('bi-heart-fill');
                button.classList.add('active');
            } else {
                icon.classList.remove('bi-heart-fill');
                icon.classList.add('bi-heart');
                button.classList.remove('active');
            }
        }
    }

    function getCsrfToken() {
        const meta = document.querySelector('meta[name="csrf-token"]');
        if (meta) return meta.getAttribute('content');
        return getCookie('csrftoken');
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