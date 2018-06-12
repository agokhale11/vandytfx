from django.test import TestCase
from main import models

# Create your tests here


models.Space.objects.create(name="word", teacher="mark", description="test", password="testing",)
if models.Space.objects.filter(name="word").exists():
        print(True)


class TestDatabase(TestCase):

    def setUp(self):
        models.Space.objects.create(name="lion", teacher="roar", description="fake", password="test")
        models.Space.objects.create(name="cat", teacher="yo", description="fake", password="test")

    def test_store_spaces(self):
        """Animals that can speak are correctly identified"""
        lion = models.Space.objects.get(name="lion")
        cat = models.Space.objects.get(name="cat")
        self.assertEqual(lion.name, 'lion')
        self.assertEqual(cat.teacher, 'yo')
