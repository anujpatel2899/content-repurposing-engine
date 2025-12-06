#!/bin/bash
# Quick verification script for Phase 1 implementation

echo "=================================================="
echo "  Content Repurposing Engine - Verification"
echo "=================================================="
echo ""

# Check Python version
echo "1️⃣ Checking Python version..."
python3 --version
echo ""

# Check imports
echo "2️⃣ Verifying imports..."
python3 -c "
import agents
import workflow
import utils
import config
from agents import RepurposingState
print('   ✅ All core modules imported successfully')
" || echo "   ❌ Import failed - run: pip3 install -r requirements.txt"
echo ""

# Check structure
echo "3️⃣ Verifying project structure..."
echo "   📁 Agents:"
ls -1 agents/*.py 2>/dev/null | wc -l | awk '{print "      " $1 " agent files found"}'
echo "   📁 Utils:"
ls -1 utils/*.py 2>/dev/null | wc -l | awk '{print "      " $1 " utility files found"}'
echo ""

# Check if .env exists
echo "4️⃣ Checking configuration..."
if [ -f ".env" ]; then
    if grep -q "GROQ_API_KEY" .env; then
        echo "   ✅ .env file found with GROQ_API_KEY"
    else
        echo "   ⚠️  .env file exists but missing GROQ_API_KEY"
    fi
else
    echo "   ℹ️  No .env file (can enter key in UI or use .env.example as template)"
fi
echo ""

# Summary
echo "=================================================="
echo "  ✅ VERIFICATION COMPLETE"
echo "=================================================="
echo ""
echo "🚀 Ready to test!"
echo ""
echo "Option 1 - Terminal Test:"
echo "  python3 cli_test.py"
echo ""
echo "Option 2 - Streamlit UI:"
echo "  streamlit run app.py"
echo ""
echo "📖 Documentation:"
echo "  - QUICKSTART.md - Get started in 3 minutes"
echo "  - README_NEW.md - Architecture details"
echo "  - IMPLEMENTATION_SUMMARY.md - What was built"
echo ""
