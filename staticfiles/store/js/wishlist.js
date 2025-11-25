document.addEventListener('DOMContentLoaded', () => {
    const hearts = document.querySelectorAll('.bi-heart, .bi-heart-fill');

    hearts.forEach(heart => {
        // We need to find the product ID. 
        // Since we didn't put it in the HTML, we need to look for the link wrapper
        // Check the parent <a> tag or the nearest button logic.
        // For your specific code, we will add a data-id attribute to the icon-circle in Step 4.
        
        heart.parentElement.addEventListener('click', function(e) {
            e.preventDefault(); // Stop link from opening
            
            const container = this.closest('.product-card');
            // We need a way to get ID. Let's assume we add onclick="toggleWishlist(id)"
            // Actually, the easier way given your setup is to use the function below:
        });
    });
});

// Better approach: Global function called by onclick
function toggleWishlist(productId, element) {
    fetch(`/wishlist/toggle/${productId}/`)
    .then(response => response.json())
    .then(data => {
        const icon = element.querySelector('i');
        
        if (data.added) {
            icon.classList.remove('bi-heart');
            icon.classList.add('bi-heart-fill');
            icon.style.color = 'red';
            alert("Added to Wishlist");
        } else {
            icon.classList.remove('bi-heart-fill');
            icon.classList.add('bi-heart');
            icon.style.color = '#333';
            alert("Removed from Wishlist");
        }
    })
    .catch(error => console.error('Error:', error));
}