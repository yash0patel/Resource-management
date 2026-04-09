import React from 'react';
import { Github, Mail, Linkedin, Phone, Globe } from 'lucide-react';
import './Contact.css';

export default function Contact() {
  const contactLinks = [
    {
      icon: Github,
      label: 'GitHub Repository',
      value: 'github.com/yash0patel/Resource-management',
      link: 'https://github.com/yash0patel/Resource-management',
      color: '#0f172a'
    },
    {
      icon: Linkedin,
      label: 'LinkedIn',
      value: 'linkedin.com/in/yashpatel2k26',
      link: 'https://www.linkedin.com/in/yashpatel2k26/',
      color: '#0077b5'
    },
    {
      icon: Mail,
      label: 'Email Support',
      value: 'yashpatelrupal@gmail.com',
      link: 'mailto:yashpatelrupal@gmail.com',
      color: '#ea4335'
    },
    {
      icon: Phone,
      label: 'Call Us',
      value: '+91 9313120390',
      link: 'tel:+919313120390',
      color: '#34a853'
    },
  ];

  return (
    <div className="contact-page animate-fade">
      <header className="header-container">
        <div className="header-tag">Support</div>
        <h1 className="header-title">Get In Touch</h1>
        <p className="header-subtitle">Professional support and collaboration channels.</p>
      </header>

      <div className="container">
        <div className="contact-links-grid">
          {contactLinks.map((contact, idx) => {
            const Icon = contact.icon;
            return (
              <a
                key={idx}
                href={contact.link}
                className="contact-card"
                target="_blank"
                rel="noopener noreferrer"
              >
                <div className="contact-icon-wrapper" style={{ color: contact.color }}>
                  <Icon size={24} />
                </div>
                <div className="contact-text">
                  <span className="contact-label">{contact.label}</span>
                  <p className="contact-value">{contact.value}</p>
                </div>
              </a>
            );
          })}
        </div>
      </div>
    </div>
  );
}
