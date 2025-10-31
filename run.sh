#!/bin/bash
# Quick start script for AI Research Assistant

echo "🧠 AI Research Assistant - LangJu Edition"
echo "=========================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "❌ Failed to create virtual environment"
        exit 1
    fi
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
if [ ! -f "venv/.installed" ]; then
    echo "📥 Installing dependencies..."
    pip install -r requirements.txt
    if [ $? -eq 0 ]; then
        touch venv/.installed
    else
        echo "❌ Failed to install dependencies"
        exit 1
    fi
else
    echo "✅ Dependencies already installed"
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found. Creating from template..."
    cp app/config/.env.template .env
    echo "✅ Created .env file. Please edit it with your API keys if needed."
fi

# Run Streamlit
echo ""
echo "🚀 Starting Streamlit application..."
echo "📝 Open http://localhost:8501 in your browser"
echo ""
streamlit run app/main.py
