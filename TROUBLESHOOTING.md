# Troubleshooting Guide

## Common Issues & Solutions

---

## 🔴 Installation Issues

### Python Not Found
**Error:**
```
'python' is not recognized as an internal or external command
```

**Solutions:**
1. Install Python from https://python.org (make sure to check "Add Python to PATH")
2. Restart your computer after installation
3. Try using `python3` instead of `python`
4. Verify installation:
   ```bash
   python --version
   ```

---

### Node.js Not Found
**Error:**
```
'node' is not recognized as an internal or external command
```

**Solutions:**
1. Install Node.js from https://nodejs.org
2. Restart your computer after installation
3. Verify installation:
   ```bash
   node --version
   npm --version
   ```

---

### Permission Denied (Linux/Mac)
**Error:**
```
Permission denied: './start.sh'
```

**Solution:**
```bash
chmod +x start.sh
./start.sh
```

---

## 🔴 Backend Issues

### Port 8000 Already in Use
**Error:**
```
Address already in use
OSError: [Errno 98] Address already in use
```

**Solutions:**

**Option 1: Find and stop the process using port 8000**

Windows:
```bash
netstat -ano | findstr :8000
taskkill /PID <pid> /F
```

Linux/Mac:
```bash
lsof -i :8000
kill -9 <pid>
```

**Option 2: Use a different port**

Modify `backend.py`:
```python
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)  # Change 8000 to 8001
```

And update `frontend/vite.config.js`:
```javascript
proxy: {
  '/api': {
    target: 'http://localhost:8001',  // Update port here too
    changeOrigin: true,
  }
}
```

---

### ModuleNotFoundError: No module named 'fastapi'
**Error:**
```
ModuleNotFoundError: No module named 'fastapi'
```

**Solution:**
```bash
pip install -r requirements.txt
```

If that doesn't work:
```bash
pip install fastapi uvicorn pandas joblib
```

---

### Model Not Found
**Error:**
```
FileNotFoundError: No model file found. Expected one of: ...
```

**Solutions:**
1. Check if model files exist in `models/` directory:
   - `best_resource_model.joblib`
   - Or `best_sales_model.joblib`
   - Or `Sales_model.pkl`

2. Verify the full path. The backend expects them in:
   ```
   models/best_resource_model.joblib
   best_sales_model.joblib
   Sales_model.pkl
   ```

3. If models are named differently, edit `backend.py`:
   ```python
   MODEL_CANDIDATES = [
       Path("your_model_path.joblib"),
       Path("another_model.pkl"),
   ]
   ```

---

### CSV File Not Found
**Warning:**
```
Note: retail_store_inventory.csv not found
```

**Solution:**
Create an empty CSV with headers:
```bash
# Windows
echo Date,Store ID,Product ID,Category,Region,Inventory Level,Units Sold,Units Ordered,Demand Forecast,Price,Discount,Weather Condition,Holiday/Promotion,Competitor Pricing,Seasonality > retail_store_inventory.csv

# Linux/Mac
echo "Date,Store ID,Product ID,Category,Region,Inventory Level,Units Sold,Units Ordered,Demand Forecast,Price,Discount,Weather Condition,Holiday/Promotion,Competitor Pricing,Seasonality" > retail_store_inventory.csv
```

---

## 🔴 Frontend Issues

### Port 3000 Already in Use
**Error:**
```
Port 3000 is in use. Would you like to use another port?
```

**Solutions:**

**Option 1: Use a different port**

Modify `frontend/vite.config.js`:
```javascript
server: {
    port: 3001,  // Change to any available port
    // ...
}
```

**Option 2: Stop the process using port 3000**

Windows:
```bash
netstat -ano | findstr :3000
taskkill /PID <pid> /F
```

Linux/Mac:
```bash
lsof -i :3000
kill -9 <pid>
```

---

### Module Not Found: react
**Error:**
```
Cannot find module 'react'
ModuleNotFoundError
```

**Solution:**
```bash
cd frontend
npm install
```

If that doesn't work, try:
```bash
rm -rf node_modules package-lock.json
npm install
```

---

### Blank Page in Browser
**Symptoms:**
- Page loads but shows nothing
- Empty white page

**Solutions:**

1. **Check browser console for errors:**
   - Press F12 → Console tab
   - Look for red error messages

2. **Wait for both servers:**
   - Ensure backend is running: http://localhost:8000/docs
   - Wait 5 seconds for frontend build
   - Refresh browser (Ctrl+F5)

3. **Frontend build failed:**
   ```bash
   cd frontend
   npm run build  # Check for errors
   ```

4. **Clear cache:**
   - Delete `frontend/.vite/` folder
   - Delete `frontend/dist/` folder
   - Close and reopen browser

---

### API Connection Failed
**Error in Console:**
```
GET http://localhost:8000/api/... 404 (Not Found)
CORS error
```

**Solutions:**

1. **Backend not running:**
   - Open new terminal
   - Run: `python -m uvicorn backend:app --reload`

2. **Wrong port:**
   - Check `frontend/vite.config.js` proxy URL
   - Backend must be on port 8000 (or update proxy)

3. **CORS blocked:**
   - Already enabled in `backend.py`
   - If custom backend, add CORS:
     ```python
     from fastapi.middleware.cors import CORSMiddleware
     app.add_middleware(
         CORSMiddleware,
         allow_origins=["*"],
         allow_credentials=True,
         allow_methods=["*"],
         allow_headers=["*"],
     )
     ```

---

## 🔴 Data Issues

### CSV Encoding Error
**Error:**
```
UnicodeDecodeError: 'utf-8' codec can't decode
```

**Solution:**
Make sure CSV file is saved as UTF-8:
1. Open file in text editor
2. Save As → UTF-8 encoding
3. Or recreate the file

---

### Duplicate Record Error
**Message:**
```
Duplicate record detected
```

**Explanation:**
A record with the same Date, Store ID, Product ID, Category, and Region already exists in the batch.

**Solution:**
1. Review the batch records
2. Delete the duplicate using the delete button
3. Or modify the duplicate to be different

---

### No Dropdowns Loading
**Problem:**
Dropdowns appear empty

**Solution:**
1. Check if CSV file exists and has data
2. Verify CSV has correct column names:
   - "Store ID"
   - "Product ID"
3. Reload page (F5)

---

## 🔴 Performance Issues

### Slow Forecast Calculation
**Problem:**
Takes more than 5 seconds to calculate

**Solutions:**
1. Try with smaller date range (not 30+ days)
2. Check if backend is stuck:
   - Look at backend terminal for errors
   - Restart backend
3. System might be slow:
   - Close other applications
   - Check available memory

---

### Slow File Upload
**Problem:**
Adding many records takes time

**Solution:**
This is normal for large batches. The system is saving to CSV which can be slow. Try:
1. Batch in smaller groups (100-500 records)
2. Use a faster disk (SSD vs HDD)

---

## 🔴 Restart Solutions

Sometimes restarting everything helps:

### Full Restart (Nuclear Option)
```bash
# Stop everything (Ctrl+C in all terminals)

# Clean dependencies
rm -rf frontend/node_modules
rm -rf frontend/.vite
rm -rf frontend/dist

# Clean Python cache
find . -type d -name __pycache__ -exec rm -r {} +

# Reinstall everything
pip install -r requirements.txt
cd frontend && npm install
cd ..

# Run again
python -m uvicorn backend:app --reload
# In another terminal:
cd frontend
npm run dev
```

---

## 🟡 Browser Cache Issues

### Page Not Updating After Changes
**Solution:**
Clear cache and reload:
1. Clear browser cache (Ctrl+Shift+Delete)
2. Hard refresh (Ctrl+Shift+F5)
3. Close and reopen browser

### Old Version Still Loading
**Solution:**
```bash
# While frontend is running:
cd frontend
npm run build
```

---

## 📞 Getting Help

### Required Information for Support:
1. Exact error message (copy-paste)
2. Which OS? (Windows/Mac/Linux)
3. Python version: `python --version`
4. Node version: `node --version`
5. What were you trying to do?
6. Terminal output (screenshots helpful)

### Debug Mode
Run backend with more logging:
```bash
python -m uvicorn backend:app --reload --log-level debug
```

---

## 🆘 Still Stuck?

1. **Read the full README_NEW.md** - Covers more details
2. **Check FastAPI docs** - http://localhost:8000/docs
3. **Browser Console** - F12 → Console for JavaScript errors
4. **Backend Terminal** - Look for Python error messages
5. **Google the error** - Copy exact error message

---

## Advanced Debugging

### Check What's Running on Ports

Windows:
```bash
netstat -ano | findstr :8000
netstat -ano | findstr :3000
```

Linux/Mac:
```bash
lsof -i :8000
lsof -i :3000
```

### View Backend Logs
The terminal where you ran `uvicorn` shows all requests and errors.

### View Frontend Errors
Press F12 in browser → Console tab → Look for red errors

### Test API Directly
```bash
curl http://localhost:8000/api/stats
```

---

**Still having issues? Make sure:**
- ✓ Python 3.8+ installed
- ✓ Node 16+ installed  
- ✓ Both requirements.txt and package.json installed
- ✓ Both servers running (8000 and 3000)
- ✓ No firewall blocking ports
- ✓ Models exist in models/ directory
- ✓ CSV file exists (can be empty)
