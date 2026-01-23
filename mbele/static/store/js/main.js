document.addEventListener("DOMContentLoaded", function () {
  const scriptTag = document.querySelector("script[data-store-url]");
  if (!scriptTag) return;

  const storeUrl = scriptTag.dataset.storeUrl;
  const suggestUrl = scriptTag.dataset.suggestUrl;
  const searchForm = document.querySelector(`form[action="${storeUrl}"]`);
  if (!searchForm) return;

  const searchInput = searchForm.querySelector('input[name="q"]');
  const minPriceInput = searchForm.querySelector('input[name="min_price"]');
  const maxPriceInput = searchForm.querySelector('input[name="max_price"]');
  const suggestionsBox = document.getElementById("search-suggestions");

  let searchTimeout;
  let suggestTimeout;

  function fetchProducts() {
    // Only live-update grid on the main store page
    if (window.location.pathname !== storeUrl) {
      return;
    }

    const productContainer = document.getElementById("product-grid-container");
    if (!productContainer) return;

    const formData = new FormData(searchForm);
    const params = new URLSearchParams(formData);

    fetch(`${storeUrl}?${params.toString()}`)
      .then((response) => response.text())
      .then((html) => {
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, "text/html");
        const newContent = doc.getElementById("product-grid-container");
        if (newContent) {
          productContainer.innerHTML = newContent.innerHTML;
        }
      })
      .catch((error) => console.error("Error fetching products:", error));
  }

  function renderSuggestions(items) {
    if (!suggestionsBox) return;

    if (!items.length) {
      suggestionsBox.classList.add("d-none");
      suggestionsBox.innerHTML = "";
      return;
    }

    const list = document.createElement("ul");
    list.className = "list-unstyled mb-0";

    items.forEach((item) => {
      const li = document.createElement("li");
      li.className = "px-3 py-2 suggestion-item";

      const link = document.createElement("a");
      link.href = item.url;
      link.textContent = item.name;
      link.className = "text-decoration-none text-dark d-block";

      li.appendChild(link);
      list.appendChild(li);
    });

    suggestionsBox.innerHTML = "";
    suggestionsBox.appendChild(list);
    suggestionsBox.classList.remove("d-none");
  }

  function fetchSuggestions() {
    if (!suggestUrl || !searchInput) return;

    const query = searchInput.value.trim();
    if (query.length < 2) {
      renderSuggestions([]);
      return;
    }

    fetch(`${suggestUrl}?q=${encodeURIComponent(query)}`)
      .then((response) => response.json())
      .then((data) => {
        renderSuggestions(data.results || []);
      })
      .catch((error) => console.error("Error fetching suggestions:", error));
  }

  [searchInput, minPriceInput, maxPriceInput].forEach((input) => {
    if (!input) return;
    input.addEventListener("input", function () {
      clearTimeout(searchTimeout);
      searchTimeout = setTimeout(fetchProducts, 300);
    });
  });

  if (searchInput) {
    searchInput.addEventListener("input", function () {
      clearTimeout(suggestTimeout);
      suggestTimeout = setTimeout(fetchSuggestions, 200);
    });

    // Hide suggestions when leaving the input
    document.addEventListener("click", function (e) {
      if (
        !suggestionsBox ||
        suggestionsBox.contains(e.target) ||
        searchInput.contains(e.target)
      ) {
        return;
      }
      suggestionsBox.classList.add("d-none");
    });
  }

  searchForm.addEventListener("submit", function (e) {
    e.preventDefault();
    renderSuggestions([]);
    fetchProducts();
  });
});
