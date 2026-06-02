from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from accounts.models import UserProfile, Role
from categories.models import Category
from tickets.models import Ticket, Status, Priority
from technicians.models import Technician


class AccountsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpass123',
            email='test@test.com', first_name='Test', last_name='User'
        )
        self.user.profile.role = Role.USER
        self.user.profile.save()

    def test_register_page_loads(self):
        resp = self.client.get(reverse('accounts:register'))
        self.assertEqual(resp.status_code, 200)

    def test_login_page_loads(self):
        resp = self.client.get(reverse('accounts:login'))
        self.assertEqual(resp.status_code, 200)

    def test_user_login(self):
        resp = self.client.post(reverse('accounts:login'), {
            'username': 'testuser', 'password': 'testpass123'
        })
        self.assertRedirects(resp, reverse('dashboard:index'))

    def test_profile_auto_created(self):
        self.assertTrue(hasattr(self.user, 'profile'))
        self.assertEqual(self.user.profile.role, Role.USER)

    def test_dashboard_requires_login(self):
        resp = self.client.get(reverse('dashboard:index'))
        self.assertRedirects(resp, '/accounts/login/?next=/dashboard/')


class TicketTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name='Reseau', icon='bi-wifi', color='primary')
        self.user = User.objects.create_user(
            username='user1', password='pass123', first_name='User', last_name='One'
        )
        self.user.profile.role = Role.USER
        self.user.profile.save()
        self.admin = User.objects.create_user(
            username='admin1', password='pass123', first_name='Admin', last_name='One'
        )
        self.admin.profile.role = Role.ADMIN
        self.admin.profile.save()

    def test_ticket_create_requires_login(self):
        resp = self.client.get(reverse('tickets:create'))
        self.assertEqual(resp.status_code, 302)

    def test_user_can_create_ticket(self):
        self.client.login(username='user1', password='pass123')
        self.client.post(reverse('tickets:create'), {
            'title': 'Test incident reseau',
            'description': 'Je ne peux pas me connecter au WiFi',
            'priority': Priority.MEDIUM,
        })
        self.assertEqual(Ticket.objects.count(), 1)
        ticket = Ticket.objects.first()
        self.assertEqual(ticket.created_by, self.user)

    def test_user_cannot_see_others_tickets(self):
        other_user = User.objects.create_user(username='other', password='pass123')
        ticket = Ticket.objects.create(
            title='Other ticket', description='desc',
            created_by=other_user, priority=Priority.LOW
        )
        self.client.login(username='user1', password='pass123')
        resp = self.client.get(reverse('tickets:detail', args=[ticket.pk]))
        self.assertEqual(resp.status_code, 302)

    def test_admin_can_see_all_tickets(self):
        ticket = Ticket.objects.create(
            title='Test', description='desc',
            created_by=self.user, priority=Priority.LOW
        )
        self.client.login(username='admin1', password='pass123')
        resp = self.client.get(reverse('tickets:detail', args=[ticket.pk]))
        self.assertEqual(resp.status_code, 200)

    def test_ticket_priority_badge(self):
        t = Ticket(priority=Priority.CRITICAL)
        self.assertEqual(t.get_priority_badge(), 'danger')
        t.priority = Priority.LOW
        self.assertEqual(t.get_priority_badge(), 'success')


class AIClassifierTestCase(TestCase):
    def test_classify_returns_dict(self):
        from ai_classifier.classifier import classify_incident
        result = classify_incident('Test', 'Test description')
        self.assertIsInstance(result, dict)
        self.assertIn('category', result)
        self.assertIn('priority', result)
        self.assertIn('confidence', result)

    def test_classify_network(self):
        from ai_classifier.classifier import classify_incident
        result = classify_incident(
            'Connexion WiFi impossible',
            'Je ne peux pas me connecter au reseau WiFi'
        )
        self.assertEqual(result['category'], 'Réseau')

    def test_classify_security_is_critical(self):
        from ai_classifier.classifier import classify_incident
        result = classify_incident(
            'Virus detecte', 'Mon ordinateur est infecte par un malware ransomware'
        )
        self.assertEqual(result['priority'], 'critical')
