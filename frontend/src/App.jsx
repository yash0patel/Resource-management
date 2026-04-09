import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Package } from 'lucide-react';
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import ForecastPlanner from './pages/ForecastPlanner';
import AddRecords from './pages/AddRecords';
import About from './pages/About';
import Contact from './pages/Contact';
import './App.css';

export default function App() {
  const [activePage, setActivePage] = useState('dashboard');
  const [stats, setStats] = useState(null);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await axios.get('/api/stats');
      setStats(response.data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  return (
    <div className="app">
      {/* Navbar */}
      <Navbar activePage={activePage} setActivePage={setActivePage} />

      {/* Page Content */}
      {activePage === 'dashboard' && <Dashboard stats={stats} setActivePage={setActivePage} />}
      {activePage === 'forecast' && <ForecastPlanner />}
      {activePage === 'records' && <AddRecords />}
      {activePage === 'about' && <About />}
      {activePage === 'contact' && <Contact />}

      {/* Footer */}
      <footer className="footer">
        <div className="footer-content">
          <div className="footer-brand">
            <div className="footer-logo">
              <Package size={20} className="brand-icon" />
              <h3>IMS</h3>
            </div>
            <p>Enterprise-grade inventory management powered by predictive analytics and modern architecture.</p>
          </div>

          <div className="footer-links" style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '4rem' }}>
            <div className="footer-column">
              <h4>Navigation</h4>
              <button onClick={() => setActivePage('dashboard')} className="footer-link-btn">Dashboard</button>
              <button onClick={() => setActivePage('forecast')} className="footer-link-btn">Forecast Planner</button>
              <button onClick={() => setActivePage('records')} className="footer-link-btn">Record Management</button>
            </div>
            <div className="footer-column">
              <h4>Support</h4>
              <button onClick={() => setActivePage('about')} className="footer-link-btn">Documentation</button>
              <button onClick={() => setActivePage('contact')} className="footer-link-btn">Contact Us</button>
            </div>
            <div className="footer-column">
              <h4>Connect</h4>
              <a href="https://github.com/yash0patel/Resource-management" target="_blank" rel="noopener noreferrer">GitHub Profile</a>
              <a href="https://www.linkedin.com/in/yashpatel2k26/" target="_blank" rel="noopener noreferrer">LinkedIn Profile</a>
            </div>
          </div>
        </div>
        <div className="footer-bottom">
          <p>2026 Inventory Management System.</p>
        </div>
      </footer>
    </div>
  );
}
