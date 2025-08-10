import React, { useState } from 'react';
import { ArrowLeft, User, MapPin, TrendingUp, CheckCircle } from 'lucide-react';

interface MatchedFarmersProps {
  cropRequirement: any;
  onBack: () => void;
}

export default function MatchedFarmers({ cropRequirement, onBack }: MatchedFarmersProps) {
  const [sentOffers, setSentOffers] = useState<Set<number>>(new Set());

  // TODO: Replace with API call
  const matchedFarmers = [
    {
      id: 1,
      name: "Abebe Kebede",
      location: "Oromia Region, East Shewa Zone",
      suitability: 94,
      estimatedYield: 1.8,
      plotSize: 3.5,
      soilType: "vertisol",
      irrigationAvailable: false,
      experience: "8 years",
      rating: 4.8,
      phone: "+251-911-234567"
    },
    {
      id: 2,
      name: "Almaz Tesfaye",
      location: "Amhara Region, North Shewa Zone",
      suitability: 89,
      estimatedYield: 1.6,
      plotSize: 2.2,
      soilType: "cambisol",
      irrigationAvailable: true,
      experience: "5 years",
      rating: 4.6,
      phone: "+251-922-345678"
    },
    {
      id: 3,
      name: "Dawit Mulugeta",
      location: "Oromia Region, West Shewa Zone",
      suitability: 87,
      estimatedYield: 2.0,
      plotSize: 4.1,
      soilType: "nitisol",
      irrigationAvailable: false,
      experience: "12 years",
      rating: 4.9,
      phone: "+251-933-456789"
    },
    {
      id: 4,
      name: "Tigist Bekele",
      location: "SNNP Region, Hadiya Zone",
      suitability: 82,
      estimatedYield: 1.5,
      plotSize: 1.8,
      soilType: "luvisol",
      irrigationAvailable: true,
      experience: "6 years",
      rating: 4.4,
      phone: "+251-944-567890"
    }
  ];

  const handleSendOffer = (farmerId: number, farmerName: string) => {
    setSentOffers(prev => new Set([...prev, farmerId]));
    // Show confirmation
    alert(`Offer sent to ${farmerName}! They will be notified and can respond through the platform.`);
  };

  const getSuitabilityColor = (percentage: number) => {
    if (percentage >= 85) return 'text-green-600 bg-green-100';
    if (percentage >= 70) return 'text-orange-600 bg-orange-100';
    return 'text-red-600 bg-red-100';
  };

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="flex items-center mb-8">
        <button
          onClick={onBack}
          className="mr-4 p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
        >
          <ArrowLeft className="h-5 w-5" />
        </button>
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Matched Farmers</h2>
          <p className="text-gray-600">Farmers who can supply your crop requirements</p>
        </div>
      </div>

      {/* Requirement Summary */}
      {cropRequirement && (
        <div className="bg-blue-50 rounded-lg p-4 mb-6">
          <h3 className="font-medium text-gray-900 mb-2">Your Requirement: {cropRequirement.cropName}</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div>
              <span className="text-gray-600">Quantity:</span>
              <span className="ml-1 font-medium">{cropRequirement.quantity} tons</span>
            </div>
            <div>
              <span className="text-gray-600">Price:</span>
              <span className="ml-1 font-medium">{cropRequirement.pricePerKg} ETB/kg</span>
            </div>
            <div>
              <span className="text-gray-600">Harvest Date:</span>
              <span className="ml-1 font-medium">{new Date(cropRequirement.harvestDate).toLocaleDateString()}</span>
            </div>
            <div>
              <span className="text-gray-600">Region:</span>
              <span className="ml-1 font-medium">{cropRequirement.region === 'any' ? 'Any Region' : cropRequirement.region}</span>
            </div>
          </div>
        </div>
      )}

      {/* Farmers Table */}
      <div className="bg-white rounded-lg shadow-sm border overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Farmer
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Location
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Suitability
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Est. Yield
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Farm Details
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Action
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {matchedFarmers.map((farmer) => (
                <tr key={farmer.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="p-2 bg-gray-100 rounded-lg mr-3">
                        <User className="h-4 w-4 text-gray-600" />
                      </div>
                      <div>
                        <div className="text-sm font-medium text-gray-900">{farmer.name}</div>
                        <div className="text-sm text-gray-500">{farmer.experience} experience</div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <MapPin className="h-4 w-4 text-gray-400 mr-1" />
                      <div className="text-sm text-gray-900">{farmer.location}</div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-3 py-1 rounded-full text-xs font-medium ${getSuitabilityColor(farmer.suitability)}`}>
                      {farmer.suitability}%
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <TrendingUp className="h-4 w-4 text-gray-400 mr-1" />
                      <div className="text-sm text-gray-900">{farmer.estimatedYield} tons/ha</div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">
                      <div>{farmer.plotSize} ha • {farmer.soilType} soil</div>
                      <div className="text-gray-500">
                        {farmer.irrigationAvailable ? '💧 Irrigated' : '🌧️ Rain-fed'}
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    {sentOffers.has(farmer.id) ? (
                      <span className="inline-flex items-center text-green-600">
                        <CheckCircle className="h-4 w-4 mr-1" />
                        Offer Sent
                      </span>
                    ) : (
                      <button
                        onClick={() => handleSendOffer(farmer.id, farmer.name)}
                        className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-md text-sm transition-colors"
                      >
                        Send Offer
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {matchedFarmers.length === 0 && (
        <div className="text-center py-12">
          <div className="text-gray-400 mb-4">
            <User className="h-12 w-12 mx-auto" />
          </div>
          <p className="text-gray-600">No farmers found matching your requirements.</p>
          <p className="text-sm text-gray-500 mt-2">Try adjusting your criteria or check back later.</p>
        </div>
      )}

      {/* Summary */}
      <div className="mt-6 bg-gray-50 rounded-lg p-4">
        <div className="flex justify-between items-center text-sm">
          <span className="text-gray-600">
            Found {matchedFarmers.length} matching farmers
          </span>
          <span className="text-gray-600">
            {sentOffers.size} offers sent
          </span>
        </div>
      </div>
    </div>
  );
}