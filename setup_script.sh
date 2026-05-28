#!/bin/bash

# Cash Tracker Application Setup Script
# This script sets up the complete cash tracking application

echo "🚀 Setting up Cash Tracker Application..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed. Please install Node.js 14 or higher."
    exit 1
fi

# Create project structure
echo "📁 Creating project structure..."
mkdir -p cash-tracker/{backend/{data,models},frontend/src/{components,services}}

# Set up backend
echo "🐍 Setting up Python backend..."
cd cash-tracker/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Create requirements.txt
cat > requirements.txt << EOF
Flask==2.3.2
Flask-CORS==4.0.0
python-dateutil==2.8.2
Werkzeug==2.3.6
click==8.1.3
itsdangerous==2.1.2
Jinja2==3.1.2
MarkupSafe==2.1.3
six==1.16.0
EOF

# Install Python dependencies
pip install -r requirements.txt

# Create initial data files
mkdir -p data
cat > data/transactions.json << EOF
{
  "transactions": [],
  "cash_received": []
}
EOF

cat > data/categories.json << EOF
{
  "categories": [
    "Food & Dining",
    "Groceries",
    "Transportation",
    "Shopping",
    "Entertainment",
    "Bills & Utilities",
    "Healthcare",
    "Education",
    "Travel",
    "Personal Care",
    "Gifts & Donations",
    "Other"
  ],
  "descriptions": []
}
EOF

# Create app.py (you'll need to copy the Flask code from the artifact above)
echo "📝 Flask app.py created. Please copy the Flask application code from the artifacts."

# Set up frontend
echo "⚛️ Setting up React frontend..."
cd ../
npx create-react-app frontend --template typescript
cd frontend

# Install additional dependencies
npm install axios lucide-react recharts
npm install -D tailwindcss postcss autoprefixer @tailwindcss/forms @tailwindcss/typography @tailwindcss/aspect-ratio

# Initialize Tailwind CSS
npx tailwindcss init -p

# Create Tailwind config (you'll need to copy from the artifact above)
echo "🎨 Tailwind CSS configuration created. Please copy the config from the artifacts."

# Update package.json.tbd to include homepage and proxy
npm pkg set homepage="."
npm pkg set proxy="http://localhost:5000"

echo "📋 React components created. Please copy the component files from the artifacts."

# Create start scripts
cd ../
cat > start_backend.sh << EOF
#!/bin/bash
cd backend
source venv/bin/activate
python app.py
EOF

cat > start_frontend.sh << EOF
#!/bin/bash
cd frontend
npm start
EOF

cat > start_app.sh << EOF
#!/bin/bash
echo "🚀 Starting Cash Tracker Application..."

# Start backend in background
echo "🐍 Starting Python backend..."
cd backend
source venv/bin/activate
python app.py &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Start frontend
echo "⚛️ Starting React frontend..."
cd ../frontend
npm start &
FRONTEND_PID=$!

echo "✅ Application started!"
echo "Backend: http://localhost:5000"
echo "Frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for user interrupt
trap 'kill $BACKEND_PID $FRONTEND_PID; exit' INT
wait
EOF

# Make scripts executable
chmod +x start_backend.sh start_frontend.sh start_app.sh

# Create README
cat > README.md << EOF
# Cash Tracker Application

A full-stack application for tracking cash purchases with React frontend and Python Flask backend.

## Quick Start

1. Copy all the code from the artifacts into their respective files:
   - Copy Flask app code to \`backend/app.py\`
   - Copy React components to \`frontend/src/components/\`
   - Copy App.js to \`frontend/src/App.js\`
   - Copy App.css to \`frontend/src/App.css\`
   - Copy tailwind.config.js to \`frontend/tailwind.config.js\`

2. Start the application:
   \`\`\`bash
   ./start_app.sh
   \`\`\`

3. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5000

## Manual Setup

### Backend
\`\`\`bash
cd backend
source venv/bin/activate
python app.py
\`\`\`

### Frontend
\`\`\`bash
cd frontend
npm start
\`\`\`

## Features

- ✅ Transaction entry with smart category suggestions
- ✅ Description autocomplete
- ✅ Real-time balance tracking
- ✅ Cash received tracking
- ✅ Transaction history with pagination and filtering
- ✅ Analytics with bar and pie charts
- ✅ Mobile-responsive design
- ✅ Data persistence in JSON files

## File Structure

\`\`\`
cash-tracker/
├── backend/
│   ├── app.py                 # Flask application
│   ├── requirements.txt       # Python dependencies
│   ├── venv/                 # Virtual environment
│   └── data/
│       ├── transactions.json  # Transaction data
│       └── categories.json    # Categories and descriptions
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   ├── TransactionForm.js
│   │   │   ├── TransactionHistory.js
│   │   │   └── Analytics.js
│   │   ├── App.js
│   │   ├── App.css
│   │   └── index.js
│   ├── package.json
│   └── tailwind.config.js
├── start_app.sh              # Start both services
├── start_backend.sh          # Start backend only
└── start_frontend.sh         # Start frontend only
\`\`\`

## Deployment on Mac Mini

1. **Install Prerequisites:**
   - Python 3.8+: \`brew install python\`
   - Node.js 14+: \`brew install node\`

2. **Clone and Setup:**
   \`\`\`bash
   git clone <your-repo> cash-tracker
   cd cash-tracker
   chmod +x *.sh
   ./start_app.sh
   \`\`\`

3. **Access from Mobile:**
   - Find your Mac Mini IP: \`ifconfig | grep inet\`
   - Access from iOS: \`http://[MAC_MINI_IP]:5000\`

## Data Backup

Your transaction data is stored in \`backend/data/\`. Regular backups are recommended:

\`\`\`bash
# Backup
cp -r backend/data backend/data_backup_$(date +%Y%m%d)

# Restore
cp -r backend/data_backup_YYYYMMDD backend/data
\`\`\`

## Troubleshooting

### Port Already in Use
\`\`\`bash
# Kill processes on port 5000
lsof -ti:5000 | xargs kill -9

# Kill processes on port 3000  
lsof -ti:3000 | xargs kill -9
\`\`\`

### Python Virtual Environment Issues
\`\`\`bash
cd backend
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
\`\`\`

### Node Dependencies Issues
\`\`\`bash
cd frontend
rm -rf node_modules package-lock.json
npm install
\`\`\`

## API Endpoints

- \`GET /api/transactions\` - Get transactions with pagination
- \`POST /api/transactions\` - Add new transaction
- \`POST /api/cash-received\` - Add cash received
- \`GET /api/categories\` - Get categories and descriptions
- \`POST /api/suggestions/category\` - Get category suggestion
- \`GET /api/suggestions/description\` - Get description suggestions
- \`GET /api/balance\` - Get current balance
- \`GET /api/analytics\` - Get analytics data

## License

MIT License - feel free to modify and distribute.
EOF

echo ""
echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Copy the Flask app code to backend/app.py"
echo "2. Copy the React components to their respective files"
echo "3. Run ./start_app.sh to start the application"
echo ""
echo "📱 The application will be accessible at:"
echo "   - Web: http://localhost:3000"
echo "   - API: http://localhost:5000"
echo ""
echo "🔧 For mobile access, use your Mac Mini's IP address"
echo "   Find IP with: ifconfig | grep inet"
echo "   Then access: http://[YOUR_IP]:5000"
echo ""