import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    GROQ_API_KEY = os.environ.get('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') or 'your-actual-groq-api-key-here'  # Set your Groq API key here