import json
from django.test import TestCase, Client
from django.urls import reverse
from store.models import Product, Cart, CartItem, Wishlist
from django.contrib.auth.models import User

class StoreFunctionalityTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.login(username='testuser', password='password')
        self.product = Product.objects.create(name='Test Product', price=100.00)

    def test_add_to_cart(self):
        response = self.client.post(reverse('add_to_cart', args=[self.product.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Cart.objects.count(), 1)
        self.assertEqual(CartItem.objects.count(), 1)
        self.assertEqual(CartItem.objects.first().product, self.product)

    def test_add_to_wishlist(self):
        response = self.client.post(reverse('add_to_wishlist', args=[self.product.id]))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['added'])
        self.assertEqual(Wishlist.objects.count(), 1)

    def test_remove_from_wishlist(self):
        wishlist = Wishlist.objects.create(user=self.user)
        wishlist.products.add(self.product)
        response = self.client.post(reverse('remove_from_wishlist', args=[self.product.id]))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertFalse(data['added'])
        self.assertEqual(wishlist.products.count(), 0)
