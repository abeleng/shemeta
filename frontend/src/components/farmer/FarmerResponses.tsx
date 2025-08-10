import React, { useState } from 'react';
import { ArrowLeft, User, Calendar, DollarSign, Package, CheckCircle, XCircle } from 'lucide-react';

interface FarmerResponsesProps {
  onBack: () => void;
}

export default function FarmerResponses({ onBack }: FarmerResponsesProps) {
  const [responses, setResponses] = useState<Record<number, 'accepted' | 'declined'>>({});

  // TODO: Replace with API call
  const buyerOffers = [
    {
      id: 1,
      buyerName: "Ethiopian Grain Trading",
      buyerType: "Export Company",
      crop: "Teff",
      quantity: 5,
      pricePerKg: 48,
      totalValue: 240000,
      harvestDate: "2024-12-15",
      deliveryLocation: "Addis Ababa",
      paymentTerms: "50% advance, 50% on delivery",
      qualityRequirements: "Grade A, moisture content below 12%",
      contactPerson: "Ato Dawit Tesfaye",
      phone: "+251-911-123456",
      offerDate: "2024-01-15",
      expiryDate: "2024-01-25"
    },
    {
      id: 2,
      buyerName: "Oromia Agricultural Cooperative",
      buyerType: "Local Cooperative",
      crop: "Maize (Hybrid)",
      quantity: 10,
      pricePerKg: 18,
      totalValue: 180000,
      harvestDate: "2024-12-20",
      deliveryLocation: "Adama",
      paymentTerms: "Payment on delivery",
      qualityRequirements: "Good quality, properly dried",
      contactPerson: "W/ro Almaz Bekele",
      phone: "+251-922-654321",
      offerDate: "2024-01-16",
      expiryDate: "2024-01-26"
    },
    {
      id: 3,
      buyerName: "Habesha Foods Processing",
      buyerType: "Food Processor",
      crop: "Haricot Beans",
      quantity: 3,
      pricePerKg: 35,
      totalValue: 105000,
      harvestDate: "2024-12-10",
      deliveryLocation: "Bahir Dar",
      paymentTerms: "30% advance, 70% on delivery",
      qualityRequirements: "Premium grade, uniform size",
      contactPerson: "Ato Mulugeta Assefa",
      phone: "+251-933-789012",
      offerDate: "2024-01-17",
      expiryDate: "2024-01-27"
    }
  ];

  const handleResponse = (offerId: number, response: 'accepted' | 'declined', offer: any) => {
    setResponses(prev => ({ ...prev, [offerId]: response }));
    
    const action = response === 'accepted' ? 'accepted' : 'declined';
    alert(`You have ${action} the offer from ${offer.buyerName}. They will be notified of your decision.`);
  };

  const getStatusColor = (response: string) => {
    switch (response) {
      case 'accepted':
        return 'bg-green-100 text-green-800';
      case 'declined':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-orange-100 text-orange-800';
    }
  };

  const getStatusText = (response: string) => {
    switch (response) {
      case 'accepted':
        return 'Accepted';
      case 'declined':
        return 'Declined';
      default:
        return 'Pending';
    }
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
          <h2 className="text-2xl font-bold text-gray-900">Buyer Offers</h2>
          <p className="text-gray-600">Review and respond to offers from buyers</p>
        </div>
      </div>

      {/* Offers List */}
      <div className="space-y-6">
        {buyerOffers.map((offer) => (
          <div key={offer.id} className="bg-white rounded-lg shadow-sm border overflow-hidden">
            {/* Offer Header */}
            <div className="bg-gray-50 px-6 py-4 border-b">
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <div className="p-2 bg-blue-100 rounded-lg mr-3">
                    <User className="h-5 w-5 text-blue-600" />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">{offer.buyerName}</h3>
                    <p className="text-sm text-gray-600">{offer.buyerType}</p>
                  </div>
                </div>
                <div className="text-right">
                  <span className={`inline-flex px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(responses[offer.id])}`}>
                    {getStatusText(responses[offer.id])}
                  </span>
                  <p className="text-xs text-gray-500 mt-1">
                    Expires: {new Date(offer.expiryDate).toLocaleDateString()}
                  </p>
                </div>
              </div>
            </div>

            {/* Offer Details */}
            <div className="p-6">
              {/* Main Offer Info */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                <div className="flex items-center">
                  <Package className="h-5 w-5 text-gray-400 mr-2" />
                  <div>
                    <p className="text-sm text-gray-600">Crop & Quantity</p>
                    <p className="font-semibold">{offer.crop}</p>
                    <p className="text-sm text-gray-500">{offer.quantity} tons</p>
                  </div>
                </div>

                <div className="flex items-center">
                  <DollarSign className="h-5 w-5 text-gray-400 mr-2" />
                  <div>
                    <p className="text-sm text-gray-600">Price per Kg</p>
                    <p className="font-semibold text-green-600">{offer.pricePerKg} ETB</p>
                    <p className="text-sm text-gray-500">Total: {offer.totalValue.toLocaleString()} ETB</p>
                  </div>
                </div>

                <div className="flex items-center">
                  <Calendar className="h-5 w-5 text-gray-400 mr-2" />
                  <div>
                    <p className="text-sm text-gray-600">Harvest Date</p>
                    <p className="font-semibold">{new Date(offer.harvestDate).toLocaleDateString()}</p>
                  </div>
                </div>

                <div className="flex items-center">
                  <div className="h-5 w-5 bg-gray-100 rounded mr-2 flex items-center justify-center">
                    <span className="text-gray-600 text-xs">📍</span>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Delivery</p>
                    <p className="font-semibold">{offer.deliveryLocation}</p>
                  </div>
                </div>
              </div>

              {/* Additional Details */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                <div>
                  <h4 className="font-medium text-gray-900 mb-2">Payment Terms</h4>
                  <p className="text-sm text-gray-600">{offer.paymentTerms}</p>
                </div>
                <div>
                  <h4 className="font-medium text-gray-900 mb-2">Quality Requirements</h4>
                  <p className="text-sm text-gray-600">{offer.qualityRequirements}</p>
                </div>
              </div>

              {/* Contact Information */}
              <div className="bg-gray-50 rounded-lg p-4 mb-6">
                <h4 className="font-medium text-gray-900 mb-2">Contact Information</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-gray-600">Contact Person:</span>
                    <span className="ml-1 font-medium">{offer.contactPerson}</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Phone:</span>
                    <span className="ml-1 font-medium">{offer.phone}</span>
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              {!responses[offer.id] && (
                <div className="flex space-x-4">
                  <button
                    onClick={() => handleResponse(offer.id, 'accepted', offer)}
                    className="flex-1 bg-green-600 hover:bg-green-700 text-white font-medium py-2 px-4 rounded-lg transition-colors flex items-center justify-center"
                  >
                    <CheckCircle className="h-4 w-4 mr-2" />
                    Accept Offer
                  </button>
                  <button
                    onClick={() => handleResponse(offer.id, 'declined', offer)}
                    className="flex-1 bg-red-600 hover:bg-red-700 text-white font-medium py-2 px-4 rounded-lg transition-colors flex items-center justify-center"
                  >
                    <XCircle className="h-4 w-4 mr-2" />
                    Decline Offer
                  </button>
                </div>
              )}

              {responses[offer.id] && (
                <div className="text-center py-4">
                  <p className="text-gray-600">
                    You have {responses[offer.id]} this offer. The buyer has been notified.
                  </p>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {buyerOffers.length === 0 && (
        <div className="text-center py-12">
          <div className="text-gray-400 mb-4">
            <Package className="h-12 w-12 mx-auto" />
          </div>
          <p className="text-gray-600">No buyer offers available.</p>
          <p className="text-sm text-gray-500 mt-2">Complete your land details and crop selection to receive offers.</p>
        </div>
      )}
    </div>
  );
}