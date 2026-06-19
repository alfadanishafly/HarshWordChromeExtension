# Hate Speech Detection Chrome Extension

A Chrome extension that detects and censors hate speech on web pages using machine learning. The extension consists of a Django backend API and a Chrome extension frontend.

## Architecture

- **Backend**: Django REST API with ML-based hate speech classification
- **Frontend**: Chrome Extension (Manifest V3) that intercepts and processes web page content

## Prerequisites

- Python 3.8+
- Google Chrome or Chromium browser
- Node.js (optional, for development)

## Installation

### 1. Backend Setup (Django API)

```bash
cd extension/hatespeechindo

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Run migrations
python manage.py migrate

# Start the server
python manage.py runserver
```

The API will be available at `http://localhost:8000`

### 2. Chrome Extension Setup

1. Open Chrome and navigate to `chrome://extensions/`
2. Enable "Developer mode" (toggle in top right)
3. Click "Load unpacked"
4. Select the `extension` folder
5. The extension icon should appear in your toolbar

## Configuration

### Environment Variables

Create a `.env` file in `extension/hatespeechindo/` with the following variables:

```bash
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
DJANGO_CORS_ORIGINS=http://localhost:8000
DJANGO_LOG_LEVEL=INFO
```

### Model Files

Ensure the following model files are present in the `extension/` directory:
- `Hate Speech Classifier.joblib` - Trained classification model
- `Hate Speech TF-IDF Vectorizer.joblib` - Text vectorization model

## Usage

1. Start the Django backend server
2. Load the Chrome extension
3. Browse any website - the extension will automatically:
   - Extract text content from the page
   - Send it to the hate speech detection API
   - Censor detected hate speech content
   - Show notifications when hate speech is found

## Project Structure

```
/workspace
├── README.md
└── extension/
    ├── manifest.json          # Chrome extension configuration
    ├── background.js          # Extension background service worker
    ├── content.js             # Content script for page processing
    ├── api.py                 # Legacy API module (deprecated)
    ├── *.joblib               # ML model files
    └── hatespeechindo/        # Django project
        ├── manage.py
        ├── requirements.txt
        ├── .env.example
        └── hatespeechindo/
            ├── settings.py    # Django settings
            ├── urls.py        # URL routing
            └── views.py       # API endpoints
```

## API Endpoints

### POST /api/check_hatespeech/

Check if text contains hate speech.

**Request:**
```json
{
  "text": "Your text to analyze"
}
```

**Response:**
```json
{
  "is_hatespeech": true
}
```

## Development Notes

### Code Improvements Made

1. **Security**: 
   - Removed hardcoded secrets (use environment variables)
   - Added proper CORS configuration
   - Improved error handling

2. **Code Quality**:
   - Added docstrings and type hints
   - Removed duplicate code
   - Fixed hardcoded Windows paths
   - Proper logging configuration

3. **Chrome Extension**:
   - Updated to Manifest V3 (latest standard)
   - Removed blocking all web requests (was breaking browsing)
   - Added proper async/await patterns
   - Better error handling

4. **Maintainability**:
   - Centralized configuration in settings.py
   - Separated concerns between modules
   - Added requirements.txt for dependency management

## Troubleshooting

### Extension not working?
1. Check that the Django server is running on port 8000
2. Verify the extension is loaded in `chrome://extensions/`
3. Check the browser console (F12) for errors

### API errors?
1. Ensure model files exist in the correct location
2. Check `api_logs.log` for detailed error messages
3. Verify NLTK data is downloaded (runs automatically on first use)

## License

This project is for educational purposes.

## Contributing

Feel free to submit issues and enhancement requests!
