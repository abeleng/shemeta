import React, { useState } from 'react';
import { ArrowLeft, MapPin, Droplets, Mountain, Locate } from 'lucide-react';

interface AddLandDetailsProps {
  userId: number; // <-- Add this prop to get the user id
  onSubmit: (details: any) => void;
  onBack: () => void;
}

export default function AddLandDetails({ userId, onSubmit, onBack }: AddLandDetailsProps) {
  const [formData, setFormData] = useState({
    region: '',
    location: '',
    plotSize: '',
    soilType: '',
    irrigationAvailable: false
  });
  const [isLocating, setIsLocating] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const token = localStorage.getItem('token'); // or however you store the JWT

    const payload = {
      region: formData.region,
      location: formData.location,
      plotSize: formData.plotSize,
      soilType: formData.soilType,
      irrigationAvailable: formData.irrigationAvailable
    };

    const res = await fetch('http://127.0.0.1:8000/api/user/add-land-detail/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(payload)
    });

    const data = await res.json();
    if (data.success) {
      onSubmit(formData);
    } else {
      alert(data.message || data.error);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? (e.target as HTMLInputElement).checked : value
    }));
  };

  const handleGetLocation = () => {
    setIsLocating(true);
    
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const { latitude, longitude } = position.coords;
          // Mock reverse geocoding - in real app, use Google Maps API
          const mockLocation = `Addis Ababa, Ethiopia (${latitude.toFixed(4)}, ${longitude.toFixed(4)})`;
          setFormData(prev => ({
            ...prev,
            location: mockLocation
          }));
          setIsLocating(false);
        },
        (error) => {
          console.error('Error getting location:', error);
          alert('Unable to get your location. Please enter it manually.');
          setIsLocating(false);
        }
      );
    } else {
      alert('Geolocation is not supported by this browser.');
      setIsLocating(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="flex items-center mb-8">
        <button
          onClick={onBack}
          className="mr-4 p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
        >
          <ArrowLeft className="h-5 w-5" />
        </button>
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Add Land Details</h2>
          <p className="text-gray-600">Tell us about your farm to get personalized recommendations</p>
        </div>
      </div>

      {/* Form */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Region */}
          <div>
            <label htmlFor="region" className="block text-sm font-medium text-gray-700 mb-2">
              <MapPin className="h-4 w-4 inline mr-1" />
              Region
            </label>
            <select
              id="region"
              name="region"
              value={formData.region}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500"
              required
            >
              <option value="">Select Region</option>
              <option value="addis-ababa">Addis Ababa</option>
              <option value="oromia">Oromia</option>
              <option value="amhara">Amhara</option>
              <option value="tigray">Tigray</option>
              <option value="snnp">Southern Nations, Nationalities, and Peoples</option>
              <option value="afar">Afar</option>
              <option value="somali">Somali</option>
              <option value="benishangul">Benishangul-Gumuz</option>
              <option value="gambela">Gambela</option>
              <option value="harari">Harari</option>
              <option value="dire-dawa">Dire Dawa</option>
            </select>
          </div>

          {/* Location */}
          <div>
            <label htmlFor="location" className="block text-sm font-medium text-gray-700 mb-2">
              Specific Location
            </label>
            <div className="flex space-x-2">
              <input
                type="text"
                id="location"
                name="location"
                value={formData.location}
                onChange={handleInputChange}
                placeholder="e.g., Debre Zeit, East Shewa Zone"
                className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500"
                required
              />
              <button
                type="button"
                onClick={handleGetLocation}
                disabled={isLocating}
                className="px-4 py-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white rounded-md transition-colors flex items-center"
              >
                <Locate className="h-4 w-4 mr-1" />
                {isLocating ? 'Getting...' : 'Get Location'}
              </button>
            </div>
            <p className="text-xs text-gray-500 mt-1">
              Click "Get Location" to automatically detect your current location
            </p>
          </div>

          {/* Plot Size */}
          <div>
            <label htmlFor="plotSize" className="block text-sm font-medium text-gray-700 mb-2">
              Plot Size (Hectares)
            </label>
            <input
              type="number"
              id="plotSize"
              name="plotSize"
              value={formData.plotSize}
              onChange={handleInputChange}
              min="0.1"
              step="0.1"
              placeholder="e.g., 2.5"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500"
              required
            />
          </div>

          {/* Soil Type */}
          <div>
            <label htmlFor="soilType" className="block text-sm font-medium text-gray-700 mb-2">
              <Mountain className="h-4 w-4 inline mr-1" />
              Soil Type
            </label>
            <select
              id="soilType"
              name="soilType"
              value={formData.soilType}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500"
              required
            >
              <option value="">Select Soil Type</option>
              <option value="vertisol">Vertisol (Black Cotton Soil)</option>
              <option value="cambisol">Cambisol (Brown Soil)</option>
              <option value="luvisol">Luvisol (Red Soil)</option>
              <option value="nitisol">Nitisol (Red Clay)</option>
              <option value="andosol">Andosol (Volcanic Soil)</option>
              <option value="fluvisol">Fluvisol (Alluvial Soil)</option>
            </select>
          </div>

          {/* Irrigation */}
          <div>
            <label className="flex items-center">
              <input
                type="checkbox"
                name="irrigationAvailable"
                checked={formData.irrigationAvailable}
                onChange={handleInputChange}
                className="h-4 w-4 text-green-600 focus:ring-green-500 border-gray-300 rounded"
              />
              <span className="ml-2 text-sm font-medium text-gray-700">
                <Droplets className="h-4 w-4 inline mr-1" />
                Irrigation Available
              </span>
            </label>
          </div>

          {/* Submit Button */}
          <div className="flex justify-end pt-4">
            <button
              type="submit"
              className="bg-green-600 hover:bg-green-700 text-white font-medium py-2 px-6 rounded-lg transition-colors"
            >
              Get Crop Recommendations
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}