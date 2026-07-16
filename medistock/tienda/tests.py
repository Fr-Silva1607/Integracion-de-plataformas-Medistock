from django.test import TestCase,Client
import json


class MediStockAPITests(TestCase):

    def setUp(self):
        self.client = Client()

#PRUEBA 10 
    def test_contact_page(self):
        response = self.client.get('/contact/')
        self.assertEqual(response.status_code, 200)