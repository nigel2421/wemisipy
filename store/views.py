from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Product, Category, BlogPost
from django.db.models import Q
from django.contrib.auth.decorators import login_required
import urllib.parse # You are using this in cart_detail

# --- EXISTING VIEWS ---



def home(request):
    # Fix: Load all available products for the homepage
    products = Product.objects.filter(available=True).order_by('-id')[:8] 
    return render(request, 'store/home.html', {'products': products})

def store(request):
    """
    This view handles the main store page, including all search and filtering logic.
    """
    products = Product.objects.filter(available=True)
    
    # Get search and filter parameters from the URL
    query = request.GET.get('q')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    
    if query:
        # Use Q objects for a case-insensitive search in name OR description
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))
        
    if min_price:
        # gte = greater than or equal to
        products = products.filter(price__gte=min_price)
        
    if max_price:
        # lte = less than or equal to
        products = products.filter(price__lte=max_price)

    return render(request, 'store/product_list.html', {'category': None, 'products': products})

def category_detail(request, category_slug):
    category = None
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(available=True, category=category)
        return render(request, 'store/product_list.html', {'category': category, 'products': products})

def product_detail(request, id):
    product = get_object_or_404(Product, id=id)
    in_wishlist = False
    # Check if the user is logged in and if the product is in their wishlist
    if request.user.is_authenticated:
        in_wishlist = request.user.wishlist_set.filter(product=product).exists()
    
    context = {
        'product': product,
        'in_wishlist': in_wishlist
    }
    return render(request, 'store/product_detail.html', context)

# --- NEW CART VIEWS ---

@require_POST # Ensure this view only accepts POST requests
def add_to_cart(request, product_id):
    # Get the cart from session, or create empty one
    cart = request.session.get('cart', {})
    
    # Add item or increment quantity
    product_id_str = str(product_id)
    if product_id_str in cart:
        cart[product_id_str] += 1
    else:
        cart[product_id_str] = 1
    
    # Save back to session
    request.session['cart'] = cart
    
    # Return the new count to update the frontend via AJAX
    return JsonResponse({'cart_count': sum(cart.values())})

def cart_detail(request):
    cart = request.session.get('cart', {})
    products = []
    total_price = 0
    
    # Build the list of items for display
    for product_id, quantity in cart.items():
        product = Product.objects.get(id=product_id)
        total = product.price * quantity
        total_price += total
        products.append({
            'product': product,
            'quantity': quantity,
            'total': total
        })

    # --- WHATSAPP LOGIC ---
    phone_number = "+254721202052" # <--- REPLACE WITH YOUR NUMBER
    message = "Hello! I'm interested in the following products:\n\n"
    
    for item in products:
        message += f"- {item['product'].name} (x{item['quantity']}) - Ksh {item['total']}\n"
    
    message += f"\nTotal: Ksh {total_price}\n\nPlease provide me with more information. Thank you."
    
    # Encode message for URL
    whatsapp_url = f"https://wa.me/{phone_number}?text={urllib.parse.quote(message)}"

    return render(request, 'store/cart_detail.html', {
        'cart_items': products, 
        'total_price': total_price,
        'whatsapp_url': whatsapp_url
    })

def clear_cart(request):
    request.session['cart'] = {}
    return redirect('cart_detail')

# --- WISHLIST VIEWS ---

def wishlist_detail(request):
    # 1. Get the list of IDs from the session
    wishlist_ids = request.session.get('wishlist', [])
    
    # 2. Get the actual Product objects from the database
    products = Product.objects.filter(id__in=wishlist_ids)
    
    # 3. Prepare data to match your HTML structure (item.product)
    wishlist_data = [{'product': p} for p in products]
    
    return render(request, 'store/wishlist_detail.html', {'wishlist': wishlist_data})

def toggle_wishlist(request, product_id):
    # Get current list
    wishlist = request.session.get('wishlist', [])
    
    # Toggle logic (Add if missing, Remove if present)
    if product_id in wishlist:
        wishlist.remove(product_id)
        added = False
    else:
        wishlist.append(product_id)
        added = True
        
    # Save back to session
    request.session['wishlist'] = wishlist
    
    return JsonResponse({'added': added, 'count': len(wishlist)})

def remove_from_wishlist(request, product_id):
    # Standard view for the "Remove" button on the wishlist page
    wishlist = request.session.get('wishlist', [])
    
    if product_id in wishlist:
        wishlist.remove(product_id)
        request.session['wishlist'] = wishlist
        
    return redirect('wishlist_detail')

# --- STATIC PAGES VIEWS ---

def careers(request):
    """Renders the careers page."""
    return render(request, 'store/careers.html')

def blog(request):
    """Renders the blog list page."""
    posts = BlogPost.objects.all() # Get all blog posts from the database
    return render(request, 'store/blog_list.html', {'posts': posts})

def blog_post_detail(request, slug):
    """Renders a single blog post detail page."""
    # Get the post by its slug, or return a 404 Not Found error if it doesn't exist
    post = get_object_or_404(BlogPost, slug=slug)
    return render(request, 'store/blog_post_detail.html', {'post': post})