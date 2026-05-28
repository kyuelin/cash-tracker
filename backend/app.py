from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import os
from datetime import datetime
from collections import defaultdict

app = Flask(__name__, static_folder='../frontend/build', static_url_path='')
CORS(app)

# Data file paths
TRANSACTIONS_FILE = os.getenv('TRANSACTIONS_FILE', 'transactions.json')
CATEGORIES_FILE = os.getenv('CATEGORIES_FILE', 'data/categories.json')

def _transaction_date(value):
    return value.get('transaction_date') or value.get('date') or ''

def _normalize_transaction(value):
    tx_date = _transaction_date(value)
    return {
        'id': value.get('id'),
        'transaction_date': tx_date,
        'date': tx_date,
        'description': value.get('description'),
        'category': value.get('category'),
        'amount': value.get('amount')
    }

def ensure_data_directory():
    """Ensure data directory and files exist"""
    os.makedirs('data', exist_ok=True)
    
    if not os.path.exists(TRANSACTIONS_FILE):
        with open(TRANSACTIONS_FILE, 'w') as f:
            json.dump({"transactions": [], "cash_received": []}, f)
    
    if not os.path.exists(CATEGORIES_FILE):
        default_categories = {
            "categories": [
                "Food & Dining", "Groceries", "Transportation", "Shopping",
                "Entertainment", "Bills & Utilities", "Healthcare", "Education",
                "Travel", "Personal Care", "Gifts & Donations", "Other"
            ],
            "descriptions": []
        }
        with open(CATEGORIES_FILE, 'w') as f:
            json.dump(default_categories, f)

def load_data():
    """Load transaction and category data"""
    ensure_data_directory()
    
    with open(TRANSACTIONS_FILE, 'r') as f:
        transactions_data = json.load(f)
    
    # Filter transactions to include only specified fields
    if 'transactions' in transactions_data:
        transactions_data['transactions'] = [_normalize_transaction(t) for t in transactions_data['transactions']]
    
    with open(CATEGORIES_FILE, 'r') as f:
        categories_data = json.load(f)
    
    return transactions_data, categories_data

def save_transactions(data):
    """Save transaction data to file"""
    with open(TRANSACTIONS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def save_categories(data):
    """Save category data to file"""
    with open(CATEGORIES_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def suggest_category(description, categories_data):
    """Suggest category based on description keywords"""
    description_lower = description.lower()
    
    # Define keyword mappings
    category_keywords = {
        "Food & Dining": ["restaurant", "coffee", "lunch", "dinner", "cafe", "food", "eat", "meal"],
        "Groceries": ["grocery", "supermarket", "market", "vegetables", "fruits", "milk", "bread"],
        "Transportation": ["gas", "fuel", "parking", "bus", "taxi", "uber", "lyft", "train", "metro"],
        "Shopping": ["store", "mall", "clothes", "shoes", "online", "amazon", "shopping"],
        "Entertainment": ["movie", "cinema", "game", "music", "concert", "theater", "fun"],
        "Bills & Utilities": ["electricity", "water", "internet", "phone", "bill", "utility"],
        "Healthcare": ["pharmacy", "doctor", "hospital", "medicine", "health", "medical"],
        "Education": ["book", "course", "school", "university", "education", "learn"],
        "Travel": ["hotel", "flight", "vacation", "trip", "travel", "tourism"],
        "Personal Care": ["haircut", "salon", "cosmetics", "personal", "beauty", "care"]
    }
    
    # Score each category
    scores = defaultdict(int)
    for category, keywords in category_keywords.items():
        for keyword in keywords:
            if keyword in description_lower:
                scores[category] += 1
    
    # Return the category with the highest score, or "Other" if no match
    if scores:
        return max(scores.items(), key=lambda x: x[1])[0]
    return "Other"

def calculate_balance(transactions_data, target_month=None):
    """Calculate running balance"""
    total_received = sum(item['amount'] for item in transactions_data.get('cash_received', []))
    total_spent = sum(t['amount'] for t in transactions_data.get('transactions', []))
    
    if target_month:
        month_spent = sum(
            t['amount'] for t in transactions_data.get('transactions', [])
            if _transaction_date(t).startswith(target_month)
        )
        month_received = sum(
            item['amount'] for item in transactions_data.get('cash_received', [])
            if _transaction_date(item).startswith(target_month)
        )
        return {
            'monthly_balance': month_received - month_spent,
            'total_balance': total_received - total_spent,
            'monthly_spent': month_spent,
            'monthly_received': month_received
        }
    
    return {
        'total_balance': total_received - total_spent,
        'total_received': total_received,
        'total_spent': total_spent
    }

@app.route('/')
def serve():
    """Serve the React app"""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/transactions', methods=['GET'])
def get_transactions():
    """Get all transactions with pagination and filtering"""
    transactions_data, _ = load_data()
    
    # Get query parameters
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))
    category_filter = request.args.get('category', '')
    search = request.args.get('search', '')
    sort_by = request.args.get('sort_by', 'transaction_date')
    sort_order = request.args.get('sort_order', 'desc')
    
    transactions = transactions_data.get('transactions', [])
    
    # Apply filters
    if category_filter:
        transactions = [t for t in transactions if t['category'] == category_filter]
    
    if search:
        search_lower = search.lower()
        transactions = [
            t for t in transactions 
            if search_lower in t['description'].lower()
        ]
    
    # Sort transactions
    reverse = sort_order == 'desc'
    if sort_by in ('transaction_date', 'date'):
        transactions.sort(key=lambda x: _transaction_date(x), reverse=reverse)
    elif sort_by == 'amount':
        transactions.sort(key=lambda x: x['amount'], reverse=reverse)
    elif sort_by == 'category':
        transactions.sort(key=lambda x: x['category'], reverse=reverse)
    elif sort_by == 'description':
        transactions.sort(key=lambda x: x['description'], reverse=reverse)
    
    # Paginate
    total = len(transactions)
    start = (page - 1) * limit
    end = start + limit
    paginated_transactions = transactions[start:end]
    
    return jsonify({
        'transactions': paginated_transactions,
        'total': total,
        'page': page,
        'limit': limit,
        'pages': (total + limit - 1) // limit
    })

@app.route('/api/transactions', methods=['POST'])
def add_transaction():
    """Add a new transaction"""
    data = request.get_json()
    
    transactions_data, categories_data = load_data()
    
    tx_date = data.get('transaction_date') or data.get('date')
    if not tx_date:
        return jsonify({'error': 'transaction_date (or date) is required'}), 400

    # Create transaction
    transaction = {
        'id': len(transactions_data.get('transactions', [])) + 1,
        'transaction_date': tx_date,
        'date': tx_date,
        'description': data['description'],
        'category': data['category'],
        'amount': float(data['amount'])
    }
    
    transactions_data.setdefault('transactions', []).append(transaction)
    save_transactions(transactions_data)
    
    # Update descriptions for autocomplete
    if data['description'] not in categories_data.get('descriptions', []):
        categories_data.setdefault('descriptions', []).append(data['description'])
        save_categories(categories_data)
    
    # Calculate updated balance
    current_month = datetime.now().strftime('%Y-%m')
    balance = calculate_balance(transactions_data, current_month)
    
    return jsonify({
        'transaction': transaction,
        'balance': balance
    })

@app.route('/api/cash-received', methods=['POST'])
def add_cash_received():
    """Add cash received entry"""
    data = request.get_json()
    
    transactions_data, _ = load_data()

    tx_date = data.get('transaction_date') or data.get('date')
    if not tx_date:
        return jsonify({'error': 'transaction_date (or date) is required'}), 400
    
    cash_entry = {
        'id': len(transactions_data.get('cash_received', [])) + 1,
        'transaction_date': tx_date,
        'date': tx_date,
        'description': data.get('description', 'Cash received'),
        'amount': float(data['amount'])
    }
    
    transactions_data.setdefault('cash_received', []).append(cash_entry)
    save_transactions(transactions_data)
    
    # Calculate updated balance
    current_month = datetime.now().strftime('%Y-%m')
    balance = calculate_balance(transactions_data, current_month)
    
    return jsonify({
        'cash_entry': cash_entry,
        'balance': balance
    })

@app.route('/api/categories', methods=['GET'])
def get_categories():
    """Get all categories"""
    _, categories_data = load_data()
    return jsonify(categories_data)

@app.route('/api/suggestions/category', methods=['POST'])
def suggest_category_endpoint():
    """Suggest category based on description"""
    data = request.get_json()
    description = data.get('description', '')
    
    _, categories_data = load_data()
    suggested_category = suggest_category(description, categories_data)
    
    return jsonify({'suggested_category': suggested_category})

@app.route('/api/suggestions/description', methods=['GET'])
def get_description_suggestions():
    """Get description suggestions for autocomplete"""
    query = request.args.get('query', '').lower()
    
    _, categories_data = load_data()
    descriptions = categories_data.get('descriptions', [])
    
    # Filter descriptions that contain the query
    suggestions = [
        desc for desc in descriptions 
        if query in desc.lower()
    ][:10]  # Limit to 10 suggestions
    
    return jsonify({'suggestions': suggestions})

@app.route('/api/balance', methods=['GET'])
def get_balance():
    """Get current balance"""
    month = request.args.get('month')
    transactions_data, _ = load_data()
    
    if month:
        balance = calculate_balance(transactions_data, month)
    else:
        current_month = datetime.now().strftime('%Y-%m')
        balance = calculate_balance(transactions_data, current_month)
    
    return jsonify(balance)

@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    """Get analytics data for charts"""
    month = request.args.get('month')
    transactions_data, _ = load_data()
    
    transactions = transactions_data.get('transactions', [])
    
    # Filter by month if specified
    if month and month != 'all':
        transactions = [t for t in transactions if _transaction_date(t).startswith(month)]
    
    # Group by category
    category_totals = defaultdict(float)
    for transaction in transactions:
        category_totals[transaction['category']] += transaction['amount']
    
    # Convert to list for chart
    chart_data = [
        {'category': category, 'amount': amount}
        for category, amount in category_totals.items()
    ]
    
    # Sort by amount descending
    chart_data.sort(key=lambda x: x['amount'], reverse=True)
    
    return jsonify({'data': chart_data})

@app.route('/health', methods=['GET'])
def health_check():
    # You can add checks for database connectivity, external services, etc.
    try:
        # Example: check database connection
        # db.session.execute('SELECT 1')

        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '1.0.0'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 503

if __name__ == '__main__':
    ensure_data_directory()
    app.run(
        debug=os.getenv('FLASK_DEBUG', 'false').lower() == 'true',
        host='0.0.0.0',
        port=int(os.getenv('PORT', '5001'))
    )
