from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import Category, Product, CartItem, Order


class BasicTests(TestCase):
	def setUp(self):
		self.client = Client()
		self.admin = User.objects.create_superuser('admin', 'a@a.com', 'adminpass')
		self.user = User.objects.create_user('user', 'u@u.com', 'userpass')
		self.cat = Category.objects.create(name='TestCat')
		self.prod = Product.objects.create(name='TestProduct', price=1000, stock=5, category=self.cat)

	def test_home_loads(self):
		r = self.client.get('/')
		self.assertEqual(r.status_code, 200)

	def test_add_to_cart_requires_login(self):
		r = self.client.post(f'/cart/add/{self.prod.id}/', {'quantity': 1})
		# should redirect to login
		self.assertIn(r.status_code, (302, 301))

	def test_add_to_cart_and_checkout(self):
		self.client.login(username='user', password='userpass')
		r = self.client.post(f'/cart/add/{self.prod.id}/', {'quantity': 2}, follow=True)
		self.assertEqual(r.status_code, 200)
		ci = CartItem.objects.filter(user=self.user, product=self.prod).first()
		self.assertIsNotNone(ci)
		# checkout
		r2 = self.client.post('/checkout/', follow=True)
		self.assertEqual(r2.status_code, 200)
		orders = Order.objects.filter(user=self.user)
		self.assertTrue(orders.exists())
