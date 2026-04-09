import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { AlertCircle, TrendingUp } from 'lucide-react';
import './ForecastPlanner.css';

export default function ForecastPlanner() {
  const [planningMode, setPlanningMode] = useState('single'); // 'single' or 'range'

  const [formData, setFormData] = useState({
    start_date: new Date().toISOString().split('T')[0],
    end_date: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    holiday_promotion: 0,
    inventory_available: 100,
    category: 'Clothing',
    region: 'East',
    weather_condition: 'Sunny',
    seasonality: 'Winter',
  });

  const [dropdowns, setDropdowns] = useState({
    categories: [],
    regions: [],
    weather_conditions: [],
    seasonalities: [],
  });

  const [forecast, setForecast] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchDropdowns();
  }, []);

  const fetchDropdowns = async () => {
    try {
      const response = await axios.get('/api/dropdowns');
      setDropdowns(response.data);
    } catch (err) {
      console.error('Error fetching dropdowns:', err);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'holiday_promotion' || name.includes('_level') || name.includes('_sold') || name.includes('_ordered')
        ? parseInt(value)
        : value === 'true' ? true : value === 'false' ? false : value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setForecast(null);

    try {
      // For single date mode, set end_date to start_date
      const submitData = {
        ...formData,
        end_date: planningMode === 'single' ? formData.start_date : formData.end_date,
      };

      const response = await axios.post('/api/forecast', submitData);
      setForecast(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Error generating forecast');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="forecast-planner animate-fade">
      <header className="header-container">
        <div className="header-tag">Predictive Engine</div>
        <h1 className="header-title">Forecast Planner</h1>
        <p className="header-subtitle">Apply machine learning models to generate future demand predictions.</p>
      </header>

      <div className="container">
        <div className="section-container">
          <h2 className="section-title"><TrendingUp size={20} /> Configuration</h2>

          <form onSubmit={handleSubmit} className="forecast-form">
            {/* Planning Mode Selection */}
            <div className="planning-mode">
              <label>Planning Type</label>
              <div className="mode-buttons">
                <button
                  type="button"
                  className={`mode-btn ${planningMode === 'single' ? 'active' : ''}`}
                  onClick={() => setPlanningMode('single')}
                >
                  📅 Single Date
                </button>
                <button
                  type="button"
                  className={`mode-btn ${planningMode === 'range' ? 'active' : ''}`}
                  onClick={() => setPlanningMode('range')}
                >
                  📊 Date Range
                </button>
              </div>
            </div>

            {/* Date Selection */}
            {planningMode === 'single' ? (
              <div className="form-row grid-1">
                <div className="form-group">
                  <label htmlFor="start_date">Target Date</label>
                  <input
                    type="date"
                    id="start_date"
                    name="start_date"
                    value={formData.start_date}
                    onChange={handleInputChange}
                  />
                </div>
              </div>
            ) : (
              <div className="form-row grid-2">
                <div className="form-group">
                  <label htmlFor="start_date">Start Date</label>
                  <input
                    type="date"
                    id="start_date"
                    name="start_date"
                    value={formData.start_date}
                    onChange={handleInputChange}
                  />
                </div>
                <div className="form-group">
                  <label htmlFor="end_date">End Date</label>
                  <input
                    type="date"
                    id="end_date"
                    name="end_date"
                    value={formData.end_date}
                    onChange={handleInputChange}
                  />
                </div>
              </div>
            )}

            {/* Inventory & Holiday */}
            <div className="form-row grid-2">
              <div className="form-group">
                <label htmlFor="inventory_available">Current Stock Available</label>
                <input
                  type="number"
                  id="inventory_available"
                  name="inventory_available"
                  value={formData.inventory_available}
                  onChange={handleInputChange}
                  min="0"
                />
              </div>
              <div className="form-group">
                <label htmlFor="holiday_promotion">Holiday/Promotion</label>
                <select
                  id="holiday_promotion"
                  name="holiday_promotion"
                  value={formData.holiday_promotion}
                  onChange={handleInputChange}
                >
                  <option value="0">No</option>
                  <option value="1">Yes</option>
                </select>
              </div>
            </div>

            {/* Category & Region */}
            <div className="form-row grid-2">
              <div className="form-group">
                <label htmlFor="category">Category</label>
                <select
                  id="category"
                  name="category"
                  value={formData.category}
                  onChange={handleInputChange}
                >
                  {dropdowns.categories.map(cat => (
                    <option key={cat} value={cat}>{cat}</option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label htmlFor="region">Region</label>
                <select
                  id="region"
                  name="region"
                  value={formData.region}
                  onChange={handleInputChange}
                >
                  {dropdowns.regions.map(reg => (
                    <option key={reg} value={reg}>{reg}</option>
                  ))}
                </select>
              </div>
            </div>

            {/* Weather & Seasonality */}
            <div className="form-row grid-2">
              <div className="form-group">
                <label htmlFor="weather_condition">Weather Condition</label>
                <select
                  id="weather_condition"
                  name="weather_condition"
                  value={formData.weather_condition}
                  onChange={handleInputChange}
                >
                  {dropdowns.weather_conditions.map(weather => (
                    <option key={weather} value={weather}>{weather}</option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label htmlFor="seasonality">Seasonality</label>
                <select
                  id="seasonality"
                  name="seasonality"
                  value={formData.seasonality}
                  onChange={handleInputChange}
                >
                  {dropdowns.seasonalities.map(season => (
                    <option key={season} value={season}>{season}</option>
                  ))}
                </select>
              </div>
            </div>

            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? 'Calculating...' : 'Calculate Resource Plan'}
            </button>
          </form>
        </div>

        {/* Results */}
        {error && (
          <div className="container">
            <div className="alert alert-error">
              <AlertCircle className="alert-icon" /> {error}
            </div>
          </div>
        )}

        {forecast && (
          <div className="forecast-results">
            {/* Summary Cards */}
            <div className="results-summary">
              <div className="summary-card">
                <TrendingUp className="summary-icon" size={32} />
                <div>
                  <p className="summary-label">Total Resource Needed</p>
                  <p className="summary-value">
                    {forecast.summary.total_resource_needed.toLocaleString()}
                  </p>
                </div>
              </div>
              <div className="summary-card">
                <TrendingUp className="summary-icon" size={32} />
                <div>
                  <p className="summary-label">Current Stock</p>
                  <p className="summary-value">
                    {forecast.summary.current_stock.toLocaleString()}
                  </p>
                </div>
              </div>
              <div className="summary-card">
                <TrendingUp className="summary-icon" size={32} />
                <div>
                  <p className="summary-label">Additional Needed</p>
                  <p className="summary-value">
                    {forecast.summary.additional_needed.toLocaleString()}
                  </p>
                </div>
              </div>
            </div>

            {/* Status Alert */}
            {forecast.summary.additional_needed > 0 ? (
              <div className="alert alert-warning">
                ⚠️ Stock is short by {forecast.summary.additional_needed.toLocaleString()} units for the selected period.
              </div>
            ) : (
              <div className="alert alert-success">
                ✓ Current stock is sufficient for the selected period.
              </div>
            )}

            {/* Forecast Table */}
            <div className="section-container">
              <h3 className="table-title">📈 Detailed Forecast</h3>
              <div className="table-wrapper">
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Date</th>
                      <th>Current Stock</th>
                      <th>Expected Usage</th>
                      <th>Closing Stock</th>
                      <th>Total Usage Till Date</th>
                      <th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {forecast.forecast.map((row, idx) => (
                      <tr key={idx} className={row.stock_status === 'Shortage' ? 'row-danger' : ''}>
                        <td>{row.date}</td>
                        <td>{row.current_stock.toLocaleString()}</td>
                        <td>{row.expected_usage.toLocaleString()}</td>
                        <td>{row.closing_stock.toLocaleString()}</td>
                        <td>{row.total_usage_till_date.toLocaleString()}</td>
                        <td>
                          <span className={`status-badge status-${row.stock_status.toLowerCase()}`}>
                            {row.stock_status}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
