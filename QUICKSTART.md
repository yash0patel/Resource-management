# Quick Start Guide - Inventory Management System

## System Requirements

- **Python 3.8+** - Download from https://python.org
- **Node.js 16+** - Download from https://nodejs.org
- **Git** (optional) - Download from https://git-scm.com

## Quick Installation & Run

### Method 1: Automatic (Recommended for Windows)

1. **Open Command Prompt** or **PowerShell** in the Inventory Management folder
2. **Run one of these commands:**

**For Command Prompt:**
```
start.bat
```

**For PowerShell:**
```
powershell -ExecutionPolicy Bypass .\start.ps1
```

This will automatically:
- Check Python and Node.js installation
- Install all dependencies
- Start both backend and frontend servers
- Open your browser to the application

---

### Method 2: Manual Setup (Works on all OS)

#### Step 1: Install Python Dependencies

Open Command Prompt/Terminal in the project directory:

```bash
pip install -r requirements.txt
```

#### Step 2: Start Backend Server

Keep the first terminal/command prompt open and run:

```bash
python -m uvicorn backend:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

#### Step 3: Open New Terminal - Start Frontend

Open another Command Prompt/Terminal window:

```bash
cd frontend
npm install
npm run dev
```

You should see:
```
VITE v4.x.x  ready in xxx ms

➜  Local:   http://localhost:3000/
```

#### Step 4: Open Browser

Visit: **http://localhost:3000**

---

## What's Now Available

### 📊 Forecast Planner Tab
- Input inventory parameters
- Get AI-powered resource forecasts
- View detailed forecast tables
- Get stock shortage warnings

### 📝 Add Records Tab
- Add inventory records with form
- Batch stage multiple records
- Delete records before uploading
- Save batch to CSV

### 📈 Dashboard
- View total records count
- See unique stores/products
- Monitor data date range

### 🔧 API Documentation
Visit: **http://localhost:8000/docs**
(Interactive API playground with all endpoints)

---

## Stopping the Servers

### If using automatic script:
- Close the command prompt windows (Ctrl+C then close)

### If using manual method:
**Terminal 1 (Backend):** Press `Ctrl+C`
**Terminal 2 (Frontend):** Press `Ctrl+C`

---

## Troubleshooting

### ❌ "Python not found"
- Ensure Python is installed
- Restart Command Prompt after installing Python
- Check by running: `python --version`

### ❌ "Node not found"
- Ensure Node.js is installed
- Restart Command Prompt after installing Node.js
- Check by running: `node --version`

### ❌ "Port 8000 already in use"
The backend port is occupied. Either:
- Find and close the other application using port 8000
- Modify `backend.py` and `frontend/vite.config.js` to use different port

### ❌ "Port 3000 already in use"
The frontend port is occupied. Either:
- Find and close the other application using port 3000
- Modify `frontend/vite.config.js` to use different port

### ❌ Frontend shows blank page
- Wait a few seconds for backend to start
- Check browser console (F12) for errors
- Verify backend is running on http://localhost:8000/docs

### ❌ "Module not found" error
Run:
```bash
pip install -r requirements.txt
```

or for frontend:
```bash
cd frontend
npm install
```

---

## First Time Setup Checklist

- [ ] Python 3.8+ installed
- [ ] Node.js 16+ installed
- [ ] Ran `pip install -r requirements.txt`
- [ ] Ran `cd frontend && npm install`
- [ ] Backend running on `http://localhost:8000`
- [ ] Frontend running on `http://localhost:3000`
- [ ] Can access both URLs in browser
- [ ] Machine learning models exist in `models/` directory

---

## Next Steps

1. **View the Dashboard** - See your data statistics
2. **Try Forecast Planner** - Play with forecast parameters
3. **Add Test Records** - Practice bulk uploading data
4. **Check API Docs** - Explore all available endpoints

---

## Production Deployment

### Build Frontend
```bash
cd frontend
npm run build
```

Output files are in `frontend/dist/`

### Run Production Backend
```bash
python -m uvicorn backend:app --host 0.0.0.0 --port 8000
```

### Security Notes
- Change CORS settings in `backend.py` for production
- Add authentication if needed
- Use environment variables for sensitive data

---

## File Structure Reference

```
.
├── backend.py                 ← FastAPI server
├── requirements.txt           ← Python dependencies
├── start.bat / start.ps1      ← Quick start scripts
├── README_NEW.md              ← Full documentation
├── retail_store_inventory.csv ← Data file
├── models/                    ← ML models directory
└── frontend/                  ← React application
    ├── package.json
    ├── vite.config.js
    ├── index.html
    └── src/
        ├── main.jsx
        ├── App.jsx
        └── pages/
            ├── ForecastPlanner.jsx
            └── AddRecords.jsx
```

---

## Need Help?

1. Check the full README_NEW.md for detailed information
2. Visit API docs at: http://localhost:8000/docs
3. Check browser console (F12) for errors
4. Ensure all files are in correct directories

---

**You're all set! Enjoy your modern Inventory Management System! 🚀**
