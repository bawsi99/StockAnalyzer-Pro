#!/bin/bash
# Setup script for prompt testing environment
# This script helps configure the necessary environment variables

echo "🔧 Setting up Prompt Testing Environment"
echo "======================================="

# Check if API keys are set
echo ""
echo "📋 Checking API Keys:"

if [ -z "$GEMINI_API_KEY" ]; then
    echo "❌ GEMINI_API_KEY not set"
    echo "   To set it temporarily: export GEMINI_API_KEY='your_api_key_here'"
    echo "   To set it permanently: echo 'export GEMINI_API_KEY=\"your_api_key_here\"' >> ~/.zshrc"
else
    echo "✅ GEMINI_API_KEY is configured"
fi

if [ -z "$POLYGON_API_KEY" ]; then
    echo "⚠️  POLYGON_API_KEY not set (optional - will use synthetic data)"
    echo "   To get a free API key: https://polygon.io/"
    echo "   To set it: export POLYGON_API_KEY='your_api_key_here'"
else
    echo "✅ POLYGON_API_KEY is configured"
fi

if [ -z "$ALPHA_VANTAGE_API_KEY" ]; then
    echo "⚠️  ALPHA_VANTAGE_API_KEY not set (optional fallback)"
    echo "   To get a free API key: https://www.alphavantage.co/support/#api-key"
    echo "   To set it: export ALPHA_VANTAGE_API_KEY='your_api_key_here'"
else
    echo "✅ ALPHA_VANTAGE_API_KEY is configured"
fi

echo ""
echo "📦 Installing required packages:"

# Install required Python packages
pip install pandas numpy requests openpyxl asyncio

echo ""
echo "✅ Setup complete!"
echo ""
echo "To run the prompt testing framework:"
echo "python prompt_testing_framework.py"
echo ""
echo "Note: The framework will work with synthetic data even without API keys,"
echo "but real API keys will provide better testing with actual market data."