# ⚡ VoxQuery - 5 Minute Setup Checklist

## Step 1: Navigate to Project (1 min)

```bash
cd c:\Users\USER\Documents\trae_projects\VoxQuery
```

## Step 2: Backend Setup (2 min)

```bash
# Go to backend
cd backend

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env

# Edit .env with your details:
# - WAREHOUSE_HOST (e.g., xy12345.us-east-1.snowflakecomputing.com)
# - WAREHOUSE_USER (your username)
# - WAREHOUSE_PASSWORD (your password)
# - WAREHOUSE_DATABASE (your database)
# - OPENAI_API_KEY (sk-...)
```

## Step 3: Frontend Setup (1 min)

```bash
# Go to frontend
cd ../frontend

# Install dependencies
npm install
```

## Step 4: Run Backend (Terminal 1)

```bash
# From backend directory
cd backend
python main.py

# You should see:
# INFO: Uvicorn running on http://0.0.0.0:8000
```

## Step 5: Run Frontend (Terminal 2)

```bash
# From frontend directory
cd frontend
npm run dev

# You should see:
# VITE v... ready in XXX ms
# ➜ Local: http://localhost:5173/
```

## Step 6: Test It! (1 min)

1. Open http://localhost:5173 in browser
2. Type: "Show top 10 clients by revenue"
3. See SQL, results, and chart!

## ✅ Verification Checklist

- [ ] Backend running on http://localhost:8000
- [ ] Frontend running on http://localhost:5173
- [ ] Can see chat interface
- [ ] Can ask a question
- [ ] Get SQL in response
- [ ] Get results table
- [ ] See auto-generated chart

## 📚 Next Steps

1. **Explore**: Try different questions
2. **Check SQL**: View generated SQL for accuracy
3. **Export**: Try CSV/Excel export
4. **Warehouse**: Change warehouse in dropdown
5. **Read**: Check QUICKSTART.md for more details

## 🔗 Quick Links

| What | Where |
|------|-------|
| Docs | http://localhost:8000/docs |
| Frontend | http://localhost:5173 |
| API | http://localhost:8000 |
| README | Open README.md |
| Examples | Open backend/examples.py |

## 🐛 Troubleshooting

**Port 8000 already in use?**
```bash
# Change API_PORT in .env to 8001
export API_PORT=8001
python main.py
```

**Port 5173 already in use?**
```bash
# Vite will find next available port
npm run dev
```

**Import errors in Python?**
```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

**NPM install fails?**
```bash
# Clear npm cache
npm cache clean --force
npm install
```

## ✨ You're Done!

Just 5 minutes and you have a working natural language SQL system!

🎉 Start asking questions!

---

**Next**: Open QUICKSTART.md for more details  
**Questions**: Check DEVELOPMENT.md  
**Architecture**: Read docs/ARCHITECTURE.md
