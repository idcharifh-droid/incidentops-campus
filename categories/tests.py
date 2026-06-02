from django.test import TestCase
from categories.models import Category


class CategoryTestCase(TestCase):

    def test_category_creation(self):
        category = Category.objects.create(
            name="Réseau",
            icon="bi-wifi",
            color="primary"
        )

        self.assertEqual(category.name, "Réseau")
        self.assertEqual(str(category), "Réseau")