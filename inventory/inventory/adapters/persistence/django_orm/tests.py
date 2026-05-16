from django.test import TestCase

class DjangoInventoryAdapter(TestCase):
    def setUp(self):
        pass 
    def test_create_product(self):
        product_data = {
            "sku": "P1",
            "name": "Product ",
            "quantity": 10,
            "low_stock_threshold": 5,
        }

