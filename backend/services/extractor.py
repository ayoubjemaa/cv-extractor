import re
import unicodedata
from typing import Tuple


def clean_text(text: str) -> str:
    """Normalise le texte : mise en minuscules et suppression des espaces multiples."""
    text = text.lower()
    text = re.sub(r'\s+', ' ', text)
    return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')


def extract_email(text: str) -> str:
    """Extrait le premier email trouvé dans le texte, sinon retourne 'Non trouvé'."""
    match = re.search(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', text)
    return match.group(0) if match else "Non trouvé"


def extract_phone(text: str) -> str:
    """
    Extrait le premier numéro de téléphone valide.
    Ignore les années ou formats du type 2025-2028.
    """
    pattern = r'(\+?\d{1,3}[\s.-]?)?((?:\d[\s.-]?){7,14}\d)'

    for match in re.finditer(pattern, text):
        phone = match.group(0).strip()

        # Ignore les années (ex : 2025 ou 2025-2028)
        if re.match(r'^\d{4}(-\d{2,4})?$', phone):
            continue

        return phone

    return "Non trouvé"


def extract_name(text: str, email: str = "") -> Tuple[str, str]:
    """
    Tente d'extraire le prénom et le nom depuis les 5 premières lignes.
    Ignore une large liste de mots non pertinents (postes, rubriques, villes, etc.).
    Si aucun nom n'est trouvé, tente de le déduire à partir de l'email.
    """

    skip_keywords = {
        "curriculum", "vitae", "resume", "cv", "profil", "profile", "portfolio",
        "formation", "education", "enseignement",
        "expérience", "experience", "expériences", "professionnelle",
        "compétences", "skills", "technologies", "tech",
        "langues", "languages", "langue",
        "projets", "projects", "réalisations",
        "certifications", "intérêts", "hobbies", "loisirs",
        "sommaire", "summary", "objectif", "about", "me",
        "développeur", "developer", "dev", "software", "web", "mobile",
        "ingénieur", "engineer", "engineering",
        "stagiaire", "stage", "intern", "internship",
        "alternant", "alternance", "apprenti", "apprentissage",
        "étudiant", "student", "élève",
        "data", "scientist", "analyst", "architecte",
        "manager", "lead", "chef", "directeur", "director", "consultant",
        "technicien", "support", "admin", "fullstack", "backend", "frontend", "devops",
        "tél", "tel", "phone", "mobile", "cell", "fixe", "fax",
        "email", "mail", "e-mail", "courriel", "gmail", "outlook", "hotmail",
        "adresse", "address", "domicile",
        "rue", "street", "avenue", "boulevard", "bvd", "impasse", "allée", "place", "route", "chemin",
        "code", "postal", "zip", "cedex", "Mars",
        "ville", "city", "pays", "country", "france", "paris", "région",
        "linkedin", "github", "gitlab", "site", "web",
        "le", "la", "l", "les", "un", "une", "des", "du", "de",
        "en", "au", "aux", "à", "a", "dans", "par", "pour", "sur", "avec", "et", "ou", "sans", "sous",
        "the", "of", "in", "to", "for", "with", "and", "at", "from", "on", "by",
        "disponible", "available", "immédiat", "immediate",
        "partir", "starting", "depuis", "since",
        "mois", "month", "année", "year", "ans", "years",
        "né", "born", "date", "naissance", "birth",
        "permis", "driver", "license", "vehicule",
        "mention", "spécialité", "option", "niveau", "grade"
    }

    # Analyse des 5 premières lignes
    lines = text.splitlines()[:5]

    for line in lines:
        words = [
            w for w in re.findall(r"[A-Za-zÀ-ÿ]+", line)
            if w.lower() not in skip_keywords
        ]

        if len(words) >= 2:
            return words[0].capitalize(), words[1].capitalize()

    # Fallback : extraction via email
    if email:
        match = re.match(r"([a-zA-Z]+)[._-]?([a-zA-Z]+)", email)
        if match:
            return match.group(1).capitalize(), match.group(2).capitalize()

    return "Non trouvé", "Non trouvé"


def extract_degree(text: str) -> str:
    """
    Identifie le diplôme principal présent dans le texte.
    Détecte aussi une spécialité éventuelle en filtrant les mots parasites.
    """

    raw_degrees = [
        "doctorat", "phd", "ph.d", "docteur",
        "diplôme d'ingénieur", "ingénierie", "ingénieur",
        "master of science", "master", "msc", "m.sc",
        "master of business administration", "mba",
        "mastère", "mastere", "dea", "dess",
        "bachelor universitaire de technologie", "bachelor", "bachelors",
        "b.sc", "b.a", "b.eng", "b.b.a", "b.f.a", "b.tech",
        "licence professionnelle", "licence pro", "licence", "but",
        "brevet de technicien supérieur", "bts",
        "diplôme universitaire de technologie", "dut",
        "deug",
        "baccalauréat", "bac"
    ]

    degrees = sorted(raw_degrees, key=len, reverse=True)
    stop_words = {"en", "de", "du", "dans", "mention", "spécialité", "avec",
                  "et", "la", "le", "l", "des", "aux", "pour"}

    pattern = rf"\b({'|'.join(degrees)})\b\s*((?:[^\d\W_]+(?:'[^\d\W_]+)?\.?\s*)+)"
    match = re.search(pattern, text.lower(), re.IGNORECASE | re.UNICODE)

    if not match:
        return "Non trouvé"

    degree_raw = match.group(1)
    degree = degree_raw.upper() if '.' in degree_raw else degree_raw.capitalize()

    specialty_words = match.group(2).split()
    filtered_words = [
        w.replace("'", "").replace(".", "")
        for w in specialty_words
        if w.lower() not in stop_words
        and not w.isdigit()
        and len(w.replace("'", "")) > 1
    ]

    specialty = " ".join(filtered_words[:2]).title()
    return f"{degree} {specialty}".strip() if filtered_words else degree
