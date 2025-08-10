import React, { useEffect, useState } from 'react';
import { Users, FileText, Plus, Eye } from 'lucide-react';

interface BuyerDashboardProps {
  onNavigate: (page: string) => void;
}

export default function BuyerDashboard({ onNavigate }: BuyerDashboardProps) {
  const [stats, setStats] = useState({
    company: '',
    totalFarmersMatched: 0,
    activeOffers: 0,
    totalPurchases: 0,
  });

  useEffect(() => {
    const fetchExporterHome = async () => {
      const token = localStorage.getItem('token');
      const res = await fetch('http://127.0.0.1:8000/api/user/exporter_home/', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
      });
      if (res.ok) {
        const data = await res.json();
        setStats({
          company: data.company || 'Your Company',
          totalFarmersMatched: data.matches ? data.matches.length : 0,
          activeOffers: data.requirements ? data.requirements.length : 0,
          totalPurchases: data.total_purchases || 0,
        });
      }
    };
    fetchExporterHome();
  }, []);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Welcome Section */}
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-gray-900">Buyer Dashboard</h2>
        <p className="text-gray-600 mt-2">{stats.company} • Connect with quality farmers</p>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center">
            <div className="p-3 bg-blue-100 rounded-lg">
              <Users className="h-6 w-6 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Farmers Matched</p>
              <p className="text-2xl font-bold text-gray-900">{stats.totalFarmersMatched}</p>
              <p className="text-sm text-blue-600">Ready to supply</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center">
            <div className="p-3 bg-green-100 rounded-lg">
              <FileText className="h-6 w-6 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Active Offers Posted</p>
              <p className="text-2xl font-bold text-gray-900">{stats.activeOffers}</p>
              <p className="text-sm text-green-600">Seeking farmers</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center">
            <div className="p-3 bg-yellow-100 rounded-lg">
              <span className="text-yellow-600 text-xl">💰</span>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Purchases</p>
              <p className="text-2xl font-bold text-gray-900">{stats.totalPurchases.toLocaleString()} ETB</p>
              <p className="text-sm text-yellow-600">This year</p>
            </div>
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <button
          onClick={() => onNavigate('post-requirement')}
          className="bg-green-600 hover:bg-green-700 text-white font-medium py-3 px-4 rounded-lg transition-colors flex items-center justify-center space-x-2"
        >
          <Plus className="h-5 w-5" />
          <span>Post Crop Requirement</span>
        </button>

        <button
          onClick={() => onNavigate('matched-farmers')}
          className="bg-white hover:bg-gray-50 text-gray-700 font-medium py-3 px-4 rounded-lg border border-gray-300 transition-colors flex items-center justify-center space-x-2"
        >
          <Eye className="h-5 w-5" />
          <span>View Matched Farmers</span>
        </button>
      </div>
    </div>
  );
}