from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash
import bcrypt
import jwt
import datetime
import stripe
from models import users_collection
from models import payments_collection
from utils import send_verification_email

auth_routes = Blueprint('auth', __name__)
payment_routes = Blueprint('payment', __name__)

stripe.api_key = "sk_test_51Q5MiGFZyG5NjtIFu8fzbR6EpALN1Bnms3m33MPsSFRCjr1gbIiMxXSvn95mKRkT0mevP73KIuAWc0PKZk2pO8h600h9xHtUnB"

@auth_routes.route('/register', methods=['POST'])
def register():
    data = request.json
    email = data['email']
    password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    if users_collection.find_one({"email": email}):
        return jsonify({"message": "User already exists."})
    
    print(data)
    users_collection.insert_one({"email": email, "password": password, "verified": True})
    return jsonify({"message": "User registered successfully. Please check your email to verify."}), 201

@auth_routes.route('/verify/<token>', methods=['GET'])
def verify_email(token):
    try:
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        users_collection.update_one({"email": data['email']}, {"$set": {"verified": True}})
        return jsonify({"message": "Email verified successfully."}), 200
    except jwt.ExpiredSignatureError:
        return jsonify({"message": "Token expired."}), 400
    except jwt.InvalidTokenError:
        return jsonify({"message": "Invalid token."}), 400

@auth_routes.route('/login', methods=['POST'])
def login():
    data = request.json
    user = users_collection.find_one({"email": data['email']})
    if not user or not bcrypt.checkpw(data['password'].encode('utf-8'), user['password'].encode('utf-8')):
        return jsonify({"message": "Invalid credentials."})
    
    if not user['verified']:
        return jsonify({"message": "Email not verified."})
    
    print(data)
    token = jwt.encode({"email": user['email'], "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)}, 'SECRET_KEY')
    return jsonify({"success": "Login Ok","token": token}), 200

@payment_routes.route('/create-payment-link', methods=['POST'])
def create_payment_link():
    try:
        data = request.json
        amount = data['amount']  
        currency = data['currency']
        description = data['description']
        if currency == "eur":
            set_currency = "price_1Q6C6CFZyG5NjtIFDtyAm05s"
        elif currency == "usd": 
           set_currency = "price_1Q686uFZyG5NjtIFp5zgCdKT"
        print(set_currency, currency)
        payment_link = stripe.PaymentLink.create(
            line_items=[{
                "price": set_currency,
                "quantity": amount,
            }],
            metadata={"currency": currency}
        )
        return jsonify({'url': payment_link.url}), 201

    except Exception as e:
        return jsonify({'error': str(e)})

@payment_routes.route('/webhook', methods=['POST'])
def stripe_webhook():
    print("------------Test--------->>>>>>>>")
    payload = request.get_data(as_text=True)
    sig = request.headers.get('Stripe-Signature')

    try:
        event = stripe.Webhook.construct_event(payload, sig, "whsec_vSssrxTPv8HT4WjLef7oSFgt27lwNqSc")
    except ValueError as e:
        print(f"Invalid payload: {e}")
        return jsonify({'error': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError as e:
        print(f"Invalid signature: {e}")
        return jsonify({'error': 'Invalid signature'}), 400

    if event['type'] == 'payment_intent.succeeded':
        handle_payment_success(event['data']['object'])
    elif event['type'] == 'payment_intent.processing':
        handle_payment_pending(event['data']['object'])
    elif event['type'] == 'payment_intent.payment_failed':
        handle_payment_failure(event['data']['object'])
    else:
        print(f"Unhandled event type {event['type']}")

    return jsonify({'status': 'success'}), 200

def handle_payment_success(payment_intent):
    print('Payment succeeded:', payment_intent)

    amount = payment_intent['amount']/100
    currency = payment_intent['currency']
    description = payment_intent['description']

    if description is None:
        description = "this is a test" 

    status = payment_intent['status']
    payment_method = payment_intent['payment_method_types']
    payment_method = payment_method[0]

    payment_id = payment_intent['id']
    pay_id = payments_collection.find_one({"payment_id": payment_id})
    if pay_id:
        result = payments_collection.update_one(
            {'payment_id': payment_id},  
            {'$set': {'status': status}}
        )
        print(result)
    else: 
        print(amount,payment_method, currency)
        payments_collection.insert_one({
            "amount": amount,
            "currency": currency,
            "description": description,
            "currency": currency,
            "status": status,
            "payment_method": payment_method,
            "createdAt": datetime.datetime.now(),
            "payment_id": payment_id
        })

def handle_payment_pending(payment_intent):
    print('Payment pending:', payment_intent)
    amount = payment_intent['amount']/100
    currency = payment_intent['currency']
    description = payment_intent['description']

    if description is None:
        description = "this is a test" 

    status = payment_intent['status']
    payment_method = payment_intent['payment_method_types']
    payment_method = payment_method[0]

    payment_id = payment_intent['id']
    pay_id = payments_collection.find_one({"payment_id": payment_id})

    if pay_id:
        result = payments_collection.update_one(
            {'payment_id': payment_id},
            {'$set': {'status': status}}
        )
        print(result)
    else: 
        payments_collection.insert_one({
            "amount": amount,
            "currency": currency,
            "description": description,
            "currency": currency,
            "status": status,
            "payment_method": payment_method,
            "createdAt": datetime.datetime.now(),
            "payment_id": payment_id
        })
    
def handle_payment_failure(payment_intent):
    print('Payment failed:', payment_intent)
    amount = payment_intent['amount']/100
    currency = payment_intent['currency']
    description = payment_intent['description']

    if description is None:
        description = "this is a test" 

    status = payment_intent['status']
    payment_method = payment_intent['payment_method_types']
    payment_method = payment_method[0]

    payment_id = payment_intent['id']
    pay_id = payments_collection.find_one({"payment_id": payment_id})
    if pay_id:
        result = payments_collection.update_one(
            {'payment_id': payment_id},
            {'$set': {'status': status}}
        )
        print(result)
    else: 
        payments_collection.insert_one({
            "amount": amount,
            "currency": currency,
            "description": description,
            "currency": currency,
            "status": status,
            "payment_method": payment_method,
            "createdAt": datetime.datetime.now(),
            "payment_id": payment_id
        })
@payment_routes.route('/analytics', methods=['POST'])
def analytics():
    payments = payments_collection.find()
    payments_data = []

    data = request.json
    date = data.get('date')
    amount = data.get('amount')
    currency = data.get('currency')

    for index, payment in enumerate(payments, start = 1 ):
        payment['id'] = index 
        payment['_id'] = str(payment['_id'])

        if 'createdAt' in payment:
            payment['date'] = payment['createdAt'].strftime("%Y-%m-%d")
            del payment['createdAt']
            print(payment['date'])

        payments_data.append(payment)

    filtered_payments = payments_data

    filters = {
        'date': date,
        'amount': amount,
        'currency': currency
    }
    non_empty_filters = {k: v for k, v in filters.items() if v is not None and v != ''}
    print(len(non_empty_filters))
    if len(non_empty_filters) == 0:
        filtered_payments = payments_data

    elif len(non_empty_filters) == 1:
        if date:
            try:
                date = datetime.datetime.fromisoformat(date)
                filtered_payments = [p for p in payments_data if datetime.datetime.fromisoformat(p['date']) >= date]
            except ValueError:
                return jsonify({"error": "Invalid date format"})
        elif amount:
            try:
                amount = int(amount)
                filtered_payments = [p for p in payments_data if p['amount'] >= amount]
            except ValueError:
                return jsonify({"error": "Invalid amount format"})
        elif currency:
            print(currency)
            filtered_payments = [p for p in payments_data if p['currency'] == currency]

    elif len(non_empty_filters) == 2:
        if date and amount:
            try:
                date = datetime.datetime.fromisoformat(date)
                amount = int(amount)
                filtered_payments = [p for p in payments_data if datetime.datetime.fromisoformat(p['date']) >= date and p['amount'] >= amount]
            except ValueError:
                return jsonify({"error": "Invalid date or amount format"})
        elif date and currency:
            try:
                date = datetime.datetime.fromisoformat(date)
                filtered_payments = [p for p in payments_data if datetime.datetime.fromisoformat(p['date']) >= date and p['currency'] == currency]
            except ValueError:
                return jsonify({"error": "Invalid date format"})
        elif amount is not None and currency:
            try:
                amount = int(amount)
                filtered_payments = [p for p in payments_data if p['amount'] >= amount and p['currency'] == currency]
            except ValueError:
                return jsonify({"error": "Invalid amount format"})
            
    else:
        try:
            if date:
                date = datetime.datetime.fromisoformat(date)
                filtered_payments = [p for p in filtered_payments if datetime.datetime.fromisoformat(p['date']) >= date]
            if amount is not None:
                amount = int(amount)
                filtered_payments = [p for p in filtered_payments if p['amount'] >= amount]
            if currency:
                filtered_payments = [p for p in filtered_payments if p['currency'] == currency]
        except ValueError:
            return jsonify({"error": "Invalid input format"})


    total_payments = len(filtered_payments)
    total_amount = sum(p['amount'] for p in filtered_payments)
    success_count = sum(1 for p in filtered_payments if p['status'] == 'success')
    pending_count = sum(1 for p in filtered_payments if p['status'] == 'pending')
    failure_count = sum(1 for p in filtered_payments if p['status'] == 'failure')

    analytics_summary = {
        'total_payments': total_payments,
        'total_amount': total_amount,
        'success_count': success_count,
        'pending_count': pending_count,
        'failure_count': failure_count,
        'payments': filtered_payments
    }

    return jsonify(analytics_summary), 200
