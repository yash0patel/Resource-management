# Inventory Management System - React & FastAPI

A modern web-based Inventory Management System with AI-powered forecasting, replacing the original Streamlit UI with a professional React frontend.

## Features

- **📊 Forecast Planner** - AI-powered resource forecasting with ML model predictions
- **📝 Add Records** - Batch add inventory records with staging before upload
- **📈 Real-time Analytics** - Dashboard with key statistics
- **🎨 Modern UI** - Professional React interface with responsive design
- **⚡ Fast Backend** - FastAPI for high-performance predictions

## Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **Uvicorn** - ASGI web server
- **Pandas** - Data processing
- **Joblib** - ML model loading
- **scikit-learn** - Machine learning

### Frontend
- **React 18** - UI library
- **Vite** - Build tool
- **Axios** - HTTP client
- **Lucide React** - Icon library
- **CSS3** - Modern styling

## Project Structure

```
├── backend.py                  # FastAPI server
├── requirements.txt            # Python dependencies
├── retail_store_inventory.csv  # Data file
├── models/                     # ML models directory
│   ├── best_resource_model.joblib
│   ├── encoders.joblib
│   └── feature_names.joblib
└── frontend/                   # React application
    ├── package.json
    ├── vite.config.js
    ├── index.html
    └── src/
        ├── main.jsx
        ├── App.jsx
        ├── App.css
        ├── index.css
        └── pages/
            ├── ForecastPlanner.jsx
            ├── ForecastPlanner.css
            ├── AddRecords.jsx
            └── AddRecords.css
```

## Setup Instructions

### Backend Setup

1. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

2. **Run the FastAPI server:**
```bash
python -m uvicorn backend:app --reload --host 0.0.0.0 --port 8000
```

The backend will be available at: `http://localhost:8000`

**API Documentation:** `http://localhost:8000/docs`

### Frontend Setup

1. **Navigate to frontend directory:**
```bash
cd frontend
```

2. **Install Node dependencies:**
```bash
npm install
```

3. **Run development server:**
```bash
npm run dev
```

The frontend will be available at: `http://localhost:3000`

### Full Setup (Both Backend & Frontend)

#### Option 1: Run in separate terminals

**Terminal 1 (Backend):**
```bash
python -m uvicorn backend:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 (Frontend):**
```bash
cd frontend
npm run dev
```

#### Option 2: Using Windows batch script (create `run.bat`):
```batch
@echo off
start python -m uvicorn backend:app --reload --host 0.0.0.0 --port 8000
cd frontend
call npm run dev
```

Then run: `.\run.bat`

## API Endpoints

### Health Check
- `GET /` - Health check and model status

### Statistics
- `GET /api/stats` - Get dashboard statistics

### Forecast
- `POST /api/forecast` - Generate resource forecast
  - **Request body:**
    ```json
    {
      "start_date": "2026-01-15",
      "end_date": "2026-01-22",
      "holiday_promotion": 0,
      "inventory_available": 500,
      "category": "Electronics",
      "region": "East",
      "weather_condition": "Sunny",
      "seasonality": "Winter"
    }
    ```

### Data Management
- `GET /api/dropdowns` - Get all dropdown options
- `POST /api/add-records` - Batch add inventory records
  - **Request body:**
    ```json
    {
      "records": [
        {
          "date": "2026-01-15",
          "store_id": "S001",
          "product_id": "P0001",
          "category": "Electronics",
          "region": "East",
          "inventory_level": 100,
          "units_sold": 5,
          "units_ordered": 10,
          "demand_forecast": 8.5,
          "price": 99.99,
          "discount": 5.0,
          "weather_condition": "Sunny",
          "holiday_promotion": 0,
          "competitor_pricing": 89.99,
          "seasonality": "Winter"
        }
      ]
    }
    ```

## UI Features

### Dashboard
- Total records count
- Unique stores count
- Unique products count
- Quick access to recent data range

### Forecast Planner
- Date range selection (single date or range)
- Current stock input
- Holiday/Promotion toggle
- Category, Region, Weather, and Seasonality selections
- Real-time forecast calculations
- Summary metrics (Total needed, Current stock, Additional needed)
- Detailed forecasting table with status indicators

### Add Records
- Comprehensive inventory record form
- Batch staging of multiple records
- Duplicate detection
- Table preview of staged records
- Batch delete functionality
- CSV export capability

## Build for Production

### Backend
The backend is production-ready. For deployment:
```bash
python -m uvicorn backend:app --host 0.0.0.0 --port 8000
```

### Frontend
Build the React app for production:
```bash
cd frontend
npm run build
```

Output files will be in `frontend/dist/` directory.

## Troubleshooting

### Model Not Loading
- Ensure model files exist in the `models/` directory
- Check file paths in `backend.py`
- Verify model compatibility with required features

### API Connection Issues
- Ensure backend is running on port 8000
- Check CORS settings in `backend.py`
- Verify frontend is accessing correct API endpoint

### Frontend Build Issues
- Delete `node_modules` and `package-lock.json`
- Run `npm install` again
- Clear Vite cache: `rm -rf frontend/.vite`

## Environment Variables (Optional)

Create `.env` file in frontend directory:
```
VITE_API_BASE_URL=http://localhost:8000
```

## Performance Tips

1. **Backend**: Use uvicorn with multiple workers: `--workers 4`
2. **Frontend**: Enable lazy loading for better initial load time
3. **Database**: Consider caching frequent queries

## Security Notes

- The backend has CORS enabled for all origins (`*`)
- For production, restrict CORS to specific domains
- Add authentication/authorization as needed
- Validate all input data

## Future Enhancements

- [ ] User authentication
- [ ] Advanced data visualization with charts
- [ ] Export to multiple formats (PDF, Excel)
- [ ] Real-time data sync
- [ ] Mobile app version
- [ ] Predictive alerts
- [ ] Multi-language support

## License

College Project © 2026

## Support

For issues or questions, please check the API documentation at `http://localhost:8000/docs` after starting the backend server.

---

**Upgrade from Streamlit:** This React + FastAPI stack provides:
- ✅ Better performance and responsiveness
- ✅ Professional UI/UX
- ✅ Scalable architecture
- ✅ Separation of concerns (frontend/backend)
- ✅ API documentation
- ✅ Better error handling
