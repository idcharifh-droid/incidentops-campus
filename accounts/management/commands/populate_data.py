"""
Management command : python manage.py populate_data
Crée les données initiales : catégories, superuser admin, technicien de démo.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from categories.models import Category
from accounts.models import UserProfile, Role
from technicians.models import Technician


class Command(BaseCommand):
    help = 'Peuple la base de données avec des données initiales'

    def handle(self, *args, **kwargs):
        self.stdout.write('=== IncidentOps Campus – Initialisation ===\n')

        # 1. Catégories
        self.stdout.write('Création des catégories...')
        default_cats = [
            ('Réseau', 'bi-wifi', 'primary', 'Problèmes de connexion réseau et WiFi'),
            ('Matériel', 'bi-pc-display', 'secondary', 'Pannes et problèmes matériels'),
            ('Logiciel', 'bi-code-square', 'info', 'Bugs et problèmes applicatifs'),
            ('Compte utilisateur', 'bi-person-lock', 'warning', 'Accès, mots de passe, permissions'),
            ('Sécurité', 'bi-shield-exclamation', 'danger', 'Incidents de sécurité informatique'),
            ('Plateforme pédagogique', 'bi-mortarboard', 'success', 'Moodle, ENT, plateformes de cours'),
            ('Serveur', 'bi-server', 'dark', 'Problèmes serveurs et infrastructure'),
            ('Imprimante', 'bi-printer', 'secondary', 'Imprimantes et périphériques d\'impression'),
            ('Vidéoprojecteur', 'bi-projector', 'info', 'Vidéoprojecteurs et équipement salles'),
            ('Autre', 'bi-question-circle', 'secondary', 'Autre type d\'incident'),
        ]
        for name, icon, color, desc in default_cats:
            cat, created = Category.objects.get_or_create(
                name=name,
                defaults={'icon': icon, 'color': color, 'description': desc}
            )
            status = 'créée' if created else 'déjà existante'
            self.stdout.write(f'  • {name} – {status}')

        # 2. Superuser admin
        self.stdout.write('\nCréation du compte administrateur...')
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser(
                username='admin',
                email='admin@incidentops.local',
                password='Admin1234!',
                first_name='Admin',
                last_name='IncidentOps'
            )
            admin.profile.role = Role.ADMIN
            admin.profile.department = 'Direction IT'
            admin.profile.save()
            self.stdout.write('  • admin / Admin1234! – créé')
        else:
            admin = User.objects.get(username='admin')
            admin.profile.role = Role.ADMIN
            admin.profile.save()
            self.stdout.write('  • admin – déjà existant (rôle mis à jour)')

        # 3. Technicien de démo
        self.stdout.write('\nCréation du technicien de démo...')
        if not User.objects.filter(username='technicien1').exists():
            tech_user = User.objects.create_user(
                username='technicien1',
                email='tech1@incidentops.local',
                password='Tech1234!',
                first_name='Ahmed',
                last_name='Benali'
            )
            tech_user.profile.role = Role.TECHNICIAN
            tech_user.profile.department = 'Support IT'
            tech_user.profile.save()
            tech_obj, _ = Technician.objects.get_or_create(user=tech_user)
            # Assign specializations
            for cat_name in ['Réseau', 'Logiciel', 'Compte utilisateur']:
                try:
                    tech_obj.specializations.add(Category.objects.get(name=cat_name))
                except Category.DoesNotExist:
                    pass
            self.stdout.write('  • technicien1 / Tech1234! – créé (spé: Réseau, Logiciel, Compte)')
        else:
            self.stdout.write('  • technicien1 – déjà existant')

        # 4. Technicien matériel
        if not User.objects.filter(username='technicien2').exists():
            tech2 = User.objects.create_user(
                username='technicien2',
                email='tech2@incidentops.local',
                password='Tech1234!',
                first_name='Fatima',
                last_name='El Amrani'
            )
            tech2.profile.role = Role.TECHNICIAN
            tech2.profile.department = 'Support Matériel'
            tech2.profile.save()
            tech2_obj, _ = Technician.objects.get_or_create(user=tech2)
            for cat_name in ['Matériel', 'Imprimante', 'Vidéoprojecteur']:
                try:
                    tech2_obj.specializations.add(Category.objects.get(name=cat_name))
                except Category.DoesNotExist:
                    pass
            self.stdout.write('  • technicien2 / Tech1234! – créé (spé: Matériel, Imprimante)')
        else:
            self.stdout.write('  • technicien2 – déjà existant')

        # 5. Technicien sécurité/serveur
        if not User.objects.filter(username='technicien3').exists():
            tech3 = User.objects.create_user(
                username='technicien3',
                email='tech3@incidentops.local',
                password='Tech1234!',
                first_name='Youssef',
                last_name='Idrissi'
            )
            tech3.profile.role = Role.TECHNICIAN
            tech3.profile.department = 'Sécurité & Serveurs'
            tech3.profile.save()
            tech3_obj, _ = Technician.objects.get_or_create(user=tech3)
            for cat_name in ['Sécurité', 'Serveur', 'Plateforme pédagogique']:
                try:
                    tech3_obj.specializations.add(Category.objects.get(name=cat_name))
                except Category.DoesNotExist:
                    pass
            self.stdout.write('  • technicien3 / Tech1234! – créé (spé: Sécurité, Serveur)')
        else:
            self.stdout.write('  • technicien3 – déjà existant')

        # 6. Utilisateur de démo
        if not User.objects.filter(username='utilisateur1').exists():
            u = User.objects.create_user(
                username='utilisateur1',
                email='user1@incidentops.local',
                password='User1234!',
                first_name='Mariam',
                last_name='Cherkaoui'
            )
            u.profile.role = Role.USER
            u.profile.department = 'Génie Informatique'
            u.profile.save()
            self.stdout.write('  • utilisateur1 / User1234! – créé')
        else:
            self.stdout.write('  • utilisateur1 – déjà existant')

        # 7. Articles base de connaissances
        self.stdout.write('\nCréation des articles de base de connaissances...')
        from knowledge_base.models import KnowledgeArticle
        admin_user = User.objects.get(username='admin')
        articles = [
            ('Réinitialiser son mot de passe', 'Compte utilisateur',
             'Pour réinitialiser votre mot de passe :\n1. Allez sur la page de connexion\n2. Cliquez sur "Mot de passe oublié"\n3. Entrez votre email universitaire\n4. Suivez le lien reçu par email\n5. Choisissez un nouveau mot de passe sécurisé (min. 8 caractères, majuscule, chiffre)'),
            ('Connexion WiFi impossible', 'Réseau',
             'Si vous ne pouvez pas vous connecter au WiFi campus :\n1. Vérifiez que le WiFi est activé sur votre appareil\n2. Oubliez le réseau et reconnectez-vous\n3. Vérifiez vos identifiants (login universitaire)\n4. Redémarrez votre appareil\n5. Si le problème persiste, soumettez un ticket avec votre numéro de salle'),
            ('Ordinateur qui ne démarre pas', 'Matériel',
             'Étapes de diagnostic :\n1. Vérifiez que le câble d\'alimentation est branché\n2. Appuyez sur le bouton d\'alimentation 10 secondes\n3. Vérifiez que l\'écran est allumé et branché\n4. Essayez de démarrer sans batterie (laptops)\n5. Si toujours bloqué, notez les messages d\'erreur affichés et créez un ticket'),
        ]
        for title, cat_name, content in articles:
            if not KnowledgeArticle.objects.filter(title=title).exists():
                try:
                    cat = Category.objects.get(name=cat_name)
                except Category.DoesNotExist:
                    cat = None
                KnowledgeArticle.objects.create(
                    title=title, content=content, category=cat, author=admin_user
                )
                self.stdout.write(f'  • "{title}" – créé')

        self.stdout.write(self.style.SUCCESS('\n✅  Initialisation terminée avec succès !'))
        self.stdout.write('\n📋  Comptes de démonstration :')
        self.stdout.write('  Admin      : admin / Admin1234!')
        self.stdout.write('  Technicien : technicien1, technicien2, technicien3 / Tech1234!')
        self.stdout.write('  Utilisateur: utilisateur1 / User1234!')
