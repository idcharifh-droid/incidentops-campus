from django.test import TestCase
from ai_classifier.classifier import classify_incident


class AIClassifierTestCase(TestCase):

    def test_classifier_returns_category_and_priority(self):
        result = classify_incident(
            "Problème WiFi",
            "Je n'arrive pas à me connecter au réseau WiFi"
        )

        self.assertIn("category", result)
        self.assertIn("priority", result)
        self.assertIn("confidence", result)