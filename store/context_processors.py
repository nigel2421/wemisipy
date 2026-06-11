from .models import Category


def categories_processor(request):
    """
    Provides all categories for use in navigation menus.
    """
    return {"menu_categories": Category.objects.all()}


def cart_processor(request):
    """
    Provides the total number of items in the cart.
    """
    cart = request.session.get("cart", {})
    cart_count = sum(cart.values())
    return {"cart_count": cart_count}


def wishlist_processor(request):
    """
    Provides the total number of items in the wishlist.
    """
    wishlist = request.session.get("wishlist", [])
    return {"wishlist_count": len(wishlist)}


def cart_and_wishlist_count(request):
    """
    Combined context processor used in settings.TEMPLATES to supply:
      - menu_categories: for the categories dropdown
      - cart_count: total items in the cart
      - wishlist_count: total items in the wishlist
    """
    from .models import Cart, Wishlist
    
    cart_count = 0
    wishlist_count = 0
    
    if request.user.is_authenticated:
        # Get count from database
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            cart_count = sum(item.quantity for item in cart.items.all())
        
        wishlist = Wishlist.objects.filter(user=request.user).first()
        if wishlist:
            wishlist_count = wishlist.products.count()
    else:
        # Fall back to session for guest users
        cart = request.session.get("cart", {})
        cart_count = sum(cart.values())
        
        wishlist = request.session.get("wishlist", [])
        wishlist_count = len(wishlist)

    # Only top-level categories; subcategories are accessible via .subcategories.all()
    top_categories = (
        Category.objects
        .filter(parent=None)
        .prefetch_related('subcategories')
        .order_by('order', 'name')
    )

    return {
        "menu_categories": top_categories,
        "cart_count": cart_count,
        "wishlist_count": wishlist_count,
    }