import React, { useState } from 'react';
import { ArrowLeft, Leaf, User, Users } from 'lucide-react';

interface AuthPageProps {
  onAuth: (userData: { name: string; type: 'farmer' | 'buyer' }) => void;
  onBack: () => void;
}

export default function AuthPage({ onAuth, onBack }: AuthPageProps) {
  const [isLogin, setIsLogin] = useState(true);
  const [userType, setUserType] = useState<'farmer' | 'buyer'>('farmer');
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: ''
  });

  const roleMap = {
    farmer: 'FARMER',
    buyer: 'EXPORTER'
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.name || !formData.email || !formData.password) {
      alert('Please fill in all required fields');
      return;
    }

    if (!isLogin && formData.password !== formData.confirmPassword) {
      alert('Passwords do not match');
      return;
    }

    const payload = {
      username: formData.email,
      password: formData.password,
      role: roleMap[userType],
      // add other fields as needed
    };

    const url = isLogin
      ? 'http://127.0.0.1:8000/api/user/login/'
      : 'http://127.0.0.1:8000/api/user/register/';

    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (res.status === 200 || res.status === 201) {
      const data = await res.json();
      // Store JWT token for authenticated requests
      if (data.access) {
        localStorage.setItem('token', data.access);
      } else if (data.token) {
        localStorage.setItem('token', data.token);
      }
      onAuth({
        name: formData.name || (userType === 'farmer' ? 'Abebe Kebede' : 'Almaz Trading'),
        type: userType
      });
      // Redirect based on role
      if (userType === 'farmer') {
        window.location.href = '/farmer/';
      } else {
        window.location.href = '/buyer/';
      }
    } else {
      const data = await res.json();
      alert(data.message || data.error);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      {/* Back Button */}
      <div className="absolute top-4 left-4">
        <button
          onClick={onBack}
          className="flex items-center text-gray-600 hover:text-gray-900 transition-colors"
        >
          <ArrowLeft className="h-5 w-5 mr-2" />
          Back to Home
        </button>
      </div>

      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        {/* Logo */}
        <div className="flex items-center justify-center mb-6">
          <Leaf className="h-12 w-12 text-green-600 mr-3" />
          <h1 className="text-3xl font-bold text-gray-900">Shemeta</h1>
        </div>

        <h2 className="text-center text-2xl font-bold text-gray-900">
          {isLogin ? 'Sign in to your account' : 'Create your account'}
        </h2>
        <p className="mt-2 text-center text-sm text-gray-600">
          {isLogin ? "Don't have an account? " : "Already have an account? "}
          <button
            onClick={() => setIsLogin(!isLogin)}
            className="font-medium text-green-600 hover:text-green-500"
          >
            {isLogin ? 'Sign up' : 'Sign in'}
          </button>
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
          {/* User Type Selection */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-3">
              I am a:
            </label>
            <div className="flex space-x-4">
              <button
                type="button"
                onClick={() => setUserType('farmer')}
                className={`flex-1 flex items-center justify-center py-3 px-4 rounded-lg border-2 transition-colors ${
                  userType === 'farmer'
                    ? 'border-green-600 bg-green-50 text-green-700'
                    : 'border-gray-300 bg-white text-gray-700 hover:border-gray-400'
                }`}
              >
                <User className="h-5 w-5 mr-2" />
                Farmer
              </button>
              <button
                type="button"
                onClick={() => setUserType('buyer')}
                className={`flex-1 flex items-center justify-center py-3 px-4 rounded-lg border-2 transition-colors ${
                  userType === 'buyer'
                    ? 'border-green-600 bg-green-50 text-green-700'
                    : 'border-gray-300 bg-white text-gray-700 hover:border-gray-400'
                }`}
              >
                <Users className="h-5 w-5 mr-2" />
                Buyer
              </button>
            </div>
          </div>

          <form className="space-y-6" onSubmit={handleSubmit}>
            <div>
              <label htmlFor="name" className="block text-sm font-medium text-gray-700">
                Full Name
              </label>
              <div className="mt-1">
                <input
                  id="name"
                  name="name"
                  type="text"
                  required
                  value={formData.name}
                  onChange={handleInputChange}
                  placeholder={userType === 'farmer' ? 'e.g., Abebe Kebede' : 'e.g., Almaz Trading Company'}
                  className="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md placeholder-gray-400 focus:outline-none focus:ring-green-500 focus:border-green-500"
                />
              </div>
            </div>

            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                Email address
              </label>
              <div className="mt-1">
                <input
                  id="email"
                  name="email"
                  type="email"
                  autoComplete="email"
                  required
                  value={formData.email}
                  onChange={handleInputChange}
                  className="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md placeholder-gray-400 focus:outline-none focus:ring-green-500 focus:border-green-500"
                />
              </div>
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                Password
              </label>
              <div className="mt-1">
                <input
                  id="password"
                  name="password"
                  type="password"
                  autoComplete="current-password"
                  required
                  value={formData.password}
                  onChange={handleInputChange}
                  className="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md placeholder-gray-400 focus:outline-none focus:ring-green-500 focus:border-green-500"
                />
              </div>
            </div>

            {!isLogin && (
              <div>
                <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700">
                  Confirm Password
                </label>
                <div className="mt-1">
                  <input
                    id="confirmPassword"
                    name="confirmPassword"
                    type="password"
                    required
                    value={formData.confirmPassword}
                    onChange={handleInputChange}
                    className="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md placeholder-gray-400 focus:outline-none focus:ring-green-500 focus:border-green-500"
                  />
                </div>
              </div>
            )}

            <div>
              <button
                type="submit"
                className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 transition-colors"
              >
                {isLogin ? 'Sign in' : 'Create account'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}