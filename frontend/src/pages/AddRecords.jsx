import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Trash2, Plus, Database } from 'lucide-react';
import './AddRecords.css';

export default function AddRecords() {
  const [formData, setFormData] = useState({
    date: new Date().toISOString().split('T')[0],
    store_id: 'S001',
    product_id: 'P0001',
    category: 'Clothing',
    region: 'East',
    inventory_level: 0,
    units_sold: 0,
    units_ordered: 0,
    demand_forecast: 0,
    price: 0,
    discount: 0,
    weather_condition: 'Sunny',
    holiday_promotion: 0,
    competitor_pricing: 0,
    seasonality: 'Winter',
  });

  const [batch, setBatch] = useState([]);
  const [dropdowns, setDropdowns] = useState({
    categories: [],
    regions: [],
    weather_conditions: [],
    seasonalities: [],
    store_ids: [],
    product_ids: [],
  });

  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);

  useEffect(() => {
    fetchDropdowns();
  }, []);

  const fetchDropdowns = async () => {
    try {
      const response = await axios.get('/api/dropdowns');
      setDropdowns(response.data);
      if (response.data.store_ids.length > 0) {
        setFormData(prev => ({ ...prev, store_id: response.data.store_ids[0] }));
      }
      if (response.data.product_ids.length > 0) {
        setFormData(prev => ({ ...prev, product_id: response.data.product_ids[0] }));
      }
    } catch (err) {
      console.error('Error fetching dropdowns:', err);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: ['inventory_level', 'units_sold', 'units_ordered', 'holiday_promotion'].includes(name)
        ? parseInt(value) || 0
        : ['demand_forecast', 'price', 'discount', 'competitor_pricing'].includes(name)
        ? parseFloat(value) || 0
        : value
    }));
  };

  const handleAddRecord = (e) => {
    e.preventDefault();
    
    // Check for duplicates
    const isDuplicate = batch.some(record =>
      record.date === formData.date &&
      record.store_id === formData.store_id &&
      record.product_id === formData.product_id &&
      record.category === formData.category &&
      record.region === formData.region
    );

    if (isDuplicate) {
      setMessage({
        type: 'error',
        text: 'Duplicate record detected. A record with the same Date, Store ID, Product ID, Category, and Region already exists in the batch.'
      });
      setTimeout(() => setMessage(null), 5000);
      return;
    }

    setBatch(prev => [...prev, { ...formData }]);
    setMessage({
      type: 'success',
      text: 'Record added to batch. You can add more records or append the batch to CSV.'
    });
    setTimeout(() => setMessage(null), 5000);

    // Reset form to defaults
    setFormData(prev => ({
      date: new Date().toISOString().split('T')[0],
      store_id: dropdowns.store_ids[0] || 'S001',
      product_id: dropdowns.product_ids[0] || 'P0001',
      category: 'Clothing',
      region: 'East',
      inventory_level: 0,
      units_sold: 0,
      units_ordered: 0,
      demand_forecast: 0,
      price: 0,
      discount: 0,
      weather_condition: 'Sunny',
      holiday_promotion: 0,
      competitor_pricing: 0,
      seasonality: 'Winter',
    }));
  };

  const handleDeleteRecord = (index) => {
    setBatch(prev => prev.filter((_, i) => i !== index));
  };

  const handleSubmitBatch = async () => {
    setLoading(true);
    try {
      const response = await axios.post('/api/add-records', {
        records: batch
      });
      setMessage({
        type: 'success',
        text: `Successfully added ${response.data.count} records to CSV.`
      });
      setBatch([]);
      setTimeout(() => setMessage(null), 5000);
    } catch (err) {
      setMessage({
        type: 'error',
        text: err.response?.data?.detail || 'Error adding records'
      });
      setTimeout(() => setMessage(null), 5000);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="add-records animate-fade">
      <header className="header-container">
        <div className="header-tag">Data Entry</div>
        <h1 className="header-title">Record Management</h1>
        <p className="header-subtitle">Append new inventory data and manage temporal record staging.</p>
      </header>

      <div className="container">
        <div className="section-container">
          <h2 className="section-title"><Plus size={20} /> New Entry Configuration</h2>
          <p className="section-description" style={{ marginBottom: '2rem' }}>
            Fill in the daily inventory record details below. Use the buttons to stage records first, then append all staged records to the CSV file.
          </p>

          {message && (
            <div className={`alert alert-${message.type} animate-fade`}>
              <span className="alert-icon">{message.type === 'success' ? '✓' : '✕'}</span>
              <span className="alert-text">{message.text}</span>
            </div>
          )}

          <form onSubmit={handleAddRecord} className="inventory-form">
            {/* 1. Primary Identifiers */}
            <div className="form-group-section" style={{ marginBottom: '2rem' }}>
              <h4 className="form-group-title" style={{ marginBottom: '1rem', color: 'var(--primary)', fontSize: '0.85rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>1. Primary Identifiers</h4>
              <div className="form-row grid-3">
                <div className="form-group">
                  <label htmlFor="date">Date</label>
                  <input type="date" id="date" name="date" value={formData.date} onChange={handleInputChange} />
                </div>
                <div className="form-group">
                  <label htmlFor="store_id">Store ID</label>
                  <select id="store_id" name="store_id" value={formData.store_id} onChange={handleInputChange}>
                    {dropdowns.store_ids.map(id => <option key={id} value={id}>{id}</option>)}
                  </select>
                </div>
                <div className="form-group">
                  <label htmlFor="product_id">Product ID</label>
                  <select id="product_id" name="product_id" value={formData.product_id} onChange={handleInputChange}>
                    {dropdowns.product_ids.map(id => <option key={id} value={id}>{id}</option>)}
                  </select>
                </div>
              </div>
            </div>

            {/* 2. Categorization */}
            <div className="form-group-section" style={{ marginBottom: '2rem' }}>
              <h4 className="form-group-title" style={{ marginBottom: '1rem', color: 'var(--primary)', fontSize: '0.85rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>2. Classification</h4>
              <div className="form-row grid-2">
                <div className="form-group">
                  <label htmlFor="category">Category</label>
                  <select id="category" name="category" value={formData.category} onChange={handleInputChange}>
                    {dropdowns.categories.map(cat => <option key={cat} value={cat}>{cat}</option>)}
                  </select>
                </div>
                <div className="form-group">
                  <label htmlFor="region">Region</label>
                  <select id="region" name="region" value={formData.region} onChange={handleInputChange}>
                    {dropdowns.regions.map(reg => <option key={reg} value={reg}>{reg}</option>)}
                  </select>
                </div>
              </div>
            </div>

            {/* 3. Operational Metrics */}
            <div className="form-group-section" style={{ marginBottom: '2rem' }}>
              <h4 className="form-group-title" style={{ marginBottom: '1rem', color: 'var(--primary)', fontSize: '0.85rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>3. Inventory & Sales</h4>
              <div className="form-row grid-3">
                <div className="form-group">
                  <label htmlFor="inventory_level">Inventory Level</label>
                  <input type="number" id="inventory_level" name="inventory_level" value={formData.inventory_level} onChange={handleInputChange} min="0" />
                </div>
                <div className="form-group">
                  <label htmlFor="units_sold">Units Sold</label>
                  <input type="number" id="units_sold" name="units_sold" value={formData.units_sold} onChange={handleInputChange} min="0" />
                </div>
                <div className="form-group">
                  <label htmlFor="units_ordered">Units Ordered</label>
                  <input type="number" id="units_ordered" name="units_ordered" value={formData.units_ordered} onChange={handleInputChange} min="0" />
                </div>
              </div>
            </div>

            {/* 4. Financials */}
            <div className="form-group-section" style={{ marginBottom: '2rem' }}>
              <h4 className="form-group-title" style={{ marginBottom: '1rem', color: 'var(--primary)', fontSize: '0.85rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>4. Financial Data</h4>
              <div className="form-row grid-3">
                <div className="form-group">
                  <label htmlFor="price">Price ($)</label>
                  <input type="number" id="price" name="price" value={formData.price} onChange={handleInputChange} min="0" step="0.01" />
                </div>
                <div className="form-group">
                  <label htmlFor="discount">Discount</label>
                  <input type="number" id="discount" name="discount" value={formData.discount} onChange={handleInputChange} min="0" step="0.01" />
                </div>
                <div className="form-group">
                  <label htmlFor="competitor_pricing">Comp. Price ($)</label>
                  <input type="number" id="competitor_pricing" name="competitor_pricing" value={formData.competitor_pricing} onChange={handleInputChange} min="0" step="0.01" />
                </div>
              </div>
            </div>

          {/* 5. Environmental & Strategy */}
          <div className="form-group-section" style={{ marginBottom: '2rem' }}>
            <h4 className="form-group-title" style={{ marginBottom: '1rem', color: 'var(--primary)', fontSize: '0.85rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>5. Environment & Strategy</h4>
            <div className="form-row grid-4">
              <div className="form-group">
                <label htmlFor="weather_condition">Weather</label>
                <select id="weather_condition" name="weather_condition" value={formData.weather_condition} onChange={handleInputChange}>
                  {dropdowns.weather_conditions.map(w => <option key={w} value={w}>{w}</option>)}
                </select>
              </div>
              <div className="form-group">
                <label htmlFor="seasonality">Seasonality</label>
                <select id="seasonality" name="seasonality" value={formData.seasonality} onChange={handleInputChange}>
                  {dropdowns.seasonalities.map(s => <option key={s} value={s}>{s}</option>)}
                </select>
              </div>
              <div className="form-group">
                <label htmlFor="holiday_promotion">Holiday Promotion</label>
                <select id="holiday_promotion" name="holiday_promotion" value={formData.holiday_promotion} onChange={handleInputChange}>
                  <option value="0">No</option>
                  <option value="1">Yes</option>
                </select>
              </div>
              <div className="form-group">
                <label htmlFor="demand_forecast">Sales Forecast</label>
                <input type="number" id="demand_forecast" name="demand_forecast" value={formData.demand_forecast} onChange={handleInputChange} min="0" step="0.01" />
              </div>
            </div>
          </div>

          <button type="submit" className="btn btn-primary" style={{ width: '100%', padding: '1.25rem' }}>
            <Plus size={20} style={{ marginRight: '0.75rem' }} /> Add record to batch
          </button>
        </form>
      </div>

      {/* Batch Display */}
      {batch.length > 0 && (
        <div className="section-container" style={{ padding: '2.5rem 0' }}>
          <h2 className="section-title" style={{ padding: '0 2.5rem' }}><Database size={20} /> Staged Records Buffer</h2>
          
          <div className="table-wrapper" style={{ overflowX: 'auto', borderTop: '1px solid var(--border)', marginTop: '1.5rem' }}>
            <table className="data-table staged-table" style={{ border: 'none' }}>
              <thead>
                <tr>
                  <th style={{ paddingLeft: '2.5rem' }}>Date</th>
                  <th>ID (S/P)</th>
                  <th>Cat/Reg</th>
                  <th>Inv/Sold/Ord</th>
                  <th>Price/Disc</th>
                  <th>Forecast</th>
                  <th>Weather/Seas</th>
                  <th>Holiday Promo</th>
                  <th>Comp.</th>
                  <th style={{ paddingRight: '2.5rem' }}>Action</th>
                </tr>
              </thead>
              <tbody>
                {batch.map((record, idx) => (
                  <tr key={idx}>
                    <td style={{ paddingLeft: '2.5rem' }}><span style={{ fontSize: '0.85rem', fontWeight: 700 }}>{record.date}</span></td>
                    <td>
                      <div className="multiplex-cell" style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
                        <span style={{ fontSize: '0.8rem', fontWeight: 800, color: 'var(--text-main)' }}>{record.store_id}</span>
                        <span style={{ fontSize: '0.75rem', color: 'var(--text-light)' }}>{record.product_id}</span>
                      </div>
                    </td>
                    <td>
                      <div className="multiplex-cell" style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
                        <span style={{ fontSize: '0.8rem', fontWeight: 800, color: 'var(--text-main)' }}>{record.category}</span>
                        <span style={{ fontSize: '0.75rem', color: 'var(--text-light)' }}>{record.region}</span>
                      </div>
                    </td>
                    <td>
                      <div className="multiplex-cell" style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
                        <span style={{ fontSize: '0.8rem', fontWeight: 800, color: 'var(--success)' }}>{record.inventory_level}</span>
                        <span style={{ fontSize: '0.75rem', color: 'var(--text-light)' }}>S: {record.units_sold} | O: {record.units_ordered}</span>
                      </div>
                    </td>
                    <td>
                      <div className="multiplex-cell" style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
                        <span style={{ fontSize: '0.8rem', fontWeight: 800, color: 'var(--text-main)' }}>${record.price.toFixed(2)}</span>
                        <span style={{ fontSize: '0.75rem', color: 'var(--danger)' }}>-${record.discount}</span>
                      </div>
                    </td>
                    <td><span style={{ fontWeight: 800 }}>{record.demand_forecast.toFixed(1)}</span></td>
                    <td>
                      <div className="multiplex-cell" style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
                        <span style={{ fontSize: '0.8rem', fontWeight: 800, color: 'var(--text-main)' }}>{record.weather_condition}</span>
                        <span style={{ fontSize: '0.75rem', color: 'var(--text-light)' }}>{record.seasonality}</span>
                      </div>
                    </td>
                    <td>
                      <span style={{ 
                        fontSize: '0.7rem', 
                        fontWeight: 800, 
                        padding: '0.2rem 0.5rem', 
                        borderRadius: '4px',
                        background: record.holiday_promotion === 1 ? 'var(--primary-light)' : '#f1f5f9',
                        color: record.holiday_promotion === 1 ? 'var(--primary)' : 'var(--text-light)'
                      }}>
                        {record.holiday_promotion === 1 ? 'Yes' : 'No'}
                      </span>
                    </td>
                    <td><span style={{ fontSize: '0.85rem', fontWeight: 600 }}>${record.competitor_pricing.toFixed(2)}</span></td>
                    <td style={{ paddingRight: '2.5rem' }}>
                      <button className="btn-icon btn-danger-icon" onClick={() => handleDeleteRecord(idx)} style={{ color: 'var(--danger)', background: 'transparent', border: 'none', cursor: 'pointer' }}>
                        <Trash2 size={16} />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

            <div className="batch-actions" style={{ padding: '2rem 2.5rem 0 2.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: '0.9rem', fontWeight: 700, color: 'var(--text-light)' }}>{batch.length} record{batch.length !== 1 ? 's' : ''} staged for append</span>
              <button 
                onClick={handleSubmitBatch} 
                className="btn btn-primary" 
                disabled={loading || batch.length === 0}
                style={{ padding: '0.75rem 2rem' }}
              >
                {loading ? 'Processing...' : 'Commit Batch to CSV'}
              </button>
            </div>
          </div>
        )}

        {batch.length === 0 && (
          <div className="alert alert-info" style={{ marginTop: '2rem' }}>
            Info: Buffer is currently empty. Add records above to stage them for the CSV append operation.
          </div>
        )}
      </div>
    </div>
  );
}
