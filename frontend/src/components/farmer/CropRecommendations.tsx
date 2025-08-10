import React from 'react';
import { ArrowLeft, Sprout } from 'lucide-react';

interface CropRecommendationsProps {
  landDetails: any[];
  recommendations: { [kebeleId: string]: any[] };
  onSelectCrop: (crop: any) => void;
  onBack: () => void;
}

export default function CropRecommendations({ landDetails, recommendations, onSelectCrop, onBack }: CropRecommendationsProps) {
  // Find the kebele_id from landDetails
  const landWithKebele = landDetails.find(ld => ld.kebele_id && recommendations[ld.kebele_id]);
  const kebeleId = landWithKebele?.kebele_id;
  let crops = kebeleId ? recommendations[kebeleId] : [];

  // Sort crops by ndvi_peak descending
  crops = [...crops].sort((a, b) => (b.ndvi_peak ?? 0) - (a.ndvi_peak ?? 0));

  return (
    <div className="max-w-3xl mx-auto px-4 py-8">
      <button onClick={onBack} className="mb-4 text-blue-600 hover:underline">&larr; Back</button>
      <h2 className="text-2xl font-bold mb-6">Crop Recommendations</h2>
      {crops.length === 0 ? (
        <p>No recommendations available for your land.</p>
      ) : (
        <div className="space-y-4">
          {crops.map((rec, idx) => (
            <div key={rec.crop + idx} className="bg-white rounded-lg shadow p-4 flex justify-between items-center">
              <div className="flex items-center gap-3">
                <Sprout className="h-8 w-8 text-green-600" />
                <div>
                  <h3 className="text-lg font-semibold">{rec.crop}</h3>
                  <p className="text-sm text-gray-600">Distance: {rec.distance.toFixed(2)}</p>
                  <p className="text-sm text-gray-600">Rainfall: {rec.seasonal_rainfall_total?.toFixed(2)}</p>
                  <p className="text-sm text-gray-600">Mean Temp: {rec.mean_temp_season?.toFixed(2)}</p>
                  <p className="text-sm text-gray-600">Data Quality: {rec.data_quality_flag}</p>
                  <p className="text-sm text-gray-600">NDVI Peak: {rec.ndvi_peak?.toFixed(2)}</p>
                </div>
              </div>
              <button
                onClick={() => onSelectCrop(rec)}
                className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
              >
                View Buyers
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}