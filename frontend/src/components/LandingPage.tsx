import React from 'react';
import { ArrowRight, Leaf, TrendingUp, Users, MapPin, Shield, Award, Globe } from 'lucide-react';

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
          <div className="flex items-center justify-center mb-8 animate-fade-in">
            <Leaf className="h-16 w-16 text-green-400 mr-4" />
            <h1 className="text-5xl md:text-6xl font-bold text-white">Shemeta</h1>
          </div>

          {/* Main Title */}
          <h2 className="text-3xl md:text-5xl font-bold text-white mb-6 leading-tight animate-slide-up">
            AI-Powered Crop Recommendation &<br />
            Buyer-Farmer Matching
          </h2>

          {/* Subtitle */}
          <p className="text-xl md:text-2xl text-green-100 mb-12 max-w-3xl mx-auto animate-slide-up-delay">
            Grow smart. Sell smart. From plot to profit.
          </p>

          {/* CTA Button */}
          <button
            onClick={onGetStarted}
            className="bg-green-600 hover:bg-green-700 text-white font-bold py-4 px-8 rounded-lg text-lg transition-all duration-300 transform hover:scale-105 shadow-lg hover:shadow-xl inline-flex items-center animate-bounce-subtle"
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
            <div className="bg-white rounded-lg shadow-lg p-8 text-center hover:shadow-xl transition-all duration-300 transform hover:-translate-y-2">
              <div className="bg-green-100 rounded-full p-4 w-16 h-16 mx-auto mb-6">
                <TrendingUp className="h-8 w-8 text-green-600" />
              </div>
              <h4 className="text-xl font-bold text-gray-900 mb-4">Smart Crop Recommendations</h4>
              <p className="text-gray-600">
                AI-powered analysis of soil, climate, and market data to recommend the most profitable crops for your land.
              </p>
            </div>

            {/* Feature 2 */}
            <div className="bg-white rounded-lg shadow-lg p-8 text-center hover:shadow-xl transition-all duration-300 transform hover:-translate-y-2">
              <div className="bg-green-100 rounded-full p-4 w-16 h-16 mx-auto mb-6">
                <Users className="h-8 w-8 text-green-600" />
              </div>
              <h4 className="text-xl font-bold text-gray-900 mb-4">Direct Buyer Matching</h4>
              <p className="text-gray-600">
                Connect directly with verified buyers who need your crops, eliminating middlemen and maximizing profits.
              </p>
            </div>

            {/* Feature 3 */}
            <div className="bg-white rounded-lg shadow-lg p-8 text-center hover:shadow-xl transition-all duration-300 transform hover:-translate-y-2">
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

      {/* Image Gallery Section */}
      <div className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h3 className="text-3xl font-bold text-gray-900 mb-4">
              Transforming Agriculture Across Ethiopia
            </h3>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              From traditional farming to modern agricultural practices, we're helping farmers thrive.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {/* Image 1 */}
            <div className="relative overflow-hidden rounded-lg shadow-lg group">
              <img
                src="https://images.pexels.com/photos/1595104/pexels-photo-1595104.jpeg?auto=compress&cs=tinysrgb&w=800&h=600&fit=crop"
                alt="Ethiopian farmer in field"
                className="w-full h-64 object-cover transition-transform duration-300 group-hover:scale-110"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                <div className="absolute bottom-4 left-4 text-white">
                  <h4 className="font-semibold">Traditional Farming</h4>
                  <p className="text-sm">Honoring heritage while embracing innovation</p>
                </div>
              </div>
            </div>

            {/* Image 2 */}
            <div className="relative overflow-hidden rounded-lg shadow-lg group">
              <img
                src="https://images.pexels.com/photos/1595108/pexels-photo-1595108.jpeg?auto=compress&cs=tinysrgb&w=800&h=600&fit=crop"
                alt="Crop harvest"
                className="w-full h-64 object-cover transition-transform duration-300 group-hover:scale-110"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                <div className="absolute bottom-4 left-4 text-white">
                  <h4 className="font-semibold">Quality Harvest</h4>
                  <p className="text-sm">Premium crops for better market prices</p>
                </div>
              </div>
            </div>

            {/* Image 3 */}
            <div className="relative overflow-hidden rounded-lg shadow-lg group">
              <img
                src="https://images.pexels.com/photos/1595105/pexels-photo-1595105.jpeg?auto=compress&cs=tinysrgb&w=800&h=600&fit=crop"
                alt="Agricultural technology"
                className="w-full h-64 object-cover transition-transform duration-300 group-hover:scale-110"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                <div className="absolute bottom-4 left-4 text-white">
                  <h4 className="font-semibold">Modern Technology</h4>
                  <p className="text-sm">AI-powered agricultural solutions</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Statistics Section */}
      <div 
        className="py-20 bg-cover bg-center bg-no-repeat relative"
        style={{
          backgroundImage: `linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.7)), url('https://images.pexels.com/photos/1595103/pexels-photo-1595103.jpeg?auto=compress&cs=tinysrgb&w=1920&h=800&fit=crop')`
        }}
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h3 className="text-3xl font-bold text-white mb-4">
              Making a Real Impact
            </h3>
            <p className="text-xl text-green-100 max-w-3xl mx-auto">
              Join thousands of farmers and buyers who are already transforming Ethiopian agriculture.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div className="text-center">
              <div className="text-4xl font-bold text-green-400 mb-2">10,000+</div>
              <div className="text-white">Farmers Connected</div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold text-green-400 mb-2">500+</div>
              <div className="text-white">Verified Buyers</div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold text-green-400 mb-2">95%</div>
              <div className="text-white">Success Rate</div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold text-green-400 mb-2">₹2.5M</div>
              <div className="text-white">Total Transactions</div>
            </div>
          </div>
        </div>
      </div>

      {/* Benefits Section */}
      <div className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h3 className="text-3xl font-bold text-gray-900 mb-4">
              Why Choose Shemeta?
            </h3>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              We provide comprehensive solutions for modern agricultural challenges.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {/* Benefit 1 */}
            <div className="flex items-start space-x-4">
              <div className="bg-green-100 rounded-lg p-3">
                <Shield className="h-6 w-6 text-green-600" />
              </div>
              <div>
                <h4 className="text-lg font-semibold text-gray-900 mb-2">Verified Partners</h4>
                <p className="text-gray-600">All buyers and farmers are thoroughly verified for secure transactions.</p>
              </div>
            </div>

            {/* Benefit 2 */}
            <div className="flex items-start space-x-4">
              <div className="bg-green-100 rounded-lg p-3">
                <Award className="h-6 w-6 text-green-600" />
              </div>
              <div>
                <h4 className="text-lg font-semibold text-gray-900 mb-2">Quality Assurance</h4>
                <p className="text-gray-600">Maintain high standards with our quality control systems.</p>
              </div>
            </div>

            {/* Benefit 3 */}
            <div className="flex items-start space-x-4">
              <div className="bg-green-100 rounded-lg p-3">
                <Globe className="h-6 w-6 text-green-600" />
              </div>
              <div>
                <h4 className="text-lg font-semibold text-gray-900 mb-2">Market Access</h4>
                <p className="text-gray-600">Connect to local and international markets for better prices.</p>
              </div>
            </div>

            {/* Benefit 4 */}
            <div className="flex items-start space-x-4">
              <div className="bg-green-100 rounded-lg p-3">
                <TrendingUp className="h-6 w-6 text-green-600" />
              </div>
              <div>
                <h4 className="text-lg font-semibold text-gray-900 mb-2">Data-Driven Insights</h4>
                <p className="text-gray-600">Make informed decisions with real-time market data and analytics.</p>
              </div>
            </div>

            {/* Benefit 5 */}
            <div className="flex items-start space-x-4">
              <div className="bg-green-100 rounded-lg p-3">
                <Users className="h-6 w-6 text-green-600" />
              </div>
              <div>
                <h4 className="text-lg font-semibold text-gray-900 mb-2">Community Support</h4>
                <p className="text-gray-600">Join a thriving community of agricultural professionals.</p>
              </div>
            </div>

            {/* Benefit 6 */}
            <div className="flex items-start space-x-4">
              <div className="bg-green-100 rounded-lg p-3">
                <MapPin className="h-6 w-6 text-green-600" />
              </div>
              <div>
                <h4 className="text-lg font-semibold text-gray-900 mb-2">Local Expertise</h4>
                <p className="text-gray-600">Benefit from deep understanding of Ethiopian agricultural conditions.</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Call to Action Section */}
      <div 
        className="py-20 bg-cover bg-center bg-no-repeat relative"
        style={{
          backgroundImage: `linear-gradient(rgba(34, 197, 94, 0.9), rgba(22, 163, 74, 0.9)), url('https://images.pexels.com/photos/1595107/pexels-photo-1595107.jpeg?auto=compress&cs=tinysrgb&w=1920&h=800&fit=crop')`
        }}
      >
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h3 className="text-3xl md:text-4xl font-bold text-white mb-6">
            Ready to Transform Your Agricultural Business?
          </h3>
          <p className="text-xl text-green-100 mb-8 max-w-2xl mx-auto">
            Join thousands of farmers and buyers who are already using Shemeta to grow their agricultural success.
          </p>
          <button
            onClick={onGetStarted}
            className="bg-white hover:bg-gray-100 text-green-600 font-bold py-4 px-8 rounded-lg text-lg transition-all duration-300 transform hover:scale-105 shadow-lg hover:shadow-xl inline-flex items-center"
          >
            Start Your Journey Today
            <ArrowRight className="ml-2 h-5 w-5" />
          </button>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-green-800 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div className="col-span-2">
              <div className="flex items-center mb-4">
                <Leaf className="h-8 w-8 text-green-400 mr-2" />
                <span className="text-2xl font-bold">Shemeta</span>
              </div>
              <p className="text-green-200 mb-4">
                Transforming Ethiopian agriculture through technology, connecting farmers with buyers, and optimizing crop selection for maximum profitability.
              </p>
            </div>
            <div>
              <h4 className="text-lg font-semibold mb-4">For Farmers</h4>
              <ul className="space-y-2 text-green-200">
                <li>Crop Recommendations</li>
                <li>Buyer Matching</li>
                <li>Market Insights</li>
                <li>Quality Standards</li>
              </ul>
            </div>
            <div>
              <h4 className="text-lg font-semibold mb-4">For Buyers</h4>
              <ul className="space-y-2 text-green-200">
                <li>Farmer Network</li>
                <li>Quality Assurance</li>
                <li>Supply Chain</li>
                <li>Market Access</li>
              </ul>
            </div>
          </div>
          <div className="border-t border-green-700 mt-8 pt-8 text-center">
            <p className="text-green-200">
              © 2024 Shemeta. Transforming Ethiopian agriculture through technology.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
