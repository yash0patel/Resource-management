import React from 'react';
import { Database, LineChart, Shield, Zap, Server, Code } from 'lucide-react';
import './About.css';

export default function About() {
  const capabilities = [
    {
      icon: LineChart,
      title: 'Temporal Forecasting',
      description: 'Advanced time-series analysis utilizing ensemble models to capture seasonality, trends, and promotional impacts.'
    },
    {
      icon: Database,
      title: 'Stock Optimization',
      description: 'Algorithmic safety-stock calculation to maintain optimal service levels while minimizing capital tied in inventory.'
    },
    {
      icon: Shield,
      title: 'Data Persistence',
      description: 'Reliable and permanent storage of all inventory transactions to ensure historical data is never lost.'
    },
    {
      icon: Zap,
      title: 'Record Management',
      description: 'Streamlined process for staging and appending new inventory entries to keep your data accurate and current.'
    }
  ];

  return (
    <div className="about-page animate-fade">
      <header className="header-container">
        <div className="header-tag">Documentation</div>
        <h1 className="header-title">System Overview</h1>
        <p className="header-subtitle">Technical documentation and core functional capabilities of IMS.</p>
      </header>

      <div className="container">
        <div className="about-grid">
          <section className="section-container">
            <h2 className="section-title"><Server size={20} /> Mission Objective</h2>
            <div className="content-text">
              <p>
                The Intelligent Inventory Management System (IMS) is engineered to solve complex supply chain challenges through data-driven automation. By integrating predictive modeling directly into the inventory workflow, we eliminate the guesswork from resource planning.
              </p>
              <p>
                Our architecture focuses on reliability, accuracy, and performance, providing a stable foundation for retail operations of any scale.
              </p>
            </div>
          </section>

          <section className="section-container">
            <h2 className="section-title"><Code size={20} /> Core Stack</h2>
            <div className="tech-list">
              <div className="tech-group">
                <h4>Data Engine</h4>
                <p>FastAPI, Python 3.10, scikit-learn, Pandas</p>
              </div>
              <div className="tech-group">
                <h4>Interface</h4>
                <p>React 18, Vite, Modern CSS3</p>
              </div>
              <div className="tech-group">
                <h4>Architecture</h4>
                <p>Restful API, Asynchronous Processing, JSON Serialization</p>
              </div>
            </div>
          </section>
        </div>

        <section className="capabilities-section">
          <h2 className="section-title-alt">Functional Capabilities</h2>
          <div className="capabilities-grid">
            {capabilities.map((item, idx) => (
              <div key={idx} className="capability-card">
                <div className="capability-icon">
                  <item.icon size={20} />
                </div>
                <div className="capability-content">
                  <h3>{item.title}</h3>
                  <p>{item.description}</p>
                </div>
              </div>
            ))}
          </div>
        </section>

        <section className="metrics-section">
          <div className="metric-item">
            <span className="metric-value">84.4%</span>
            <span className="metric-label">Model Accuracy</span>
          </div>
          <div className="metric-item">
            <span className="metric-value">&lt; 25ms</span>
            <span className="metric-label">API Latency</span>
          </div>
          <div className="metric-item">
            <span className="metric-value">100%</span>
            <span className="metric-label">Record Integrity</span>
          </div>
        </section>
      </div>
    </div>
  );
}
