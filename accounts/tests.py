from django.test import TestCase
from django.contrib.auth.models import User
from accounts.models import Role


class AccountsTestCase(TestCase):

    def test_user_profile_created_automatically(self):
        user = User.objects.create_user(
            username="hiba",
            password="testpass123"
        )

        self.assertTrue(hasattr(user, "profile"))
        self.assertEqual(user.profile.role, Role.USER)