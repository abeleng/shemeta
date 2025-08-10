import React from 'react';
import { MapPin, TrendingUp, Users, Plus, Bell } from 'lucide-react';

interface FarmerDashboardProps {
  onNavigate: (page: string) => void;
  landDetails: any[];
  recommendations: { [kebeleId: string]: any[] };
  matches: any[];
}

export default function FarmerDashboard({ onNavigate, landDetails, recommendations, matches }: FarmerDashboardProps) {
  // Compute stats from real data
  const recommendedCrops = Object.values(recommendations).reduce((acc, crops) => acc + crops.length, 0);
  const activeBuyerOffers = matches.length;
  const totalEarnings = matches.reduce((sum, m) => sum + (m.requirement?.price_per_kg ?? 0) * (m.requirement?.quantity ?? 0), 0);

  // Recent offers: show the latest 2 matches
  const recentOffers = matches.slice(0, 2).map((match) => ({
    id: match.match_id,
    buyerName: match.exporter,
    crop: match.crop_name,
    quantity: match.requirement?.quantity,
    pricePerKg: match.requirement?.price_per_kg,
    status: match.status
  }));

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Welcome Section */}
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-gray-900">Farmer Dashboard</h2>
        <p className="text-gray-600 mt-2">
          {landDetails[0]?.region || "Your Region"} • Manage your farm and connect with buyers
        </p>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center">
            <div className="p-3 bg-green-100 rounded-lg">
              <TrendingUp className="h-6 w-6 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Recommended Crops</p>
              <p className="text-2xl font-bold text-gray-900">{recommendedCrops}</p>
              <p className="text-sm text-green-600">This season</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center">
            <div className="p-3 bg-blue-100 rounded-lg">
              <Users className="h-6 w-6 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Active Buyer Offers</p>
              <p className="text-2xl font-bold text-gray-900">{activeBuyerOffers}</p>
              <p className="text-sm text-blue-600">Waiting for response</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center">
            <div className="p-3 bg-yellow-100 rounded-lg">
              <span className="text-yellow-600 text-xl">💰</span>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Potential Earnings</p>
              <p className="text-2xl font-bold text-gray-900">{totalEarnings.toLocaleString()} ETB</p>
              <p className="text-sm text-yellow-600">This season</p>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Offers */}
      {recentOffers.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm border p-6 mb-8">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center">
              <Bell className="h-5 w-5 mr-2 text-orange-500" />
              Recent Buyer Offers
            </h3>
            <button
              onClick={() => onNavigate('farmer-responses')}
              className="text-green-600 hover:text-green-700 text-sm font-medium"
            >
              View All
            </button>
          </div>
          <div className="space-y-3">
            {recentOffers.map((offer) => (
              <div key={offer.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div>
                  <p className="font-medium text-gray-900">{offer.buyerName}</p>
                  <p className="text-sm text-gray-600">
                    {offer.quantity} tons of {offer.crop} at {offer.pricePerKg} ETB/kg
                  </p>
                </div>
                <span className="bg-orange-100 text-orange-800 text-xs font-medium px-2 py-1 rounded-full">
                  {offer.status.charAt(0).toUpperCase() + offer.status.slice(1)}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Action Buttons */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <button
          onClick={() => onNavigate('add-land')}
          className="bg-green-600 hover:bg-green-700 text-white font-medium py-3 px-4 rounded-lg transition-colors flex items-center justify-center space-x-2"
        >
          <Plus className="h-5 w-5" />
          <span>Add My Land Details</span>
        </button>

        <button
          onClick={() => onNavigate('recommendations')}
          className="bg-white hover:bg-gray-50 text-gray-700 font-medium py-3 px-4 rounded-lg border border-gray-300 transition-colors flex items-center justify-center space-x-2"
        >
          <MapPin className="h-5 w-5" />
          <span>View Crop Recommendations</span>
        </button>
      </div>
    </div>
  );
}