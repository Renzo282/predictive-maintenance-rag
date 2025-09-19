#!/bin/bash

# Predictive Maintenance RAG Agent - Installation Script

echo "🚀 Installing Predictive Maintenance RAG Agent..."

# Check if Python 3.8+ is installed
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Error: Python 3.8 or higher is required. Current version: $python_version"
    exit 1
fi

echo "✅ Python version check passed: $python_version"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p data/vector_store
mkdir -p models
mkdir -p logs

# Copy environment file
echo "⚙️ Setting up environment..."
if [ ! -f .env ]; then
    cp config.env .env
    echo "📝 Created .env file from config.env"
    echo "⚠️  Please update .env with your actual credentials"
else
    echo "✅ .env file already exists"
fi

# Initialize database
echo "🗄️ Initializing database..."
python scripts/init_database.py

echo ""
echo "🎉 Installation completed successfully!"
echo ""
echo "Next steps:"
echo "1. Update .env file with your actual credentials"
echo "2. Activate virtual environment: source venv/bin/activate"
echo "3. Start the application: python main.py"
echo "4. Test the API: python scripts/test_api.py"
echo ""
echo "For more information, see README.md"
