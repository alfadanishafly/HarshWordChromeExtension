"""
Hate Speech Detection API Views

This module provides endpoints for hate speech detection using machine learning models.
"""
import json
import logging
import os
from pathlib import Path

import joblib
import nltk
import re
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

logger = logging.getLogger(__name__)

# Ensure NLTK data is downloaded
try:
    stopwords.words('indonesian')
except LookupError:
    nltk.download('stopwords', quiet=True)
    nltk.download('punkt', quiet=True)


@csrf_exempt
def check_hatespeech(request):
    """
    Check if the provided text contains hate speech.
    
    Args:
        request: Django HTTP request object
        
    Returns:
        JsonResponse with 'is_hatespeech' boolean or error message
    """
    if request.method == 'POST':
        try:
            # Try to parse JSON body first (for Chrome extension compatibility)
            try:
                request_data = json.loads(request.body.decode('utf-8'))
                text = request_data.get('text', '')
            except (json.JSONDecodeError, UnicodeDecodeError):
                # Fallback to form data
                text = request.POST.get('text', '')
            
            if not text:
                return JsonResponse({'error': 'No text provided'}, status=400)
            
            # Use machine learning model to check for hate speech
            is_hatespeech = check_with_machine_learning(text)
            logger.info("Hate speech detection result: %s", is_hatespeech)
            
            return JsonResponse({'is_hatespeech': is_hatespeech})
            
        except Exception as e:
            logger.error("Error processing hate speech detection: %s", str(e))
            return JsonResponse({'error': f'Processing error: {str(e)}'}, status=500)
    
    return JsonResponse({'error': 'Invalid request method. Use POST.'}, status=405)


def check_with_machine_learning(text):
    """
    Load ML models and predict if text contains hate speech.
    
    Args:
        text: Input text to analyze
        
    Returns:
        bool: True if hate speech detected, False otherwise
    """
    try:
        # Load models using paths from settings
        model_path = getattr(settings, 'MODEL_PATH', None)
        vectorizer_path = getattr(settings, 'VECTORIZER_PATH', None)
        
        if not model_path or not vectorizer_path:
            # Fallback to default paths in BASE_DIR
            base_dir = settings.BASE_DIR
            model_path = base_dir / 'Hate Speech Classifier.joblib'
            vectorizer_path = base_dir / 'Hate Speech TF-IDF Vectorizer.joblib'
        
        model = joblib.load(model_path)
        vectorizer = joblib.load(vectorizer_path)
        
        # Preprocess the text
        processed_text = preprocess_text(text)
        logger.debug("Processed text: %s", processed_text)
        
        # Vectorize and predict
        vectorized_text = vectorizer.transform([processed_text])
        prediction = model.predict(vectorized_text)
        
        logger.debug("Prediction: %s", prediction)
        return bool(prediction[0])
        
    except FileNotFoundError as e:
        logger.error("Model file not found: %s", str(e))
        raise
    except Exception as e:
        logger.error("Prediction error: %s", str(e))
        raise


def preprocess_text(text):
    """
    Clean and preprocess text for ML model input.
    
    Args:
        text: Raw input text
        
    Returns:
        str: Processed and cleaned text
    """
    # Remove special characters except spaces, numbers, and alphabets
    processed_text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    
    # Tokenize
    tokens = word_tokenize(processed_text)
    
    # Remove Indonesian stopwords
    stop_words = set(stopwords.words('indonesian'))
    filtered_tokens = [word for word in tokens if word.lower() not in stop_words]
    
    # Convert to lowercase
    lowercase_tokens = [word.lower() for word in filtered_tokens]
    
    # Join back into text
    return ' '.join(lowercase_tokens)
