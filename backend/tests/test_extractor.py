import sys
import os
import pytest

# Ajout du dossier parent au path pour pouvoir importer 'services'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.extractor import extract_email, extract_phone, extract_degree

# TESTS EMAIL 

def test_extract_email_nominal():
    """Test d'un email standard."""
    text = "Pour me contacter : jean.dupont@gmail.com merci."
    assert extract_email(text) == "jean.dupont@gmail.com"

def test_extract_email_not_found():
    """Test quand il n'y a pas d'email."""
    text = "Bonjour, je m'appelle Jean Dupont."
    assert extract_email(text) == "Non trouvé"

def test_extract_email_complex():
    """Test avec des caractères plus complexes."""
    text = "Contact: prenom-nom_123@mon-domaine.co.uk svp"
    assert extract_email(text) == "prenom-nom_123@mon-domaine.co.uk"


# TESTS TÉLÉPHONE

def test_extract_phone_mobile_fr():
    """Test d'un mobile français classique."""
    text = "Mon portable est le 06 12 34 56 78."
    assert extract_phone(text) == "06 12 34 56 78"

def test_extract_phone_international():
    """Test d'un format international."""
    text = "Joignable au +33 6 12 34 56 78."
    assert extract_phone(text) == "+33 6 12 34 56 78"

def test_extract_phone_ignore_dates():
    """
    CRITIQUE : Vérifie qu'une plage de dates (ex: 2020-2022) 
    n'est PAS détectée comme un numéro de téléphone.
    """
    text = "Expérience chez Google de 2020-2022."
    assert extract_phone(text) == "Non trouvé"

def test_extract_phone_with_dots():
    """Test avec des points comme séparateurs."""
    text = "Tel: 01.45.67.89.10"
    assert extract_phone(text) == "01.45.67.89.10"


# TESTS DIPLÔME

def test_extract_degree_simple():
    """Test d'un diplôme simple sans spécialité."""
    text = "J'ai obtenu mon Baccalauréat en 2015."
    # La fonction capitalise le résultat
    assert extract_degree(text) == "Baccalauréat"

def test_extract_degree_with_specialty():
    """Test d'un diplôme avec spécialité (Master Data Science)."""
    text = "Diplômé d'un Master Data Science à Paris."
    # Doit capturer 'Master' + 2 mots suivants valides
    assert extract_degree(text) == "Master Data Science"

def test_extract_degree_skip_stopwords():
    """
    Test la gestion des mots de liaison (de, en...).
    'BUT Informatique de Gestion' -> Doit ignorer 'de' et prendre 'Gestion'.
    """
    text = "Titulaire d'un BUT Informatique de Gestion."
    assert extract_degree(text) == "But Informatique Gestion"

def test_extract_degree_not_found():
    """Test quand aucun diplôme connu n'est présent."""
    text = "J'ai suivi une formation en cuisine."
    assert extract_degree(text) == "Non trouvé"