
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views
from .sitemaps import StaticViewSitemap, ProductSitemap
from django.contrib.sitemaps.views import sitemap

sitemaps = {
    'static': StaticViewSitemap,
    'products': ProductSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')), 
    path('', views.home, name='home'),
    path('store/', views.store, name='store'),
    path('category/<slug:category_slug>/', views.category_detail, name='category_detail'),
    path('product/<int:id>/', views.product_detail, name='product_detail'),
    
    # New Cart URLs
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/update/<int:product_id>/', views.update_cart_item, name='update_cart_item'),
    path('clear-cart/', views.clear_cart, name='clear_cart'),

    # Wishlist URLs
    path('wishlist/', views.wishlist_detail, name='wishlist_detail'),
    path('wishlist/toggle/<int:product_id>/', views.toggle_wishlist, name='toggle_wishlist'),
     path('wishlist/remove/<int:product_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('careers/', views.careers, name='careers'), 
    path('blog/', views.blog, name='blog'), # The main blog page
    path('blog/<slug:slug>/', views.blog_post_detail, name='blog_post_detail'), # The detail page for a single post
    path('search-suggestions/', views.search_suggestions, name='search_suggestions'),
    path("ckeditor5/", include('django_ckeditor_5.urls'), name="ck_editor_5_upload_file"),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
