"""Test Gemini API connection and model response. Run: python scripts/test_gemini.py"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from dotenv import load_dotenv

load_dotenv()

from app import create_app
from app.ai.gemini_service import generate_text, FALLBACK_MODELS


def main():
    app = create_app()
    with app.app_context():
        key = app.config.get('GEMINI_API_KEY')
        model = app.config.get('GEMINI_MODEL', 'gemini-2.5-flash')
        print(f'API key configured: {bool(key)}')
        print(f'Configured model: {model}')
        print(f'Fallback models: {", ".join(FALLBACK_MODELS)}')
        print('-' * 50)

        response, error = generate_text('Reply with exactly one word: Working')
        if error:
            print('FAILED:', error)
            sys.exit(1)
        print('SUCCESS:', response)
        print('-' * 50)
        print('Gemini AI is working correctly.')


if __name__ == '__main__':
    main()
