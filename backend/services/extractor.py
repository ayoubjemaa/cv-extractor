import re
import unicodedata
import logging
from typing import Tuple, List, Set

# --- CONFIGURATION LOGGING ---
logger = logging.getLogger(__name__)

# --- CONSTANTES DE CONFIGURATION ---

# Mots à ignorer lors de l'analyse (dates, structure, soft skills...)
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

    # Grammaire & Mots courants
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

    # Soft Skills
    "dynamique", "dynamic", "motivé", "motivated", "sérieux", "serious",
    "curieux", "curious", "autonome", "autonomous", "rigueur", "rigorous",
    "équipe", "team", "teamwork", "relationnel", "relational",
    "créatif", "creative", "polyvalent", "versatile", "organisé", "organized",
    "ponctuel", "punctual", "sociable", "leadership", "management"
}

# Liste des diplômes connus
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

# Mots d'arrêt pour la détection de la spécialité du diplôme
DEGREE_STOP_WORDS: Set[str] = {
    # Articles & Prépositions
    "le", "la", "l", "les", "un", "une", "des", "du", "de", "d",
    "en", "au", "aux", "à", "a", "dans", "par", "pour", "sur", "avec", 
    "et", "ou", "ni", "car", "sans", "sous", "vers", "chez",
    "the", "a", "an", "of", "in", "to", "for", "with", "and", "&", "or",
    "at", "from", "on", "by", "about",

    # Vocabulaire Académique / Structure
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


# --- FONCTIONS UTILITAIRES ---

def clean_text(text: str) -> str:
    """
    Normalise le texte : mise en minuscules, suppression des espaces multiples
    et suppression des accents.
    """
    if not text:
        return ""

    try:
        text = text.lower()
        
        replacements = {
            'œ': 'oe', 'æ': 'ae', '€': ' euro ',
            '’': "'", '‘': "'", '–': "-"
        }
        for char, repl in replacements.items():
            text = text.replace(char, repl)

        text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
        return re.sub(r'\s+', ' ', text).strip()
    
    except Exception as e:
        logger.warning(f"Echec du nettoyage de texte : {e}")
        return text


# --- FONCTIONS D'EXTRACTION ---

def extract_email(text: str) -> str:
    """Extrait le premier email trouvé."""
    if not text: 
        return "Non trouvé"

    try:
        match = re.search(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', text)
        return match.group(0) if match else "Non trouvé"
    except Exception as e:
        logger.error(f"Erreur regex email : {e}")
        return "Non trouvé"


def extract_phone(text: str) -> str:
    """Extrait le téléphone en filtrant les années (ex: 2025-2028)."""
    if not text: 
        return "Non trouvé"

    pattern = r'(\+?\d{1,3}[\s.-]?)?((?:\d[\s.-]?){7,14}\d)'

    try:
        for match in re.finditer(pattern, text):
            phone = match.group(0).strip()
            # Protection contre les années
            if re.match(r'^\d{4}(-\d{2,4})?$', phone):
                continue
            return phone
    except Exception as e:
        logger.error(f"Erreur regex téléphone : {e}")

    return "Non trouvé"


def extract_name(text: str) -> Tuple[str, str]:
    """
    Extrait le prénom et le nom.
    Priorité : En-tête du CV sinon Deviné via l'email.
    """
    if not text: 
        return "Non trouvé", "Non trouvé"

    try:
        # Recherche dans les 5 premières lignes
        lines = text.splitlines()[:5]

        for line in lines:
            candidates = re.findall(r'\b[A-Za-zÀ-ÿ]{3,}\b', line)
            valid_words = [w for w in candidates if w.lower() not in SKIP_KEYWORDS]
            
            if len(valid_words) >= 2:
                return valid_words[0].capitalize(), valid_words[1].capitalize()

        # Si échec, tentative via l'email
        email = extract_email(text)
        if email and email != "Non trouvé":
            # Nettoyage de la partie locale (avant @) pour retirer les chiffres
            local_part = re.sub(r'\d+', '', email.split("@")[0])
            parts = re.split(r'[._-]', local_part)
            
            valid_parts = [p for p in parts if len(p) >= 2]
            
            if len(valid_parts) >= 2:
                return valid_parts[0].capitalize(), valid_parts[1].capitalize()
    
    except Exception as e:
        logger.error(f"Erreur extraction nom : {e}")

    return "Non trouvé", "Non trouvé"


def extract_degree(text: str) -> str:
    """
    Recherche un diplôme connu et tente d'extraire la spécialité associée.
    Ex: 'BUT Informatique de Gestion' -> 'But Informatique Gestion'
    """
    if not text:
        return "Non trouvé"

    try:
        words = re.findall(r"[^\s]+", text.lower())

        for i, word in enumerate(words):
            if word in RAW_DEGREES:
                #extraction diplome
                degree = word.capitalize()
                
                # Recherche de la spécialité dans les mots suivants
                specialty_parts = []
                
                for next_word in words[i + 1 : i + 10]:
                    clean_word = next_word.replace(".", "").replace(",", "").replace("'", "")
                    
                    if clean_word in DEGREE_STOP_WORDS or clean_word.isdigit():
                        continue
                    
                    #rendre la spécialité de 2 mots uniquement
                    specialty_parts.append(clean_word.capitalize())
                    if len(specialty_parts) >= 2:
                        break
                
                full_title = f"{degree} {' '.join(specialty_parts)}".strip()
                return full_title

    except Exception as e:
        logger.error(f"Erreur inattendue lors de l'extraction du diplôme : {e}")

    return "Non trouvé"