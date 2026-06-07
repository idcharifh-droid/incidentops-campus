# IncidentOps Campus 

**Plateforme de gestion des incidents informatiques**  
Projet de fin de module – Django – Filières d'ingénieurs 2025-2026

---

##  Arborescence complète du projet

```
incidentops/                          ← Racine du projet
│
├── manage.py                         ← Point d'entrée Django CLI
├── requirements.txt                  ← Dépendances Python
├── Dockerfile                        ← Image Docker de l'application
├── docker-compose.yml                ← Orchestration (Django + PostgreSQL + Nginx)
├── entrypoint.sh                     ← Script de démarrage du conteneur
├── nginx.conf                        ← Configuration Nginx (reverse proxy)
├── .env.example                      ← Modèle de variables d'environnement
├── .env                              ← Variables d'environnement (non committé)
├── .gitignore                        ← Fichiers exclus de Git
│
├── .github/
│   └── workflows/
│       └── ci-cd.yml                 ← Pipeline CI/CD GitHub Actions
│
├── incidentops/                      ← Package principal Django
│   ├── __init__.py
│   ├── settings.py                   ← Configuration Django
│   ├── urls.py                       ← URLs racine
│   ├── wsgi.py                       ← WSGI pour Gunicorn
│   ├── asgi.py
│   └── views.py                      ← Handlers 404/500
│
├── accounts/                         ← Gestion utilisateurs & rôles
│   ├── models.py                     ← UserProfile (rôles: user/technician/admin)
│   ├── views.py                      ← Login, register, profil, gestion users
│   ├── forms.py                      ← Formulaires d'inscription/connexion/profil
│   ├── urls.py
│   ├── decorators.py                 ← @admin_required, @technician_required
│   ├── admin.py
│   ├── apps.py
│   ├── tests.py
│   └── management/
│       └── commands/
│           └── populate_data.py      ← Commande d'initialisation des données
│
├── tickets/                          ← Cœur métier : gestion des incidents
│   ├── models.py                     ← Ticket, Comment, Attachment, TicketHistory
│   ├── views.py                      ← CRUD tickets, commentaires, affectation
│   ├── forms.py                      ← Formulaires ticket/commentaire
│   ├── urls.py
│   ├── admin.py
│   ├── apps.py
│   └── tests.py                      ← Tests unitaires (accounts + tickets + IA)
│
├── categories/                       ← Catégories d'incidents
│   ├── models.py                     ← Category
│   ├── views.py
│   ├── urls.py
│   ├── admin.py
│   └── apps.py
│
├── technicians/                      ← Profils techniciens & spécialisations
│   ├── models.py                     ← Technician (spécialisations, charge)
│   ├── views.py
│   ├── urls.py
│   ├── admin.py
│   └── apps.py
│
├── dashboard/                        ← Tableaux de bord (user/tech/admin)
│   ├── views.py
│   ├── urls.py
│   └── apps.py
│
├── notifications/                    ← Notifications internes
│   ├── models.py                     ← Notification
│   ├── views.py
│   ├── urls.py
│   ├── utils.py                      ← Fonctions d'envoi de notifications
│   ├── context_processors.py         ← Injection notifications dans templates
│   └── apps.py
│
├── knowledge_base/                   ← Base de connaissances / articles
│   ├── models.py                     ← KnowledgeArticle
│   ├── views.py
│   ├── urls.py
│   └── apps.py
│
├── ai_classifier/                    ← Module IA : classification automatique
│   ├── classifier.py                 ← TF-IDF + similarité cosinus (scikit-learn)
│   ├── views.py                      ← Endpoint AJAX /ai/classify/
│   ├── urls.py
│   └── apps.py
│
├── reports/                          ← Rapports & exports (CSV, JSON)
│   ├── views.py
│   ├── urls.py
│   └── apps.py
│
├── templates/                        ← Templates HTML (Bootstrap 5)
│   ├── base.html                     ← Layout principal (sidebar + topbar)
│   ├── home.html                     ← Page d'accueil publique
│   ├── 404.html / 500.html
│   ├── accounts/                     ← login, register, profile, users
│   ├── tickets/                      ← list, detail, create
│   ├── dashboard/                    ← user.html, technician.html, admin.html
│   ├── notifications/
│   ├── knowledge_base/
│   ├── categories/
│   ├── technicians/
│   └── reports/
│
├── static/                           ← Fichiers statiques (CSS/JS/images)
│   ├── css/
│   ├── js/
│   └── img/
│
└── media/                            ← Fichiers uploadés (avatars, pièces jointes)
```

---

##  Installation & Démarrage

### Méthode 1 — Avec Docker Compose (recommandée)

```bash
# 1. Cloner le projet
git clone https://github.com/VOTRE_USERNAME/incidentops-campus.git
cd incidentops-campus

# 2. Créer le fichier .env
cp .env.example .env
# Éditez .env et changez les mots de passe !

# 3. Lancer avec Docker Compose
docker-compose up --build

# L'application est disponible sur :
#   http://localhost       (via Nginx, port 80)
#   http://localhost:8000  (Django directement)
```

### Méthode 2 — Sans Docker (développement local)

```bash
# 1. Cloner le projet
git clone https://github.com/VOTRE_USERNAME/incidentops-campus.git
cd incidentops-campus

# 2. Créer l'environnement virtuel Python
python -m venv venv
source venv/bin/activate          # Linux/macOS
# venv\Scripts\activate           # Windows

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Configurer les variables d'environnement
cp .env.example .env
# Éditez .env avec vos paramètres (base de données, etc.)

# 5. Créer la base de données PostgreSQL
createdb incidentops_db
createuser -P incidentops_user

# 6. Appliquer les migrations
python manage.py migrate

# 7. Peupler les données initiales (catégories, comptes de démo)
python manage.py populate_data

# 8. Lancer le serveur de développement
python manage.py runserver
# → http://127.0.0.1:8000
```

---

##  Configuration de la base de données (settings.py)

Le fichier `incidentops/settings.py` lit les variables depuis `.env` via `python-decouple` :

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='incidentops_db'),
        'USER': config('DB_USER', default='incidentops_user'),
        'PASSWORD': config('DB_PASSWORD', default='password'),
        'HOST': config('DB_HOST', default='db'),       # 'db' = service Docker
        'PORT': config('DB_PORT', default='5432'),
    }
}
```

**Pour le développement local**, changez `DB_HOST=localhost` dans `.env`.

---

##  Comptes de démonstration

Après `python manage.py populate_data` :

| Rôle          | Identifiant    | Mot de passe |
|---------------|----------------|--------------|
| Administrateur | `admin`        | `Admin1234!` |
| Technicien 1  | `technicien1`  | `Tech1234!`  |
| Technicien 2  | `technicien2`  | `Tech1234!`  |
| Technicien 3  | `technicien3`  | `Tech1234!`  |
| Utilisateur   | `utilisateur1` | `User1234!`  |

---

##  Module IA – Classification automatique

Le module `ai_classifier/classifier.py` utilise :
- **TF-IDF** (`scikit-learn`) pour vectoriser les descriptions d'incidents
- **Similarité cosinus** pour trouver la catégorie la plus proche
- **Détection de mots-clés d'urgence** pour ajuster la priorité

**Endpoint AJAX** : `POST /ai/classify/`

```json
// Requête
{ "title": "Serveur inaccessible", "description": "Le serveur est down pour tout le campus" }

// Réponse
{ "success": true, "result": { "category": "Serveur", "priority": "critical", "confidence": 0.72 } }
```

Sur la page de création de ticket, l'IA suggère automatiquement catégorie et priorité dès que l'utilisateur tape, avec un bouton pour appliquer la suggestion.

---

##  Sécurité

| Mesure | Implémentation |
|--------|---------------|
| Authentification obligatoire | `@login_required` sur toutes les vues |
| Contrôle d'accès par rôle | `@admin_required`, `@technician_required` |
| Isolation des données | Chaque user ne voit que ses tickets |
| Protection CSRF | Activée par défaut Django |
| Validation fichiers | Extension + taille (max 5 Mo) |
| Variables sensibles | Fichier `.env` (jamais sur Git) |
| Mots de passe | Hashés par Django (PBKDF2) |
| Mode debug | `DEBUG=False` en production |
| En-têtes sécurité | `SECURE_HSTS`, `X_FRAME_OPTIONS`, etc. |

---

## CI/CD GitHub Actions

Le fichier `.github/workflows/ci-cd.yml` exécute à chaque push sur `main` :

1. **Tests** → migrations + tests unitaires + couverture de code
2. **Qualité** → flake8 (analyse statique)
3. **Build Docker** → construction + push sur Docker Hub
4. **Sécurité** → audit des dépendances (pip-audit)

**Configuration requise** (secrets GitHub) :
- `DOCKERHUB_USERNAME` – votre nom d'utilisateur Docker Hub
- `DOCKERHUB_TOKEN` – token d'accès Docker Hub

---

##  Lancer les tests

```bash
# Tests complets
python manage.py test tickets --verbosity=2

# Avec couverture de code
pip install coverage
coverage run manage.py test tickets
coverage report
coverage html    # → htmlcov/index.html
```

---

##  Déploiement production

```bash
# Variables d'environnement (.env)
DEBUG=False
SECRET_KEY=une-cle-tres-longue-et-aleatoire-generee
ALLOWED_HOSTS=votre-domaine.com,www.votre-domaine.com

# Lancer en production
docker-compose up -d --build
```

**Stack production** :
- **Gunicorn** (3 workers) – serveur WSGI
- **Nginx** – reverse proxy + fichiers statiques/media
- **PostgreSQL 15** – base de données
- **Docker Compose** – orchestration

---

## Commandes utiles

```bash
# Migrations
python manage.py makemigrations
python manage.py migrate

# Données initiales
python manage.py populate_data

# Créer un superuser manuellement
python manage.py createsuperuser

# Fichiers statiques
python manage.py collectstatic

# Shell Django
python manage.py shell

# Interface d'administration Django
# → http://127.0.0.1:8000/admin/
```

---

##  Technologies utilisées

| Composant | Technologie |
|-----------|-------------|
| Framework backend | Django 4.2 |
| Base de données | PostgreSQL 15 |
| Serveur WSGI | Gunicorn |
| Reverse proxy | Nginx |
| Frontend | Bootstrap 5 + Bootstrap Icons |
| Intelligence artificielle | scikit-learn (TF-IDF + cosine similarity) |
| Conteneurisation | Docker + Docker Compose |
| CI/CD | GitHub Actions |
| Gestion config | python-decouple |
| Fichiers statiques | WhiteNoise |
| Formulaires | django-crispy-forms + crispy-bootstrap5 |

---

*IncidentOps Campus – Projet de fin de module Django – 2025-2026*
