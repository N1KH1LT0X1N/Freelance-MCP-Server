# Quick Reference - Freelance MCP Server

## 🚀 Start Server

### Manual:
```bash
python freelance_server.py stdio
```

### With Claude Desktop:
Already configured in `%APPDATA%\Claude\claude_desktop_config.json`

---

## 🛠️ Available Tools (10)

| Tool | Description |
|------|-------------|
| `search_gigs` | Search freelance gigs by skills, budget, platform |
| `generate_proposal` | AI-generated proposal for a specific gig |
| `negotiate_rate` | AI-powered rate negotiation assistant |
| `code_review` | Review code for quality, security, performance |
| `code_debug` | Debug code with AI assistance |
| `optimize_profile` | Optimize freelancer profile for better matches |
| `validate` | Verify user identity with OTP |
| `create_user_profile` | Create new freelancer profile |
| `analyze_profile_fit` | Analyze how well profile matches gig |
| `track_application_status` | Track status of job applications |

---

## 📋 Available Prompts (8)

1. **Freelance Project Proposal Writer** - Create winning proposals
2. **Rate Negotiation Assistant** - Negotiate better rates
3. **Client Communication Template** - Professional client messages
4. **Profile Optimizer** - Improve your profile
5. **Gig Search Strategy** - Find the best gigs
6. **Application Tracker** - Track your applications
7. **Skills Gap Analyzer** - Identify skill gaps
8. **Time Management Planner** - Plan your work schedule

---

## 📦 Available Resources (3)

| Resource | Description |
|----------|-------------|
| `gig://{id}` | Get details for specific gig |
| `gigs://all` | Get all available gigs |
| `user://{username}` | Get user profile data |

---

## 🧪 Testing Commands

### Run All Tests:
```bash
python tests\test_debug.py
```

### Check Syntax:
```bash
python -m pylint --errors-only freelance_server.py
```

### Test Import:
```bash
python -c "import freelance_server; print('OK')"
```

### Test JSON-RPC:
```bash
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}' | python freelance_server.py stdio
```

---

## 🔧 Configuration

### Required Environment Variables (.env):
```bash
GROQ_API_KEY=your_groq_api_key_here
OWNER_PHONE_NUMBER=1234567890
```

### Optional Environment Variables:
```bash
LOG_LEVEL=INFO
DATABASE_PATH=./data/freelance.db
```

---

## 📂 Project Structure

```
mcp-server-1/
├── freelance_server.py    # Main server (1507 lines)
├── requirements.txt       # Dependencies
├── .env                   # Config (not tracked)
│
├── core/                  # Core modules
├── database/              # Data models & manager
├── mcp_extensions/        # Prompts & resources
├── utils/                 # Utilities
├── tests/                 # Test suite
├── docs/                  # Documentation (10 files)
├── examples/              # Usage examples
└── archive/               # Legacy files
```

---

## 🐛 Troubleshooting

### Server won't start:
```bash
# Check dependencies
uv run --with mcp --with python-dotenv --with langchain-groq --with pydantic freelance_server.py stdio
```

### "Server disconnected" in Claude:
1. Check .env file has GROQ_API_KEY
2. Restart Claude Desktop
3. Check logs in Claude Desktop → Settings → Developer

### Import errors:
```bash
# Install missing dependencies
pip install -r requirements.txt
```

---

## 📊 Test Results

```
✓ Imports......................... PASS
✓ Server Module................... PASS
✓ Database........................ PASS (16 gigs)
✓ Helper Functions................ PASS
✓ MCP Tools....................... PASS (10 tools)
✓ Environment..................... PASS

RESULTS: 6/6 tests passed ✅
```

---

## 🎯 Quick Examples

### Search for gigs:
```
"Search for Python gigs under $1000"
```

### Generate proposal:
```
"Generate a proposal for gig ID abc123"
```

### Optimize profile:
```
"Help me optimize my freelancer profile"
```

### Check market trends:
```
"Show me freelance market trends"
```

---

## 📚 Documentation

- **README.md** - Complete setup guide
- **STRUCTURE.md** - Project organization
- **DEBUG_REPORT.md** - Bug fixes
- **VALIDATION_STATUS.md** - Test results
- **docs/** - Detailed guides

---

## ✅ Status: PRODUCTION READY

All tests passing • Zero errors • Fully validated

---

*Quick Reference v1.0.0*
