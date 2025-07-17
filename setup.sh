#!/bin/bash

echo "🚀 Setting up Timetable Generation System..."
echo "=============================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16+ first."
    exit 1
fi

echo "✅ Prerequisites check passed"

# Backend Setup
echo ""
echo "📦 Setting up Backend..."
cd django-backend

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Navigate to backend directory
cd backend

# Run migrations
echo "Running database migrations..."
python manage.py migrate

echo "✅ Backend setup completed!"

# Frontend Setup
echo ""
echo "📦 Setting up Frontend..."
cd ../../frontend

# Install dependencies
echo "Installing Node.js dependencies..."
npm install

echo "✅ Frontend setup completed!"

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "To start the application:"
echo "1. Start Backend:"
echo "   cd django-backend/backend"
echo "   source ../venv/bin/activate"
echo "   python manage.py runserver 8000"
echo ""
echo "2. Start Frontend (in a new terminal):"
echo "   cd frontend"
echo "   npm run dev"
echo ""
echo "3. Access the application:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo ""
echo "📚 For detailed instructions, see README.md" 