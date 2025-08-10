import React from 'react';
import { ArrowLeft, User, MapPin, Calendar, DollarSign } from 'lucide-react';

interface MatchedBuyersProps {
  selectedCrop: any;
  onBack: () => void;
}

export default function MatchedBuyers({ selectedCrop, onBack }: MatchedBuyersProps) {
  // TODO: Replace with API call
  const matchedBuyers = [
    {
      id: 1,
      name: "Ethiopian Grain Trading",
      type: "Export Company",
      quantityNeeded: 25,
      pricePerKg: 48,
      harvestDate: "2024-12-15",
      location: "Addis Ababa",
      rating: 4.8,
      verified: true
    },
    {
      id: 2,
      name: "Oromia Agricultural Cooperative",
      type: "Local Cooperative",
      quantityNeeded: 15,
      pricePerKg: 42,
      harvestDate: "2024-12-20",
      location: "Adama",
      rating: 4.5,
      verified: true
    },
    {
      id: 3,
      name: "Habesha Foods Processing",
      type: "Food Processor",
      quantityNeeded: 30,
      pricePerKg: 46,
      harvestDate: "2024-12-10",
      location: "Bahir Dar",
      rating: 4.6,
      verified: true
    }
  ];

  const handleAcceptOffer = (buyer: any) => {
    alert(`Offer accepted! ${buyer.name} will be notified of your interest. They will contact you within 24 hours to discuss delivery details.`);
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="flex items-center mb-8">
        <button
          onClick={onBack}
          className="mr-4 p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
        >
          <ArrowLeft className="h-5 w-5" />
        </button>
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Matched Buyers</h2>
          <p className="text-gray-600">Buyers interested in your {selectedCrop?.name}</p>
        </div>
      </div>

      {/* Selected Crop Summary */}
      {selectedCrop && (
        <div className="bg-green-50 rounded-lg p-4 mb-6">
          <h3 className="font-medium text-gray-900 mb-2">Selected Crop: {selectedCrop.name}</h3>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
            <div>
              <span className="text-gray-600">Expected Yield:</span>
              <span className="ml-1 font-medium">{selectedCrop.expectedYield} tons/ha</span>
            </div>
            <div>
              <span className="text-gray-600">Your Price:</span>
              <span className="ml-1 font-medium">{selectedCrop.sellingPrice} ETB/kg</span>
            </div>
            <div>
              <span className="text-gray-600">Suitability:</span>
              <span className="ml-1 font-medium text-green-600">{selectedCrop.suitability}%</span>
            </div>
          </div>
        </div>
      )}

      {/* Buyers List */}
      <div className="space-y-6">
        {matchedBuyers.map((buyer) => (
          <div key={buyer.id} className="bg-white rounded-lg shadow-sm border p-6">
            <div className="flex flex-col lg:flex-row lg:items-center justify-between">
              <div className="flex-1">
                {/* Buyer Header */}
                <div className="flex items-center mb-4">
                  <div className="p-2 bg-blue-100 rounded-lg mr-3">
                    <User className="h-5 w-5 text-blue-600" />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">{buyer.name}</h3>
                    <p className="text-sm text-gray-600">{buyer.type}</p>
                  </div>
                  {buyer.verified && (
                    <span className="ml-3 bg-green-100 text-green-800 text-xs font-medium px-2 py-1 rounded-full">
                      Verified
                    </span>
                  )}
                </div>

                {/* Buyer Details Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
                  <div className="flex items-center">
                    <div className="h-5 w-5 bg-gray-100 rounded mr-2 flex items-center justify-center">
                      <span className="text-gray-600 text-xs">📦</span>
                    </div>
                    <div>
                      <p className="text-xs text-gray-600">Quantity Needed</p>
                      <p className="font-semibold">{buyer.quantityNeeded} tons</p>
                    </div>
                  </div>

                  <div className="flex items-center">
                    <DollarSign className="h-5 w-5 text-gray-400 mr-2" />
                    <div>
                      <p className="text-xs text-gray-600">Price Offered</p>
                      <p className="font-semibold text-green-600">{buyer.pricePerKg} ETB/kg</p>
                    </div>
                  </div>

                  <div className="flex items-center">
                    <Calendar className="h-5 w-5 text-gray-400 mr-2" />
                    <div>
                      <p className="text-xs text-gray-600">Harvest Date</p>
                      <p className="font-semibold">{new Date(buyer.harvestDate).toLocaleDateString()}</p>
                    </div>
                  </div>

                  <div className="flex items-center">
                    <MapPin className="h-5 w-5 text-gray-400 mr-2" />
                    <div>
                      <p className="text-xs text-gray-600">Location</p>
                      <p className="font-semibold">{buyer.location}</p>
                    </div>
                  </div>
                </div>

                {/* Price Comparison */}
                <div className="bg-gray-50 rounded p-3 mb-4">
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-600">Price difference:</span>
                    <span className={`text-sm font-medium ${
                      buyer.pricePerKg > (selectedCrop?.sellingPrice || 0) 
                        ? 'text-green-600' 
                        : buyer.pricePerKg === (selectedCrop?.sellingPrice || 0)
                        ? 'text-gray-600'
                        : 'text-orange-600'
                    }`}>
                      {buyer.pricePerKg > (selectedCrop?.sellingPrice || 0) && '+'}
                      {buyer.pricePerKg - (selectedCrop?.sellingPrice || 0)} ETB/kg
                    </span>
                  </div>
                </div>
              </div>

              <div className="lg:ml-6 mt-4 lg:mt-0">
                <button
                  onClick={() => handleAcceptOffer(buyer)}
                  className="w-full lg:w-auto bg-green-600 hover:bg-green-700 text-white font-medium py-2 px-6 rounded-lg transition-colors"
                >
                  Accept Offer
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {matchedBuyers.length === 0 && (
        <div className="text-center py-12">
          <div className="text-gray-400 mb-4">
            <User className="h-12 w-12 mx-auto" />
          </div>
          <p className="text-gray-600">No buyers found for your selected crop yet.</p>
          <p className="text-sm text-gray-500 mt-2">Check back later or try different crops.</p>
        </div>
      )}
    </div>
  );
}