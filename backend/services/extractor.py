import re
import unicodedata
from typing import Tuple, List, Set

# --- CONSTANTES DE CONFIGURATION ---

SKIP_KEYWORDS: Set[str] = {
    # Temporel
    "janvier", "février", "mars", "avril", "mai", "juin",
    "juillet", "août", "aout", "septembre", "octobre", "novembre", "décembre",
    "january", "february", "march", "april", "may", "june",
    "july", "august", "september", "october", "november", "december",
    "jan", "feb", "mar", "apr", "jun", "jul", "aug", "sep", "oct", "nov", "dec",
    "lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche",
    "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday",
    "aujourd'hui", "today", "now", "present", "présent", "actuel", "current",
    "année", "year", "ans", "years", "mois", "month", "months",
    "semaine", "week", "jour", "day", "date", "durée", "duration", "période", "period",
    "depuis", "since", "pendant", "during", "vers", "about",

    # Structure CV & Rubriques
    "curriculum", "vitae", "resume", "cv", "profil", "profile", "portfolio",
    "formation", "education", "enseignement", "academic", "background",
    "expérience", "experience", "expériences", "professionnelle", "work", "history",
    "compétences", "skills", "technologies", "tech", "technical", "aptitudes",
    "langues", "languages", "langue", "linguistique",
    "projets", "projects", "réalisations", "achievements",
    "certifications", "diplômes", "degrees", "certificats", "brevets",
    "intérêts", "hobbies", "loisirs", "activités", "interests", "activities",
    "sommaire", "summary", "objectif", "objective", "about", "me", "infos",
    "références", "references", "annexes", "appendix", "divers", "miscellaneous",

    # Identité Professionnelle
    "développeur", "developer", "dev", "prog", "coder", "programmer",
    "ingénieur", "engineer", "engineering", "génie",
    "stagiaire", "stage", "intern", "internship", "trainee",
    "alternant", "alternance", "apprenti", "apprentissage", "apprentice",
    "étudiant", "student", "élève", "pupil", "graduate", "alumni",
    "data", "scientist", "analyst", "architecte", "architect",
    "manager", "lead", "chef", "directeur", "director", "head", "vp",
    "consultant", "expert", "spécialiste", "specialist",
    "technicien", "technician", "support", "admin", "administrator",
    "fullstack", "backend", "frontend", "devops", "sysadmin", "network",
    "freelance", "indépendant", "contractor", "employé", "employee",
    "junior", "senior", "medior", "confirmé", "confirmed", "lead",

    # Coordonnées
    "tél", "tel", "phone", "mobile", "cell", "fixe", "fax", "gsm",
    "email", "mail", "e-mail", "courriel", "contact", "coordonnées",
    "gmail", "outlook", "hotmail", "yahoo", "icloud", "protonmail",
    "adresse", "address", "domicile", "home", "location", "localisation",
    "rue", "street", "avenue", "boulevard", "bvd", "impasse", "allée", "place",
    "route", "chemin", "road", "way", "lane", "drive",
    "code", "postal", "zip", "cedex", "bp", "appartement", "apt", "étage", "floor",
    "ville", "city", "pays", "country", "france", "paris", "lyon", "marseille",
    "région", "region", "province", "state", "district",
    "linkedin", "github", "gitlab", "bitbucket", "site", "web", "website", "url",

    # Grammaire
    "le", "la", "l", "les", "un", "une", "des", "du", "de", "d",
    "mon", "ma", "mes", "ton", "ta", "tes", "son", "sa", "ses", "notre", "votre", "leur",
    "je", "tu", "il", "elle", "nous", "vous", "ils", "elles", "moi", "toi",
    "ce", "cet", "cette", "ces", "celui", "celle", "ceux", "celles",
    "qui", "que", "quoi", "dont", "où",
    "en", "au", "aux", "à", "a", "dans", "par", "pour", "sur", "avec", "et", "ou", "ni", "car",
    "mais", "donc", "or", "sans", "sous", "chez", "vers",
    "the", "a", "an", "this", "that", "these", "those",
    "my", "your", "his", "her", "its", "our", "their",
    "i", "you", "he", "she", "it", "we", "they", "me", "us", "them",
    "of", "in", "to", "for", "with", "and", "or", "but", "nor", "so", "yet",
    "at", "from", "on", "by", "about", "into", "through", "over", "before", "after",

    # Action & État
    "disponible", "available", "immédiat", "immediate", "immediately",
    "partir", "starting", "démarrage", "start",
    "né", "born", "date", "naissance", "birth", "age", "âge",
    "permis", "driver", "license", "driving", "b", "a", "vehicule", "voiture", "car",
    "recherche", "cherche", "seeking", "looking", "search", "demande",
    "souhaite", "wish", "aimerait", "would", "like",
    "objectif", "goal", "target", "mission", "vision",
    "mention", "spécialité", "option", "niveau", "level", "grade",
    "admis", "admitted", "obtenu", "obtained", "validé", "validated",

    # Qualités / Soft Skills
    "dynamique", "dynamic", "motivé", "motivated", "sérieux", "serious",
    "curieux", "curious", "autonome", "autonomous", "rigueur", "rigorous",
    "équipe", "team", "teamwork", "relationnel", "relational",
    "créatif", "creative", "polyvalent", "versatile", "organisé", "organized",
    "ponctuel", "punctual", "sociable", "leadership", "management"
}

RAW_DEGREES: List[str] = [
    "doctorat", "phd", "ph.d", "docteur",
    "diplôme d'ingénieur", "ingénierie", "ingénieur",
    "master of science", "master", "msc", "m.sc",
    "master of business administration", "mba",
    "mastère", "mastere", "dea", "dess",
    "bachelor universitaire de technologie", "but", "bachelor", "bachelors",
    "b.sc", "b.a", "b.eng", "b.b.a", "b.f.a", "b.tech",
    "licence professionnelle", "licence pro", "licence",
    "brevet de technicien supérieur", "bts",
    "diplôme universitaire de technologie", "dut",
    "deug",
    "baccalauréat", "bac"
]

DEGREE_STOP_WORDS: Set[str] = {
    # Articles & Prépositions en Français et Anglais
    "le", "la", "l", "les", "un", "une", "des", "du", "de", "d",
    "en", "au", "aux", "à", "a", "dans", "par", "pour", "sur", "avec", 
    "et", "ou", "ni", "car", "sans", "sous", "vers", "chez",

    "the", "a", "an",
    "of", "in", "to", "for", "with", "and", "&", "or",
    "at", "from", "on", "by", "about",

    # Vocabulaire Académique / Structure en Francais et Anglais
    "mention", "spécialité", "spécialisation", "option", "filière", "parcours",
    "cursus", "orientation", "branche", "domaine", "intitulé",
    "niveau", "grade", "titre", "diplôme", "certificat",
    "majeure", "mineure", "module", "uv",

    "major", "minor", "specialization", "speciality", "focus", "track",
    "emphasis", "stream", "field", "branch", "concentration",
    "degree", "diploma", "honours", "hons", "award",

    # Parasites (Lieux, Dates, Institutions) 
    "université", "university", "école", "school", "institute", "institut",
    "faculté", "faculty", "academy", "académie",
    "paris", "lyon", "marseille", "france",
    "mars", "avril", "mai", "juin", "juillet", "septembre", "octobre"
}


# FONCTIONS UTILITAIRES 

def clean_text(text: str) -> str:
    """
    Normalise le texte : mise en minuscules, suppression des espaces multiples
    et suppression des accents
    """

    if not text:
        return ""

    text = text.lower()
    
    replacements = {
        'œ': 'oe', 'æ': 'ae', '€': ' euro ',
        '’': "'", '‘': "'", '–': "-"
    }
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)

    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')

    text = re.sub(r'\s+', ' ', text).strip()
    
    return text


# FONCTIONS D'EXTRACTION 

def extract_email(text: str) -> str:
    """Extrait le premier email trouvé. Retourne 'Non trouvé' si echec."""
    if not text:
        return "Non trouvé"

    match = re.search(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', text)
    return match.group(0) if match else "Non trouvé"


def extract_phone(text: str) -> str:
    """Extrait le téléphone. Filtre les années (ex: 2025-2028)."""
    if not text:
        return "Non trouvé"

    pattern = r'(\+?\d{1,3}[\s.-]?)?((?:\d[\s.-]?){7,14}\d)'

    for match in re.finditer(pattern, text):
        phone = match.group(0).strip()
        if re.match(r'^\d{4}(-\d{2,4})?$', phone):
            continue
        return phone

    return "Non trouvé"


def extract_name(text: str) -> Tuple[str, str]:
    """
    Extrait le prénom et le nom depuis les 5 premières lignes.
    Protection : Si text est None, retourne ('Non trouvé', 'Non trouvé').
    """
    if not text:
        return "Non trouvé", "Non trouvé"

    lines = text.splitlines()[:5]

    for line in lines:
        candidates = re.findall(r'\b[A-Za-zÀ-ÿ]{3,}\b', line)
        valid_words = [w for w in candidates if w.lower() not in SKIP_KEYWORDS]
        
        if len(valid_words) >= 2:
            return valid_words[0].capitalize(), valid_words[1].capitalize()

    return "Non trouvé", "Non trouvé"


def extract_degree(text: str) -> str:
    """Identifie le diplôme principal et sa spécialité."""
    if not text:
        return "Non trouvé"

    words = re.findall(r"[^\s]+", text.lower())

    for i, word in enumerate(words):
        for deg in RAW_DEGREES:
            if deg.lower() == word:
                degree = deg.capitalize() if len(deg) > 3 else deg.upper()
                specialty_words = []
                j = i + 1
                while j < len(words) and len(specialty_words) < 2:
                    w = words[j].replace(".", "").replace(",", "").replace("'", "")
                    if w not in DEGREE_STOP_WORDS and not w.isdigit():
                        specialty_words.append(w.capitalize())
                    j += 1
                
                specialty = " ".join(specialty_words)
                return f"{degree} {specialty}".strip() if specialty else degree

    return "Non trouvé"