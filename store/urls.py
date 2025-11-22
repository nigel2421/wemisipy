from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('products/', views.product_list, name='store'),
    path('category/<slug:category_slug>/', views.product_list, name='category_detail'),
    path('product/<int:id>/', views.product_detail, name='product_detail'),
    
    # New Cart URLs
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('clear-cart/', views.clear_cart, name='clear_cart'),

    # Wishlist URLs
    path('wishlist/', views.wishlist_detail, name='wishlist_detail'),
    path('wishlist/toggle/<int:product_id>/', views.toggle_wishlist, name='toggle_wishlist'),
     path('wishlist/remove/<int:product_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('careers/', views.home, name='careers'), 
    path('blog/', views.home, name='blog'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)