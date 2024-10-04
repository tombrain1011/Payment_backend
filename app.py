from flask import Flask
from flask_cors import CORS
from routes import auth_routes, payment_routes
from config import Config
from flask_mail import Mail 

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)
mail = Mail(app)

app.register_blueprint(auth_routes)
app.register_blueprint(payment_routes)

if __name__ == '__main__':
    app.run(debug=True)
