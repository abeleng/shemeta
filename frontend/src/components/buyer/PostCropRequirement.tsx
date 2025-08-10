import React, { useState } from 'react';
import { ArrowLeft, Package, DollarSign, Calendar, MapPin } from 'lucide-react';

interface PostCropRequirementProps {
  onBack: () => void;
}

export default function PostCropRequirement({ onBack }: PostCropRequirementProps) {
  const [formData, setFormData] = useState({
    cropName: '',
    quantity: '',
    pricePerKg: '',
    harvestDate: '',
    region: '',
    qualityRequirements: '',
    additionalNotes: ''
  });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setMessage(null);

    const token = localStorage.getItem('token');
    try {
      const res = await fetch('http://127.0.0.1:8000/api/user/post_crop_requirement/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(formData),
      });
      const data = await res.json();
      if (res.ok && data.success) {
        setMessage('Crop requirement posted successfully!');
        setFormData({
          cropName: '',
          quantity: '',
          pricePerKg: '',
          harvestDate: '',
          region: '',
          qualityRequirements: '',
          additionalNotes: ''
        });
      } else {
        setMessage(data.message || 'Failed to post crop requirement.');
      }
    } catch (err) {
      setMessage('Network error. Please try again.');
    }
    setLoading(false);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
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
          <h2 className="text-2xl font-bold text-gray-900">Post Crop Requirement</h2>
          <p className="text-gray-600">Connect with farmers who can supply your needed crops</p>
        </div>
      </div>

      {/* Form */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Crop Name */}
          <div>
            <label htmlFor="cropName" className="block text-sm font-medium text-gray-700 mb-2">
              <Package className="h-4 w-4 inline mr-1" />
              Crop Name
            </label>
            <select
              id="cropName"
              name="cropName"
              value={formData.cropName}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500"
              required
            >
              <option value="">Select Crop</option>
              <option value="sorghum">Sorghum</option>
              <option value="rice">Rice</option>
              <option value="bean">Bean</option>
              <option value="lentil">Lentil</option>
              <option value="safflower">Safflower</option>
              <option value="sesame">Sesame</option>
              <option value="soybean">Soybean</option>
              <option value="carrot">Carrot</option>
              <option value="garlic">Garlic</option>
              <option value="onion">Onion</option>
              <option value="tomato">Tomato</option>
              <option value="mandarin">Mandarin</option>
              <option value="mango">Mango</option>
              <option value="coffee">Coffee</option>
              <option value="avocado">Avocado</option>
              <option value="banana">Banana</option>
            </select>
          </div>

          {/* Quantity and Price */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label htmlFor="quantity" className="block text-sm font-medium text-gray-700 mb-2">
                Quantity Required (Tons)
              </label>
              <input
                type="number"
                id="quantity"
                name="quantity"
                value={formData.quantity}
                onChange={handleInputChange}
                min="0.1"
                step="0.1"
                placeholder="e.g., 25"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500"
                required
              />
            </div>

            <div>
              <label htmlFor="pricePerKg" className="block text-sm font-medium text-gray-700 mb-2">
                <DollarSign className="h-4 w-4 inline mr-1" />
                Price per Kg (ETB)
              </label>
              <input
                type="number"
                id="pricePerKg"
                name="pricePerKg"
                value={formData.pricePerKg}
                onChange={handleInputChange}
                min="1"
                placeholder="e.g., 45"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500"
                required
              />
            </div>
          </div>

          {/* Harvest Date and Region */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label htmlFor="harvestDate" className="block text-sm font-medium text-gray-700 mb-2">
                <Calendar className="h-4 w-4 inline mr-1" />
                Required Harvest Date
              </label>
              <input
                type="date"
                id="harvestDate"
                name="harvestDate"
                value={formData.harvestDate}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500"
                required
              />
            </div>

            <div>
              <label htmlFor="region" className="block text-sm font-medium text-gray-700 mb-2">
                <MapPin className="h-4 w-4 inline mr-1" />
                Preferred Region
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
                <option value="any">Any Region</option>
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
          </div>

          {/* Quality Requirements */}
          <div>
            <label htmlFor="qualityRequirements" className="block text-sm font-medium text-gray-700 mb-2">
              Quality Requirements
            </label>
            <textarea
              id="qualityRequirements"
              name="qualityRequirements"
              value={formData.qualityRequirements}
              onChange={handleInputChange}
              rows={3}
              placeholder="e.g., Grade A, moisture content below 12%, minimal defects..."
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500"
            />
          </div>

          {/* Additional Notes */}
          <div>
            <label htmlFor="additionalNotes" className="block text-sm font-medium text-gray-700 mb-2">
              Additional Notes (Optional)
            </label>
            <textarea
              id="additionalNotes"
              name="additionalNotes"
              value={formData.additionalNotes}
              onChange={handleInputChange}
              rows={2}
              placeholder="Any other requirements or preferences..."
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500"
            />
          </div>

          {/* Submit Button */}
          <div className="flex justify-end pt-4">
            <button
              type="submit"
              className="bg-green-600 hover:bg-green-700 text-white font-medium py-2 px-6 rounded-lg transition-colors"
              disabled={loading}
            >
              {loading ? 'Submitting...' : 'Find Matching Farmers'}
            </button>
          </div>
        </form>
        {message && (
          <div className="mt-4 text-center text-sm text-green-700">{message}</div>
        )}
      </div>
    </div>
  );
}