from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import nltk
import pickle
import requests
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import logging

logger = logging.getLogger(__name__)

@csrf_exempt
def check_hatespeech(request):
    if request.method == 'POST':
        data = request.POST.get('text', '')

        # Gunakan model machine learning untuk memeriksa kata-kata hatespeech
        is_hatespeech = check_with_machine_learning(data)
        logger.info("is_hatespeech: %s", is_hatespeech)

        # Mengembalikan respons JSON dengan hasil pemeriksaan
        return JsonResponse({'is_hatespeech': is_hatespeech})

    # Mengembalikan respons error jika ada masalah dalam permintaan
    return JsonResponse({'error': 'Invalid request'})

def check_with_machine_learning(text):
    # Muat model dari file model.pkl
    with open('model.pkl', 'rb') as f:
        model = pickle.load(f)

    # Preprocessing teks
    processed_text = preprocess_text(text)
    logger.info("Processed Text: %s", processed_text)

    # Lakukan prediksi menggunakan model
    prediction = model.predict([processed_text])
    logger.info("Prediction: %s", prediction)

    # Jika prediksi menunjukkan kata-kata sebagai hatespeech, kembalikan True, jika tidak kembalikan False
    return bool(prediction[0])

def preprocess_text(text):
    # Tokenisasi teks menjadi kata-kata
    tokens = word_tokenize(text)

    # Menghapus stopwords
    stop_words = set(stopwords.words('indonesian'))
    filtered_tokens = [word for word in tokens if word.lower() not in stop_words]

    # Mengubah semua kata menjadi lowercase
    lowercase_tokens = [word.lower() for word in filtered_tokens]

    # Menangani kata slang (jika diperlukan)
    processed_tokens = replace_slang(lowercase_tokens)

    # Menggabungkan kata-kata menjadi teks yang sudah diproses
    processed_text = ' '.join(processed_tokens)

    return processed_text

def replace_slang(tokens):
    # Mengambil kamus kata slang dari URL
    response = requests.get('https://raw.githubusercontent.com/louisowen6/NLP_bahasa_resources/master/combined_slang_words.txt')
    slang_dict = {}

    if response.status_code == 200:
        slang_lines = response.text.split('\n')
        for line in slang_lines:
            if line:
                slang_word, expanded_word = line.split(':')
                slang_dict[slang_word] = expanded_word.strip()

    processed_tokens = []
    for token in tokens:
        if token in slang_dict:
            processed_tokens.append(slang_dict[token])
        else:
            processed_tokens.append(token)

    return processed_tokens
