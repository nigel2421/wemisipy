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
    cart = request.session.get("cart", {})
    wishlist = request.session.get("wishlist", [])

    return {
        "menu_categories": Category.objects.all(),
        "cart_count": sum(cart.values()),
        "wishlist_count": len(wishlist),
    }