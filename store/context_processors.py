from .models import Product

def cart_processor(request):
    cart = request.session.get('cart', {})
    cart_count = sum(cart.values())
    return {'cart_count': cart_count}

def wishlist_processor(request):
    wishlist = request.session.get('wishlist', [])
    return {'wishlist_count': len(wishlist)}