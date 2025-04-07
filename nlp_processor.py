import os
import json
import logging
import re
from difflib import SequenceMatcher

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load FAQ data
def load_faq_data():
    """Load FAQ data from JSON file."""
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.join(script_dir, 'data', 'faq_data.json')
        
        with open(data_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading FAQ data: {str(e)}")
        # Return a minimal default dataset if file can't be loaded
        return {
            "faqs": [
                {
                    "question": "Τι είναι η ΕΚΑΑ;",
                    "answer": "H Ευρωπαϊκή Κάρτα Ασφάλισης Ασθένειας (ΕΚΑΑ) είναι μια δωρεάν κάρτα που σας προσφέρει πρόσβαση σε ιατρικά αναγκαίες, κρατικές περιθάλψεις κατά την προσωρινή διαμονή σας σε οποιαδήποτε από τις 27 χώρες της ΕΕ, την Ισλανδία, το Λιχτενστάιν, τη Νορβηγία, την Ελβετία και το Ηνωμένο Βασίλειο, με τους ίδιους όρους και το ίδιο κόστος (σε ορισμένες χώρες, δωρεάν) με τους ασφαλισμένους των εν λόγω χωρών."
                }
            ]
        }

# Load the FAQ data
faq_data = load_faq_data()

def clean_text(text):
    """Clean and normalize text for better matching."""
    if not text:
        return ""
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove punctuation and extra spaces
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def similarity_ratio(a, b):
    """Calculate similarity ratio between two strings."""
    return SequenceMatcher(None, a, b).ratio()

def find_best_match(user_question):
    """Find the best matching question in the FAQ data."""
    if not user_question:
        return None
    
    cleaned_question = clean_text(user_question)
    
    best_match = None
    best_score = 0
    
    for faq in faq_data.get("faqs", []):
        cleaned_faq_question = clean_text(faq.get("question", ""))
        
        # Calculate similarity score
        score = similarity_ratio(cleaned_question, cleaned_faq_question)
        
        # Check for keyword matches to improve matching
        for word in cleaned_question.split():
            if word and len(word) > 3 and word in cleaned_faq_question:
                score += 0.1  # Boost score for keyword matches
        
        if score > best_score:
            best_score = score
            best_match = faq
    
    # Only return a match if the score is above a threshold
    if best_score >= 0.3:
        logger.debug(f"Best match found with score {best_score}")
        return best_match
    
    return None

def process_question(user_question):
    """Process user question and return the appropriate answer."""
    try:
        logger.debug(f"Processing question: {user_question}")
        
        # Find best matching FAQ
        best_match = find_best_match(user_question)
        
        if best_match:
            return best_match.get("answer", "")
        else:
            return "Συγγνώμη, δεν μπορώ να βρω μια απάντηση στην ερώτησή σας. Παρακαλώ δοκιμάστε να διατυπώσετε την ερώτησή σας διαφορετικά ή ρωτήστε κάτι άλλο σχετικά με την ΕΚΑΑ (Ευρωπαϊκή Κάρτα Ασφάλισης Ασθένειας)."
            # Sorry, I can't find an answer to your question. Please try rewording your question or ask something else about EHIC.
    except Exception as e:
        logger.error(f"Error in process_question: {str(e)}")
        return "Παρουσιάστηκε σφάλμα κατά την επεξεργασία της ερώτησής σας. Παρακαλώ δοκιμάστε ξανά."
        # An error occurred while processing your question. Please try again.
