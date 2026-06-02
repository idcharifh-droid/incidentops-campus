"""
AI Classifier for IncidentOps Campus
Uses TF-IDF + Cosine Similarity to classify incidents by category and priority.
"""
import os
import json
import numpy as np

# Training data: (description_keywords, category, priority)
TRAINING_DATA = [
    # Réseau
    ("wifi connexion internet réseau déconnexion lent accès point accès câble ethernet",
     "Réseau", "medium"),
    ("wi-fi ne fonctionne pas connexion internet coupée réseau instable pas de réseau",
     "Réseau", "high"),
    ("impossible accéder internet wifi déconnecte fréquemment réseau lent",
     "Réseau", "medium"),
    ("perte connexion réseau campus ethernet switch routeur vpn",
     "Réseau", "high"),

    # Matériel
    ("ordinateur ne démarre pas écran noir panne hardware clavier souris",
     "Matériel", "high"),
    ("écran cassé ordinateur tombe en panne disque dur batterie chargeur",
     "Matériel", "high"),
    ("clavier ne répond plus souris fonctionne pas port usb défectueux",
     "Matériel", "medium"),
    ("ordinateur lent freezes plantage mémoire ram processeur surchauffe",
     "Matériel", "medium"),

    # Logiciel
    ("logiciel ne s'ouvre pas application plante erreur installation mise à jour",
     "Logiciel", "medium"),
    ("application crash erreur logiciel bug programme ne répond pas",
     "Logiciel", "medium"),
    ("windows erreur mise à jour office word excel powerpoint outlook",
     "Logiciel", "low"),
    ("antivirus licence expirée logiciel installé malware virus",
     "Logiciel", "high"),

    # Compte utilisateur
    ("mot de passe oublié compte bloqué connexion impossible identifiants",
     "Compte utilisateur", "medium"),
    ("réinitialisation mot de passe compte verrouillé accès refusé authentification",
     "Compte utilisateur", "medium"),
    ("créer compte nouveau utilisateur permissions accès droits",
     "Compte utilisateur", "low"),
    ("email messagerie accès boite mail outlook teams",
     "Compte utilisateur", "low"),

    # Sécurité
    ("virus malware ransomware attaque piratage intrusion accès non autorisé",
     "Sécurité", "critical"),
    ("phishing email suspect lien malveillant tentative hameçonnage arnaque",
     "Sécurité", "critical"),
    ("données volées fuite données sécurité compromis accès illégal",
     "Sécurité", "critical"),
    ("compte piraté mot de passe changé activité suspecte connexion inconnue",
     "Sécurité", "critical"),

    # Plateforme pédagogique
    ("moodle plateforme cours en ligne e-learning espace numérique travail",
     "Plateforme pédagogique", "medium"),
    ("accès cours plateforme pédagogique impossible moodle teams classe virtuelle",
     "Plateforme pédagogique", "high"),
    ("devoir soumis pas visible note cours en ligne espace étudiant",
     "Plateforme pédagogique", "medium"),

    # Serveur
    ("serveur inaccessible tous étudiants application down hors service production",
     "Serveur", "critical"),
    ("serveur web tombé base données inaccessible service indisponible erreur 500",
     "Serveur", "critical"),
    ("serveur lent performances dégradées temps réponse élevé charge serveur",
     "Serveur", "high"),
    ("backup sauvegarde serveur espace disque plein stockage serveur",
     "Serveur", "medium"),

    # Imprimante
    ("imprimante ne fonctionne pas impression bloquée bourrage papier cartouche",
     "Imprimante", "low"),
    ("imprimante hors ligne driver pilote imprimante installation",
     "Imprimante", "low"),

    # Vidéoprojecteur
    ("vidéoprojecteur ne s'allume pas projection problème salle cours affichage",
     "Vidéoprojecteur", "medium"),
    ("projecteur image floue câble hdmi connexion salle amphi",
     "Vidéoprojecteur", "low"),

    # Autre
    ("autre problème divers demande information question générale",
     "Autre", "low"),
]

PRIORITY_KEYWORDS = {
    "critical": [
        "tous", "toute l'école", "tout le campus", "inaccessible pour tous",
        "serveur down", "production", "hors service", "virus", "piratage",
        "données volées", "attaque", "ransomware", "urgent", "critique",
        "bloque tout le monde", "impossible pour personne"
    ],
    "high": [
        "urgent", "bloqué", "impossible", "complètement", "ne démarre pas",
        "panne totale", "depuis plusieurs jours", "empêche de travailler"
    ],
    "medium": [
        "lent", "problème", "ne fonctionne pas bien", "parfois", "intermittent"
    ],
    "low": [
        "demande", "question", "information", "amélioration", "suggestion"
    ]
}


def _compute_tfidf_similarity(query, documents):
    """Compute TF-IDF cosine similarity between query and documents."""
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity

        corpus = documents + [query]
        vectorizer = TfidfVectorizer(
            analyzer='word',
            ngram_range=(1, 2),
            min_df=1,
            stop_words=None
        )
        tfidf_matrix = vectorizer.fit_transform(corpus)
        query_vec = tfidf_matrix[-1]
        doc_vecs = tfidf_matrix[:-1]
        similarities = cosine_similarity(query_vec, doc_vecs).flatten()
        return similarities
    except ImportError:
        # Fallback: keyword matching
        return _keyword_similarity(query, documents)


def _keyword_similarity(query, documents):
    """Simple keyword overlap similarity as fallback."""
    query_words = set(query.lower().split())
    scores = []
    for doc in documents:
        doc_words = set(doc.lower().split())
        intersection = query_words & doc_words
        union = query_words | doc_words
        score = len(intersection) / len(union) if union else 0
        scores.append(score)
    return scores


def _adjust_priority_by_keywords(text, base_priority):
    """Override priority if strong keywords detected."""
    text_lower = text.lower()
    for priority, keywords in PRIORITY_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                # Only upgrade priority, never downgrade
                priority_order = ['low', 'medium', 'high', 'critical']
                if priority_order.index(priority) > priority_order.index(base_priority):
                    return priority
                break
    return base_priority


def classify_incident(title, description):
    """
    Classify an incident based on title and description.
    Returns dict with 'category' and 'priority'.
    """
    try:
        text = f"{title} {description}".lower()

        docs = [item[0] for item in TRAINING_DATA]
        categories = [item[1] for item in TRAINING_DATA]
        priorities = [item[2] for item in TRAINING_DATA]

        similarities = _compute_tfidf_similarity(text, docs)
        best_idx = int(np.argmax(similarities))
        best_score = similarities[best_idx]

        if best_score < 0.05:
            return {'category': 'Autre', 'priority': 'medium', 'confidence': 0}

        suggested_category = categories[best_idx]
        suggested_priority = priorities[best_idx]

        # Adjust priority based on urgency keywords
        suggested_priority = _adjust_priority_by_keywords(text, suggested_priority)

        return {
            'category': suggested_category,
            'priority': suggested_priority,
            'confidence': round(float(best_score), 3)
        }
    except Exception as e:
        return {'category': 'Autre', 'priority': 'medium', 'confidence': 0, 'error': str(e)}
