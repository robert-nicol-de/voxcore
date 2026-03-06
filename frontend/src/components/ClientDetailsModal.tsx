import React from 'react';
import './ClientDetailsModal.css';

interface ClientDetailsModalProps {
  isOpen: boolean;
  clientName: string;
  clientValue: number;
  chartType: string;
  chartTitle: string;
  onClose: () => void;
}

export const ClientDetailsModal: React.FC<ClientDetailsModalProps> = ({
  isOpen,
  clientName,
  clientValue,
  chartType,
  chartTitle,
  onClose,
}) => {
  if (!isOpen) return null;

  // Mock client data - in production, this would come from an API
  const mockClientData = {
    name: clientName,
    value: clientValue,
    status: 'Active',
    joinDate: '2022-03-15',
    industry: 'Technology',
    location: 'San Francisco, CA',
    email: 'contact@' + clientName.toLowerCase().replace(/\s+/g, '') + '.com',
    phone: '+1 (555) 123-4567',
    website: 'www.' + clientName.toLowerCase().replace(/\s+/g, '') + '.com',
    employees: Math.floor(Math.random() * 5000) + 100,
    annualRevenue: '$' + (clientValue * 1000).toLocaleString(),
    accountManager: 'Sarah Johnson',
    lastContact: '2024-02-28',
    nextReview: '2024-03-15',
    notes: 'High-value client with strong growth trajectory. Excellent payment history.',
    contacts: [
      { name: 'John Smith', title: 'CEO', email: 'john@example.com', phone: '+1 (555) 111-1111' },
      { name: 'Jane Doe', title: 'CFO', email: 'jane@example.com', phone: '+1 (555) 222-2222' },
      { name: 'Mike Wilson', title: 'CTO', email: 'mike@example.com', phone: '+1 (555) 333-3333' },
    ],
    recentTransactions: [
      { date: '2024-02-25', type: 'Invoice', amount: '$45,000', status: 'Paid' },
      { date: '2024-02-15', type: 'Payment', amount: '$45,000', status: 'Completed' },
      { date: '2024-01-25', type: 'Invoice', amount: '$45,000', status: 'Paid' },
      { date: '2024-01-15', type: 'Payment', amount: '$45,000', status: 'Completed' },
    ],
  };

  return (
    <div className="client-modal-overlay" onClick={onClose}>
      <div className="client-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div>
            <h1>{clientName}</h1>
            <p className="modal-subtitle">Detailed Client Information</p>
          </div>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>

        <div className="modal-content">
          {/* Overview Section */}
          <div className="section">
            <h2>📊 Overview</h2>
            <div className="overview-grid">
              <div className="overview-item">
                <div className="label">Status</div>
                <div className="value status-active">{mockClientData.status}</div>
              </div>
              <div className="overview-item">
                <div className="label">Value</div>
                <div className="value">${clientValue.toLocaleString()}</div>
              </div>
              <div className="overview-item">
                <div className="label">Join Date</div>
                <div className="value">{mockClientData.joinDate}</div>
              </div>
              <div className="overview-item">
                <div className="label">Industry</div>
                <div className="value">{mockClientData.industry}</div>
              </div>
              <div className="overview-item">
                <div className="label">Location</div>
                <div className="value">{mockClientData.location}</div>
              </div>
              <div className="overview-item">
                <div className="label">Employees</div>
                <div className="value">{mockClientData.employees.toLocaleString()}</div>
              </div>
            </div>
          </div>

          {/* Contact Information */}
          <div className="section">
            <h2>📞 Contact Information</h2>
            <div className="contact-info">
              <div className="info-row">
                <span className="label">Email:</span>
                <span className="value">{mockClientData.email}</span>
              </div>
              <div className="info-row">
                <span className="label">Phone:</span>
                <span className="value">{mockClientData.phone}</span>
              </div>
              <div className="info-row">
                <span className="label">Website:</span>
                <span className="value">{mockClientData.website}</span>
              </div>
              <div className="info-row">
                <span className="label">Annual Revenue:</span>
                <span className="value">{mockClientData.annualRevenue}</span>
              </div>
            </div>
          </div>

          {/* Account Management */}
          <div className="section">
            <h2>👤 Account Management</h2>
            <div className="contact-info">
              <div className="info-row">
                <span className="label">Account Manager:</span>
                <span className="value">{mockClientData.accountManager}</span>
              </div>
              <div className="info-row">
                <span className="label">Last Contact:</span>
                <span className="value">{mockClientData.lastContact}</span>
              </div>
              <div className="info-row">
                <span className="label">Next Review:</span>
                <span className="value">{mockClientData.nextReview}</span>
              </div>
            </div>
          </div>

          {/* Key Contacts */}
          <div className="section">
            <h2>👥 Key Contacts</h2>
            <div className="contacts-list">
              {mockClientData.contacts.map((contact, idx) => (
                <div key={idx} className="contact-card">
                  <div className="contact-name">{contact.name}</div>
                  <div className="contact-title">{contact.title}</div>
                  <div className="contact-details">
                    <div>📧 {contact.email}</div>
                    <div>📱 {contact.phone}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Recent Transactions */}
          <div className="section">
            <h2>💰 Recent Transactions</h2>
            <div className="transactions-table">
              <div className="table-header">
                <div className="col-date">Date</div>
                <div className="col-type">Type</div>
                <div className="col-amount">Amount</div>
                <div className="col-status">Status</div>
              </div>
              {mockClientData.recentTransactions.map((tx, idx) => (
                <div key={idx} className="table-row">
                  <div className="col-date">{tx.date}</div>
                  <div className="col-type">{tx.type}</div>
                  <div className="col-amount">{tx.amount}</div>
                  <div className="col-status">
                    <span className={`status-badge ${tx.status.toLowerCase()}`}>
                      {tx.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Notes */}
          <div className="section">
            <h2>📝 Notes</h2>
            <div className="notes-box">
              {mockClientData.notes}
            </div>
          </div>
        </div>

        <div className="modal-footer">
          <button className="btn-secondary" onClick={onClose}>Close</button>
          <button className="btn-primary">📧 Send Email</button>
          <button className="btn-primary">📞 Schedule Call</button>
        </div>
      </div>
    </div>
  );
};
