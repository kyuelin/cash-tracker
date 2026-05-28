import React, { useState, useEffect } from 'react';
import { Wallet, History, BarChart3 } from 'lucide-react';
import TransactionForm from './components/TransactionForm';
import TransactionHistory from './components/TransactionHistory';
import Analytics from './components/Analytics';
import './App.css';

function App() {
  const [activeTab, setActiveTab] = useState('entry');
  const [balance, setBalance] = useState({
    total_balance: 0,
    monthly_balance: 0,
    monthly_spent: 0,
    monthly_received: 0
  });

  const fetchBalance = async () => {
    try {
      const response = await fetch('/api/balance');
      const data = await response.json();
      setBalance(data);
    } catch (error) {
      console.error('Error fetching balance:', error);
    }
  };

  useEffect(() => {
    fetchBalance();
  }, []);

  const tabs = [
    { id: 'entry', label: 'New Transaction', icon: Wallet },
    { id: 'history', label: 'History', icon: History },
    { id: 'analytics', label: 'Analytics', icon: BarChart3 }
  ];

  const renderContent = () => {
    switch (activeTab) {
      case 'entry':
        return <TransactionForm onTransactionAdded={fetchBalance} balance={balance} />;
      case 'history':
        return <TransactionHistory />;
      case 'analytics':
        return <Analytics />;
      default:
        return <TransactionForm onTransactionAdded={fetchBalance} balance={balance} />;
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount || 0);
  };

  const currentMonth = new Date().toLocaleString('default', { month: 'long', year: 'numeric' });

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <div className="flex justify-between items-center">
            <h1 className="text-2xl font-bold text-gray-900">Cash Tracker</h1>
            <div className="flex space-x-6 text-sm">
              <div className="text-center">
                <div className="text-gray-500">Total Balance</div>
                <div className={`font-semibold ${balance.total_balance >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {formatCurrency(balance.total_balance)}
                </div>
              </div>
              <div className="text-center">
                <div className="text-gray-500">{currentMonth}</div>
                <div className={`font-semibold ${balance.monthly_balance >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {formatCurrency(balance.monthly_balance)}
                </div>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <nav className="bg-white border-b">
        <div className="max-w-4xl mx-auto px-4">
          <div className="flex space-x-8">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 py-4 px-2 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <tab.icon className="w-4 h-4" />
                <span>{tab.label}</span>
              </button>
            ))}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 py-6">
        {renderContent()}
      </main>
    </div>
  );
}

export default App;