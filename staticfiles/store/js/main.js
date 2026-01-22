document.addEventListener('DOMContentLoaded', function() {
    const storeUrl = document.querySelector('script[data-store-url]').dataset.storeUrl;
    const searchForm = document.querySelector(`form[action="${storeUrl}"]`);
    if (!searchForm) return;

    const searchInput = searchForm.querySelector('input[name="q"]');
    const minPriceInput = searchForm.querySelector('input[name="min_price"]');
    const maxPriceInput = searchForm.querySelector('input[name="max_price"]');
    let searchTimeout;

    function fetchProducts() {
        if (window.location.pathname !== storeUrl) {
            return;
        }

        const productContainer = document.getElementById('product-grid-container');
        if (!productContainer) return;

        const formData = new FormData(searchForm);
        const params = new URLSearchParams(formData);

        fetch(`${storeUrl}?${params.toString()}`)
            .then(response => response.text())
            .then(html => {
                const parser = new DOMParser();
                const doc = parser.parseFromString(html, 'text/html');
                const newContent = doc.getElementById('product-grid-container');
                if (newContent) {
                    productContainer.innerHTML = newContent.innerHTML;
                }
            })
            .catch(error => console.error('Error fetching products:', error));
    }

    [searchInput, minPriceInput, maxPriceInput].forEach(input => {
        input.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(fetchProducts, 300);
        });
    });

    searchForm.addEventListener('submit', function(e) {
        e.preventDefault();
        fetchProducts();
    });
});
