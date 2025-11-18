# Freelance MCP Server - Quick Start Guide

Get up and running in 5 minutes!

## 🚀 Quick Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Get GROQ API Key (Free)

1. Visit https://console.groq.com/
2. Sign up for a free account
3. Create an API key
4. Copy the key (starts with `gsk_...`)

### 3. Configure Environment

The `.env` file has been created for you. Edit it and add your GROQ API key:

```bash
# Open .env in your editor
nano .env  # or vim, code, etc.

# Replace this line:
GROQ_API_KEY=gsk_your_groq_api_key_here_replace_this

# With your actual key:
GROQ_API_KEY=gsk_abc123xyz...
```

### 4. Run the Demo

```bash
# Option 1: Quick demo (recommended for first time)
python main.py

# Option 2: Comprehensive demo
python freelance_client.py --mode demo

# Option 3: Simplified demo
python freelance_client2.py

# Option 4: Interactive mode
python freelance_client.py --mode interactive
```

## ✅ Verify Installation

```bash
python freelance_client.py --check-env
```

This will check:
- Python version (3.11+)
- Required packages
- Environment variables
- File structure

## 🎯 What You Get

After running the demo, you'll see:

1. **Gig Search** - Find freelance opportunities across 6 platforms
2. **Profile Creation** - Set up your freelancer profile
3. **AI Proposals** - Generate personalized proposals with ChatGroq
4. **Rate Negotiation** - Get strategic advice for rate discussions
5. **Code Review** - Automated code quality analysis
6. **Code Debug** - Fix common code issues automatically
7. **Profile Optimization** - AI-powered profile improvement tips
8. **Market Trends** - Current freelance market insights

## 🔧 Common Issues

### "GROQ_API_KEY not configured"
- Make sure you edited `.env` and added your real API key
- Key should start with `gsk_`
- No quotes or spaces around the key

### "freelance_server.py not found"
- Make sure you're in the project directory
- Run `ls` to verify files are present

### "Module 'mcp' not found"
```bash
pip install mcp langchain-groq pydantic python-dotenv
```

## 📚 Next Steps

1. **Try Claude Desktop Integration** - See [README.md](README.md) section "Integration with Claude Desktop"
2. **Run Tests** - `pytest tests/ -v`
3. **Explore Interactive Mode** - `python freelance_client.py --mode interactive`
4. **Check Documentation** - See [USAGE.md](USAGE.md) for advanced features

## 💡 Tips

- The server uses **mock data** for demonstration
- AI features require a valid GROQ_API_KEY
- All features work offline except AI-powered ones
- Check `CHANGELOG.md` for version history

## 🆘 Need Help?

- **Issues**: https://github.com/N1KH1LT0X1N/Freelance-MCP-Server/issues
- **Documentation**: See `docs/` directory
- **Examples**: Check `main.py` and `freelance_client.py`

## 🎉 You're Ready!

Run `python main.py` and choose option 1 or 2 to see the magic!
