import os

class Config(object):
    SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key")
    MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://tombrain1011:icdO8YDs9E8HOoBJ@cluster0.uso4lqs.mongodb.net/Emily?retryWrites=true&w=majority&appName=Cluster0")
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = "noreply@flask.com"
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_DEBUG = True
    STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "sk_test_...")  # Add your Stripe secret key
