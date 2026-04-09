import React from 'react';
import { Database, BarChart3, TrendingUp, Zap } from 'lucide-react';
import './Dashboard.css';

export default function Dashboard({ stats, setActivePage }) {
  return (
    <div className="dashboard animate-fade">
      <header className="header-container">
        <div className="header-tag">System Live</div>
        <h1 className="header-title">Management Dashboard</h1>
        <p className="header-subtitle">Real-time inventory metrics and predictive analytics overview.</p>
      </header>

      <div className="container">
        {stats && (
          <section className="section-container">
            <h2 className="section-title"><BarChart3 size={18} /> Operational Metrics</h2>
            <div className="stats-grid">
              <div className="stat-card">
                <span className="stat-label">Total Records</span>
                <p className="stat-value">{stats.total_records.toLocaleString()}</p>
              </div>
              <div className="stat-card">
                <span className="stat-label">Unique Stores</span>
                <p className="stat-value">{stats.unique_stores}</p>
              </div>
              <div className="stat-card">
                <span className="stat-label">Unique Products</span>
                <p className="stat-value">{stats.unique_products}</p>
              </div>
            </div>
          </section>
        )}

        <div className="dashboard-grid">
          <section className="section-container">
            <h2 className="section-title"><Zap size={18} /> Quick Operations</h2>
            <div className="action-list">
              <button className="action-item" onClick={() => setActivePage('forecast')}>
                <TrendingUp size={18} />
                <div className="action-text">
                  <span>Forecast Planner</span>
                  <p>Predict inventory requirements</p>
                </div>
              </button>
              <button className="action-item" onClick={() => setActivePage('records')}>
                <Database size={18} />
                <div className="action-text">
                  <span>Record Management</span>
                  <p>Batch update stock data</p>
                </div>
              </button>
            </div>
          </section>

          <section className="section-container">
            <h2 className="section-title"><Database size={18} /> System Status</h2>
            <div className="status-info">
              <div className="status-item">
                <span className="status-dot"></span>
                <p>Database Engine: Online</p>
              </div>
              <div className="status-item">
                <span className="status-dot"></span>
                <p>Prediction Engine: Ready</p>
              </div>
              <div className="status-item">
                <span className="status-dot"></span>
                <p>API Connectivity: Stabilized</p>
              </div>
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}
