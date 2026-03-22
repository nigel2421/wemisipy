from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.urls import reverse
from django.views.decorators.http import require_POST
from .models import Product, Category, BlogPost, ProductImage, Cart, CartItem, Wishlist, Order, OrderItem, JobOpening, JobApplication
from django.db.models import Q
from django.contrib.auth.decorators import login_required
import urllib.parse
import json
import uuid
from django.core.mail import send_mail
from django.conf import settings

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
    images = ProductImage.objects.filter(product=product)

    # Simple "similar products" and "frequently bought together" suggestions
    similar_products = (
        Product.objects.filter(available=True, category=product.category)
        .exclude(id=product.id)[:4]
    )
    frequently_bought_together = (
        Product.objects.filter(available=True, category=product.category)
        .exclude(id__in=[product.id])[:3]
    )

    # WhatsApp CTA link for this specific product
    phone_number = "+254721202052"
    message = (
        f"Hello! I'm interested in this product:\n\n"
        f"- {product.name} (Category: {product.category.name})\n"
        f"Price: Ksh {product.price}\n"
        f"Dimensions: {product.dimensions or 'N/A'}\n\n"
        f"Product page: {request.build_absolute_uri()}\n\n"
        f"Please provide me with more information. Thank you."
    )
    whatsapp_url = f"https://wa.me/{phone_number}?text={urllib.parse.quote(message)}"

    context = {
        "product": product,
        "images": images,
        "similar_products": similar_products,
        "frequently_bought_together": frequently_bought_together,
        "whatsapp_url": whatsapp_url,
    }
    return render(request, "store/product_detail.html", context)

# --- NEW CART VIEWS ---

@require_POST
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not item_created:
            cart_item.quantity += 1
            cart_item.save()
        cart_count = sum(item.quantity for item in cart.items.all())
    else:
        cart = request.session.get('cart', {})
        product_id_str = str(product_id)
        if product_id_str in cart:
            cart[product_id_str] += 1
        else:
            cart[product_id_str] = 1
        request.session['cart'] = cart
        cart_count = sum(cart.values())
    
    return JsonResponse({'cart_count': cart_count})

def cart_detail(request):
    cart_items = []
    total_price = 0
    
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            for item in cart.items.all():
                total = item.product.price * item.quantity
                total_price += total
                cart_items.append({
                    'product': item.product,
                    'quantity': item.quantity,
                    'total': total
                })
    else:
        session_cart = request.session.get('cart', {})
        for product_id, quantity in session_cart.items():
            try:
                product = Product.objects.get(id=product_id)
                total = product.price * quantity
                total_price += total
                cart_items.append({
                    'product': product,
                    'quantity': quantity,
                    'total': total
                })
            except Product.DoesNotExist:
                continue

    phone_number = "+254721202052"
    message = "Hello! I'm interested in the following products:\n\n"
    for item in cart_items:
        message += f"- {item['product'].name} (x{item['quantity']}) - Ksh {item['total']}\n"
    message += f"\nTotal: Ksh {total_price}\n\nPlease provide me with more information. Thank you."
    whatsapp_url = f"https://wa.me/{phone_number}?text={urllib.parse.quote(message)}"

    return render(request, 'store/cart_detail.html', {
        'cart_items': cart_items, 
        'total_price': total_price,
        'whatsapp_url': whatsapp_url
    })

@require_POST
def checkout(request):
    """
    Creates an Order from the cart and redirects to WhatsApp with the Order ID.
    """
    cart_items = []
    total_price = 0
    
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        if not cart:
            return redirect('cart_detail')
        if not cart.items.exists():
            return redirect('cart_detail')
        db_items = cart.items.all()
        for item in db_items:
            total_price += item.product.price * item.quantity
            cart_items.append(item)
    else:
        session_cart = request.session.get('cart', {})
        if not session_cart:
            return redirect('cart_detail')
        for product_id, quantity in session_cart.items():
            try:
                product = Product.objects.get(id=product_id)
                total_price += product.price * quantity
                cart_items.append({'product': product, 'quantity': quantity})
            except Product.DoesNotExist:
                continue

    # Create the Order
    order = Order.objects.create(
        user=request.user if request.user.is_authenticated else None,
        total_price=total_price,
        status='Pending',
        full_name=request.POST.get('full_name'),
        phone_number=request.POST.get('phone_number'),
        address=request.POST.get('address'),
        email=request.POST.get('email')
    )
    
    # Create OrderItems
    for item in cart_items:
        product = item.product if hasattr(item, 'product') else item['product']
        quantity = item.quantity if hasattr(item, 'quantity') else item['quantity']
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity,
            price=product.price
        )

    # Clear the cart after order is created
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            cart.items.all().delete()
    else:
        request.session['cart'] = {}

    # Prepare WhatsApp message
    phone_number = "+254721202052"
    message = f"Hello! I want to confirm my order:\n\n"
    message += f"Customer: {order.full_name}\n"
    message += f"Phone: {order.phone_number}\n"
    message += f"Delivery Address: {order.address}\n\n"
    message += "Products:\n"
    
    for item in order.items.all():
        message += f"- {item.product.name} (x{item.quantity}) - Ksh {item.price * item.quantity}\n"
    
    message += f"\nTotal: Ksh {order.total_price}\n"
    message += f"\n--------------------------\n"
    message += f"Order ID: {order.order_id}"
    
    whatsapp_url = f"https://wa.me/{phone_number}?text={urllib.parse.quote(message)}"
    return redirect(whatsapp_url)


@require_POST
def update_cart_item(request, product_id):
    """
    Adjust quantity for a single cart line item.
    Expects an 'action' of 'inc' or 'dec' in POST JSON.
    Returns updated line total, quantity and cart total.
    """
    product = get_object_or_404(Product, id=product_id)
    product_id_str = str(product_id)
    action = ""

    try:
        data = json.loads(request.body or "{}")
        action = data.get("action", "")
    except Exception:
        action = request.POST.get("action", "")

    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)
        
        if action == "inc":
            cart_item.quantity += 1
            cart_item.save()
        elif action == "dec":
            cart_item.quantity = max(cart_item.quantity - 1, 0)
            if cart_item.quantity <= 0:
                cart_item.delete()
            else:
                cart_item.save()
        
        quantity = CartItem.objects.filter(cart=cart, product=product).first().quantity if CartItem.objects.filter(cart=cart, product=product).exists() else 0
        line_total = product.price * quantity
        cart_total = sum(item.product.price * item.quantity for item in cart.items.all())
        cart_count = sum(item.quantity for item in cart.items.all())
    else:
        cart = request.session.get("cart", {})
        quantity = cart.get(product_id_str, 0)

        if action == "inc":
            quantity += 1
        elif action == "dec":
            quantity = max(quantity - 1, 0)

        if quantity <= 0:
            cart.pop(product_id_str, None)
        else:
            cart[product_id_str] = quantity

        request.session["cart"] = cart
        
        cart_total = 0
        for pid, qty in cart.items():
            try:
                p = Product.objects.get(id=pid)
                cart_total += p.price * qty
            except Product.DoesNotExist:
                continue
        
        line_total = product.price * quantity
        cart_count = sum(cart.values())

    return JsonResponse(
        {
            "product_id": product_id,
            "quantity": quantity,
            "line_total": float(line_total),
            "cart_total": float(cart_total),
            "cart_count": cart_count,
        }
    )

@login_required # Ideally only admins, but let's keep it simple for now
def download_invoice(request, order_id):
    """
    Generates a PDF invoice for a given order using PyMuPDF (fitz).
    """
    import fitz
    from django.http import HttpResponse, FileResponse
    import io

    order = get_object_or_404(Order, id=order_id)
    
    # Create a new PDF document
    doc = fitz.open()
    page = doc.new_page()
    
    # Define some basic layout constants
    y = 50
    x = 50
    line_height = 20
    
    # Header
    page.insert_text((x, y), "WEMISI HARDWARE & GENERAL MERCHANDISE", fontsize=18, fontname="helv", color=(0, 0, 0))
    y += 30
    page.insert_text((x, y), "INVOICE / RECEIPT", fontsize=14, fontname="helv-bold")
    y += 40
    
    # Order Info
    page.insert_text((x, y), f"Order ID: {order.order_id}", fontsize=12)
    y += line_height
    page.insert_text((x, y), f"Date: {order.created_at.strftime('%Y-%m-%d %H:%M')}", fontsize=12)
    y += line_height
    if order.user:
        page.insert_text((x, y), f"Customer: {order.user.username}", fontsize=12)
        y += line_height
    
    y += 20
    # Items Table Header
    page.insert_text((x, y), "Product", fontsize=10, fontname="helv-bold")
    page.insert_text((x + 250, y), "Qty", fontsize=10, fontname="helv-bold")
    page.insert_text((x + 300, y), "Price", fontsize=10, fontname="helv-bold")
    page.insert_text((x + 400, y), "Total", fontsize=10, fontname="helv-bold")
    y += 15
    page.draw_line((x, y), (x + 500, y))
    y += 20
    
    # Items
    for item in order.items.all():
        page.insert_text((x, y), item.product.name[:40], fontsize=10)
        page.insert_text((x + 250, y), str(item.quantity), fontsize=10)
        page.insert_text((x + 300, y), f"Ksh {item.price}", fontsize=10)
        page.insert_text((x + 400, y), f"Ksh {item.price * item.quantity}", fontsize=10)
        y += line_height
        if y > 750: # Simple page overflow check
            page = doc.new_page()
            y = 50
    
    y += 10
    page.draw_line((x, y), (x + 500, y))
    y += 25
    
    # Total
    page.insert_text((x + 350, y), "Grand Total:", fontsize=12, fontname="helv-bold")
    page.insert_text((x + 450, y), f"Ksh {order.total_price}", fontsize=12, fontname="helv-bold")
    
    y += 50
    page.insert_text((x, y), "Thank you for shopping with us!", fontsize=10, fontname="helv-italic")
    
    # Save PDF to memory
    pdf_bytes = doc.write()
    doc.close()
    
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{order.order_id}.pdf"'
    return response

def clear_cart(request):
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            cart.items.all().delete()
    else:
        request.session['cart'] = {}
    return redirect('cart_detail')

# --- WISHLIST VIEWS ---

def wishlist_detail(request):
    wishlist_data = []
    if request.user.is_authenticated:
        wishlist = Wishlist.objects.filter(user=request.user).first()
        if wishlist:
            for product in wishlist.products.all():
                wishlist_data.append({'product': product})
    else:
        wishlist_ids = request.session.get('wishlist', [])
        products = Product.objects.filter(id__in=wishlist_ids)
        wishlist_data = [{'product': p} for p in products]
    
    return render(request, 'store/wishlist_detail.html', {'wishlist': wishlist_data})

def toggle_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    added = False
    count = 0

    if request.user.is_authenticated:
        wishlist, created = Wishlist.objects.get_or_create(user=request.user)
        if product in wishlist.products.all():
            wishlist.products.remove(product)
            added = False
        else:
            wishlist.products.add(product)
            added = True
        count = wishlist.products.count()
    else:
        wishlist = request.session.get('wishlist', [])
        if product_id in wishlist:
            wishlist.remove(product_id)
            added = False
        else:
            wishlist.append(product_id)
            added = True
        request.session['wishlist'] = wishlist
        count = len(wishlist)
    
    return JsonResponse({'added': added, 'count': count})

def remove_from_wishlist(request, product_id):
    if request.user.is_authenticated:
        wishlist = Wishlist.objects.filter(user=request.user).first()
        if wishlist:
            product = get_object_or_404(Product, id=product_id)
            wishlist.products.remove(product)
    else:
        wishlist = request.session.get('wishlist', [])
        if product_id in wishlist:
            wishlist.remove(product_id)
            request.session['wishlist'] = wishlist
        
    return redirect('wishlist_detail')

# --- STATIC PAGES VIEWS ---

def careers(request):
    """Renders the careers list page with active job openings."""
    jobs = JobOpening.objects.filter(is_active=True)
    return render(request, 'store/careers.html', {'jobs': jobs})

def job_detail(request, slug):
    """Renders the detail page for a specific job opening."""
    job = get_object_or_404(JobOpening, slug=slug, is_active=True)
    return render(request, 'store/job_detail.html', {'job': job})

@require_POST
def apply_for_job(request, slug):
    """Handles the job application form submission."""
    job = get_object_or_404(JobOpening, slug=slug)
    
    full_name = request.POST.get('full_name')
    email = request.POST.get('email')
    phone = request.POST.get('phone')
    cv = request.FILES.get('cv')
    cover_letter = request.POST.get('cover_letter')
    
    if not all([full_name, email, phone, cv]):
        return JsonResponse({'error': 'Please fill all required fields.'}, status=400)
    
    application = JobApplication.objects.create(
        job=job,
        full_name=full_name,
        email=email,
        phone=phone,
        cv=cv,
        cover_letter=cover_letter
    )
    
    # Send email notification to admin
    try:
        subject = f"New Job Application: {full_name} for {job.title}"
        message = (
            f"A new application has been received for {job.title}.\n\n"
            f"Name: {full_name}\n"
            f"Email: {email}\n"
            f"Phone: {phone}\n"
            f"Cover Letter: {cover_letter}\n\n"
            f"View in Admin: http://{request.get_host()}/admin/store/jobapplication/{application.id}/change/"
        )
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL or 'noreply@wemisi.com',
            [settings.ADMIN_EMAIL or 'admin@wemisi.com'],
            fail_silently=True,
        )
    except Exception as e:
        print(f"Error sending job application mail: {e}")

    return JsonResponse({'success': 'Application submitted successfully!'})

def blog(request):
    """Renders the blog list page."""
    posts = BlogPost.objects.all() # Get all blog posts from the database
    return render(request, 'store/blog_list.html', {'posts': posts})

def blog_post_detail(request, slug):
    """Renders a single blog post detail page."""
    # Get the post by its slug, or return a 404 Not Found error if it doesn't exist
    post = get_object_or_404(BlogPost, slug=slug)
    return render(request, 'store/blog_post_detail.html', {'post': post})


def search_suggestions(request):
    """
    Lightweight JSON endpoint for inline search suggestions.
    Returns up to 5 matching products by name.
    """
    query = request.GET.get("q", "").strip()
    results = []

    if query:
        products = (
            Product.objects.filter(available=True, name__icontains=query)
            .order_by("name")[:5]
        )
        for product in products:
            results.append(
                {
                    "name": product.name,
                    "url": reverse("product_detail", args=[product.id]),
                }
            )

    return JsonResponse({"results": results})