import React, { useState, useEffect } from 'react';
import { Plus, DollarSign } from 'lucide-react';

const TransactionForm = ({ onTransactionAdded, balance }) => {
  const [formData, setFormData] = useState({
    date: new Date().toISOString().split('T')[0],
    description: '',
    category: '',
    amount: ''
  });
  
  const [cashReceived, setCashReceived] = useState({
    date: new Date().toISOString().split('T')[0],
    description: 'Cash received',
    amount: ''
  });

  const [categories, setCategories] = useState([]);
  const [suggestions, setSuggestions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [suggestedCategory, setSuggestedCategory] = useState('');
  const [showCashForm, setShowCashForm] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    fetchCategories();
  }, []);

  const fetchCategories = async () => {
    try {
      const response = await fetch('/api/categories');
      const data = await response.json();
      setCategories(data.categories || []);
    } catch (error) {
      console.error('Error fetching categories:', error);
    }
  };

  const fetchSuggestions = async (query) => {
    if (query.length < 2) {
      setSuggestions([]);
      setShowSuggestions(false);
      return;
    }

    try {
      const response = await fetch(`/api/suggestions/description?query=${encodeURIComponent(query)}`);
      const data = await response.json();
      setSuggestions(data.suggestions || []);
      setShowSuggestions(data.suggestions.length > 0);
    } catch (error) {
      console.error('Error fetching suggestions:', error);
    }
  };

  const suggestCategory = async (description) => {
    if (!description) return;

    try {
      const response = await fetch('/api/suggestions/category', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ description })
      });
      const data = await response.json();
      setSuggestedCategory(data.suggested_category);
      
      if (data.suggested_category && !formData.category) {
        setFormData(prev => ({ ...prev, category: data.suggested_category }));
      }
    } catch (error) {
      console.error('Error getting category suggestion:', error);
    }
  };

  const handleDescriptionChange = (e) => {
    const value = e.target.value;
    setFormData(prev => ({ ...prev, description: value }));
    
    fetchSuggestions(value);
    
    // Debounce category suggestion
    clearTimeout(window.categoryTimeout);
    window.categoryTimeout = setTimeout(() => {
      suggestCategory(value);
    }, 500);
  };

  const handleSuggestionClick = (suggestion) => {
    setFormData(prev => ({ ...prev, description: suggestion }));
    setShowSuggestions(false);
    suggestCategory(suggestion);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (isSubmitting) return;

    setIsSubmitting(true);

    try {
      const response = await fetch('/api/transactions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });

      if (response.ok) {
        setFormData({
          date: new Date().toISOString().split('T')[0],
          description: '',
          category: '',
          amount: ''
        });
        setSuggestedCategory('');
        onTransactionAdded();
      } else {
        console.error('Error adding transaction');
      }
    } catch (error) {
      console.error('Error submitting transaction:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCashReceivedSubmit = async (e) => {
    e.preventDefault();
    if (isSubmitting) return;

    setIsSubmitting(true);

    try {
      const response = await fetch('/api/cash-received', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(cashReceived)
      });

      if (response.ok) {
        setCashReceived({
          date: new Date().toISOString().split('T')[0],
          description: 'Cash received',
          amount: ''
        });
        setShowCashForm(false);
        onTransactionAdded();
      } else {
        console.error('Error adding cash received');
      }
    } catch (error) {
      console.error('Error submitting cash received:', error);
    } finally {
      setIsSubmitting(false);
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
    <div className="space-y-6">
      {/* Balance Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Balance</p>
              <p className={`text-2xl font-bold ${balance.total_balance >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {formatCurrency(balance.total_balance)}
              </p>
            </div>
            <div className="p-3 bg-blue-100 rounded-full">
              <DollarSign className="w-6 h-6 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">{currentMonth}</p>
              <p className={`text-2xl font-bold ${balance.monthly_balance >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {formatCurrency(balance.monthly_balance)}
              </p>
              <p className="text-xs text-gray-500 mt-1">
                Received: {formatCurrency(balance.monthly_received)} | 
                Spent: {formatCurrency(balance.monthly_spent)}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex space-x-4">
        <button
          onClick={() => setShowCashForm(!showCashForm)}
          className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors"
        >
          <Plus className="w-4 h-4" />
          <span>Add Cash Received</span>
        </button>
      </div>

      {/* Cash Received Form */}
      {showCashForm && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Add Cash Received</h3>
          <form onSubmit={handleCashReceivedSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Date
                </label>
                <input
                  type="date"
                  value={cashReceived.date}
                  onChange={(e) => setCashReceived(prev => ({ ...prev, date: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Amount ($)
                </label>
                <input
                  type="number"
                  step="0.01"
                  value={cashReceived.amount}
                  onChange={(e) => setCashReceived(prev => ({ ...prev, amount: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="0.00"
                  required
                />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Description
              </label>
              <input
                type="text"
                value={cashReceived.description}
                onChange={(e) => setCashReceived(prev => ({ ...prev, description: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Cash received"
              />
            </div>
            <div className="flex space-x-3">
              <button
                type="submit"
                disabled={isSubmitting}
                className="flex-1 bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 disabled:opacity-50 transition-colors"
              >
                {isSubmitting ? 'Adding...' : 'Add Cash'}
              </button>
              <button
                type="button"
                onClick={() => setShowCashForm(false)}
                className="px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Transaction Form */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Add New Purchase</h3>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Date
              </label>
              <input
                type="date"
                value={formData.date}
                onChange={(e) => setFormData(prev => ({ ...prev, date: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Amount ($)
              </label>
              <input
                type="number"
                step="0.01"
                value={formData.amount}
                onChange={(e) => setFormData(prev => ({ ...prev, amount: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="0.00"
                required
              />
            </div>
          </div>

          <div className="relative">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Description
            </label>
            <input
              type="text"
              value={formData.description}
              onChange={handleDescriptionChange}
              onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
              onFocus={() => suggestions.length > 0 && setShowSuggestions(true)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="What did you buy?"
              required
            />
            {showSuggestions && suggestions.length > 0 && (
              <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-md shadow-lg max-h-48 overflow-y-auto">
                {suggestions.map((suggestion, index) => (
                  <button
                    key={index}
                    type="button"
                    onClick={() => handleSuggestionClick(suggestion)}
                    className="w-full px-3 py-2 text-left hover:bg-gray-50 focus:bg-gray-50 focus:outline-none"
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Category
              {suggestedCategory && (
                <span className="text-blue-600 text-xs ml-2">
                  (Suggested: {suggestedCategory})
                </span>
              )}
            </label>
            <select
              value={formData.category}
              onChange={(e) => setFormData(prev => ({ ...prev, category: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            >
              <option value="">Select a category</option>
              {categories.map((category) => (
                <option key={category} value={category}>
                  {category}
                </option>
              ))}
            </select>
          </div>

          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 transition-colors"
          >
            {isSubmitting ? 'Adding Transaction...' : 'Add Transaction'}
          </button>
        </form>
      </div>

      {/* Real-time Balance Preview */}
      {formData.amount && (
        <div className="bg-gray-50 rounded-lg p-4">
          <h4 className="text-sm font-medium text-gray-700 mb-2">Balance Preview</h4>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-gray-600">Current Total: </span>
              <span className={balance.total_balance >= 0 ? 'text-green-600' : 'text-red-600'}>
                {formatCurrency(balance.total_balance)}
              </span>
            </div>
            <div>
              <span className="text-gray-600">After Purchase: </span>
              <span className={balance.total_balance - parseFloat(formData.amount || 0) >= 0 ? 'text-green-600' : 'text-red-600'}>
                {formatCurrency(balance.total_balance - parseFloat(formData.amount || 0))}
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TransactionForm;