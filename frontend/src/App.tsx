import React, { useState } from 'react';
import { BrowserRouter, Routes, Route, useNavigate } from 'react-router-dom';
import LandingPage from './components/LandingPage';
import AuthPage from './components/AuthPage';
import FarmerView from './components/FarmerView';
import BuyerView from './components/BuyerView';
import { Leaf } from 'lucide-react';

function App() {
  const [user, setUser] = useState<{ name: string; type: 'farmer' | 'buyer' } | null>(null);

  return (
    <BrowserRouter>
      <Routes>
        <Route
          path="/"
          element={<LandingPage onGetStarted={() => window.location.href = '/auth'} />}
        />
        <Route
          path="/auth"
          element={
            <AuthPage
              onAuth={(userData) => {
                setUser(userData);
                if (userData.type === 'farmer') {
                  window.location.href = '/farmer';
                } else {
                  window.location.href = '/buyer';
                }
              }}
              onBack={() => window.location.href = '/'}
            />
          }
        />
        <Route
          path="/farmer"
          element={
            <div className="min-h-screen bg-gray-50">
              <Header user={user} onLogout={() => {
                setUser(null);
                window.location.href = '/';
              }} onToggleView={() => {}} />
              <FarmerView />
            </div>
          }
        />
        <Route
          path="/buyer"
          element={
            <div className="min-h-screen bg-gray-50">
              <Header user={user} onLogout={() => {
                setUser(null);
                window.location.href = '/';
              }} onToggleView={() => {}} />
              <BuyerView />
            </div>
          }
        />
      </Routes>
    </BrowserRouter>
  );
}

interface HeaderProps {
  user: { name: string; type: 'farmer' | 'buyer' } | null;
  onLogout: () => void;
  onToggleView: () => void;
}

function Header({ user, onLogout, onToggleView }: HeaderProps) {
  return (
    <header className="bg-white shadow-sm border-b">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center space-x-3">
            <Leaf className="h-8 w-8 text-green-600" />
            <h1 className="text-2xl font-bold text-gray-900">Shemeta</h1>
          </div>
          <div className="flex items-center space-x-4">
            <span className="text-sm text-gray-600">Welcome, {user?.name}</span>
            <button
              onClick={onLogout}
              className="text-sm text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md hover:bg-gray-100 transition-colors"
            >
              Logout
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}

export default App;