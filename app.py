import os
import logging
from flask import Flask, render_template, request, jsonify
from nlp_processor import process_question

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "ehic-faq-chatbot-secret")

@app.route('/')
def index():
    """Render the main page of the chatbot."""
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    """Process user questions and return answers."""
    try:
        user_question = request.form.get('question', '')
        logger.debug(f"Received question: {user_question}")
        
        if not user_question:
            return jsonify({
                'status': 'error',
                'message': 'Παρακαλώ εισάγετε μια ερώτηση.'  # Please enter a question
            }), 400
        
        answer = process_question(user_question)
        
        return jsonify({
            'status': 'success',
            'answer': answer
        })
    except Exception as e:
        logger.error(f"Error processing question: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Παρουσιάστηκε σφάλμα κατά την επεξεργασία της ερώτησής σας. Παρακαλώ δοκιμάστε ξανά.'
            # An error occurred while processing your question. Please try again.
        }), 500

@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors."""
    return render_template('index.html'), 404

@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors."""
    logger.error(f"Server error: {str(e)}")
    return render_template('index.html'), 500
