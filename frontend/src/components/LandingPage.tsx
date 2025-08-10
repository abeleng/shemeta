import React from 'react';
import { ArrowRight, Leaf, TrendingUp, Users, MapPin } from 'lucide-react';

interface LandingPageProps {
  onGetStarted: () => void;
}

export default function LandingPage({ onGetStarted }: LandingPageProps) {
  return (
    <div className="min-h-screen bg-white">
      {/* Hero Section */}
      <div 
        className="relative bg-cover bg-center bg-no-repeat min-h-screen flex items-center"
        style={{
          backgroundImage: `linear-gradient(rgba(0, 0, 0, 0.4), rgba(0, 0, 0, 0.4)), url('https://images.pexels.com/photos/2132227/pexels-photo-2132227.jpeg?auto=compress&cs=tinysrgb&w=1920&h=1080&fit=crop')`
        }}
      >
        <div className="absolute inset-0 bg-gradient-to-r from-green-900/80 to-green-700/60"></div>
        
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          {/* Logo */}
          <div className="flex items-center justify-center mb-8">
            <Leaf className="h-16 w-16 text-green-400 mr-4" />
            <h1 className="text-5xl md:text-6xl font-bold text-white">Shemeta</h1>
          </div>

          {/* Main Title */}
          <h2 className="text-3xl md:text-5xl font-bold text-white mb-6 leading-tight">
            AI-Powered Crop Recommendation &<br />
            Buyer-Farmer Matching
          </h2>

          {/* Subtitle */}
          <p className="text-xl md:text-2xl text-green-100 mb-12 max-w-3xl mx-auto">
            Grow smart. Sell smart. From plot to profit.
          </p>

          {/* CTA Button */}
          <button
            onClick={onGetStarted}
            className="bg-green-600 hover:bg-green-700 text-white font-bold py-4 px-8 rounded-lg text-lg transition-all duration-300 transform hover:scale-105 shadow-lg hover:shadow-xl inline-flex items-center"
          >
            Get Started
            <ArrowRight className="ml-2 h-5 w-5" />
          </button>
        </div>
      </div>

      {/* Features Section */}
      <div className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h3 className="text-3xl font-bold text-gray-900 mb-4">
              Empowering Ethiopian Agriculture
            </h3>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Connect farmers with buyers, optimize crop selection, and maximize profits through intelligent recommendations.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* Feature 1 */}
            <div className="bg-white rounded-lg shadow-lg p-8 text-center hover:shadow-xl transition-shadow">
              <div className="bg-green-100 rounded-full p-4 w-16 h-16 mx-auto mb-6">
                <TrendingUp className="h-8 w-8 text-green-600" />
              </div>
              <h4 className="text-xl font-bold text-gray-900 mb-4">Smart Crop Recommendations</h4>
              <p className="text-gray-600">
                AI-powered analysis of soil, climate, and market data to recommend the most profitable crops for your land.
              </p>
            </div>

            {/* Feature 2 */}
            <div className="bg-white rounded-lg shadow-lg p-8 text-center hover:shadow-xl transition-shadow">
              <div className="bg-green-100 rounded-full p-4 w-16 h-16 mx-auto mb-6">
                <Users className="h-8 w-8 text-green-600" />
              </div>
              <h4 className="text-xl font-bold text-gray-900 mb-4">Direct Buyer Matching</h4>
              <p className="text-gray-600">
                Connect directly with verified buyers who need your crops, eliminating middlemen and maximizing profits.
              </p>
            </div>

            {/* Feature 3 */}
            <div className="bg-white rounded-lg shadow-lg p-8 text-center hover:shadow-xl transition-shadow">
              <div className="bg-green-100 rounded-full p-4 w-16 h-16 mx-auto mb-6">
                <MapPin className="h-8 w-8 text-green-600" />
              </div>
              <h4 className="text-xl font-bold text-gray-900 mb-4">Location-Based Insights</h4>
              <p className="text-gray-600">
                Get recommendations tailored to your specific location, soil type, and local market conditions.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-green-800 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <div className="flex items-center justify-center mb-4">
            <Leaf className="h-8 w-8 text-green-400 mr-2" />
            <span className="text-2xl font-bold">Shemeta</span>
          </div>
          <p className="text-green-200">
            Transforming Ethiopian agriculture through technology
          </p>
        </div>
      </footer>
    </div>
  );
}