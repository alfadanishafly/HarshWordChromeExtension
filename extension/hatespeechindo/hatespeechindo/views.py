from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import nltk
import requests
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import logging
import nltk
import requests
import re
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer

logger = logging.getLogger(__name__)

@csrf_exempt
def check_hatespeech(request):
    if request.method == 'POST':
        # Extract the raw request body
        raw_body = request.body.decode('utf-8')

        # Print the raw request body
        print("request.body:", raw_body)

        # Use machine learning model to check for hate speech words
        is_hatespeech = check_with_machine_learning(raw_body)
        logger.info("is_hatespeech: %s", is_hatespeech)

        # Return JSON response with the checking result
        return JsonResponse({'is_hatespeech': is_hatespeech})

    # Return error response if there is an issue with the request
    return JsonResponse({'error': 'Invalid request'})


def check_with_machine_learning(text):
    # Load the model from the model.pkl file
    model = joblib.load('Hate Speech Classifier.joblib')
    vectorize_model = joblib.load('Hate Speech TF-IDF Vectorizer.joblib')

    # Preprocess the text
    processed_text = preprocess_text(text)
    logger.info("Processed Text: %s", processed_text)
    print("Processed Text:", processed_text)

    # Vectorize the text
    vectorized_text = vectorize_model.transform([processed_text])

    # Perform prediction using the model
    prediction = model.predict(vectorized_text)
    logger.info("Prediction: %s", prediction)
    print("Prediction:", prediction)

    # If the prediction indicates hate speech words, return True; otherwise, return False
    return bool(prediction[0])


def preprocess_text(text):
    # Remove special characters except spaces, numbers, and alphabets
    processed_text = re.sub(r'[^a-zA-Z0-9\s]', '', text)

    # Tokenize the text
    tokens = word_tokenize(processed_text)

    # Remove stopwords
    stop_words = set(stopwords.words('indonesian'))
    filtered_tokens = [word for word in tokens if word.lower() not in stop_words]

    # Convert all words to lowercase
    lowercase_tokens = [word.lower() for word in filtered_tokens]

    # Join the processed tokens back into text
    processed_text = ' '.join(lowercase_tokens)

    return processed_text
