import React, { useState, useEffect } from 'react';
import FarmerDashboard from './farmer/FarmerDashboard';
import AddLandDetails from './farmer/AddLandDetails';
import CropRecommendations from './farmer/CropRecommendations';
import MatchedBuyers from './farmer/MatchedBuyers';
import FarmerResponses from './farmer/FarmerResponses';

type FarmerPage = 'dashboard' | 'add-land' | 'recommendations' | 'matched-buyers' | 'farmer-responses';

export default function FarmerView() {
  const [currentPage, setCurrentPage] = useState<FarmerPage>('dashboard');
  const [landDetails, setLandDetails] = useState<any[]>([]);
  const [selectedCrop, setSelectedCrop] = useState(null);
  const [recommendations, setRecommendations] = useState<{ [kebeleId: string]: any[] }>({});
  const [matches, setMatches] = useState<any[]>([]);

  useEffect(() => {
    const fetchFarmerHome = async () => {
      const token = localStorage.getItem('token');
      const res = await fetch('http://127.0.0.1:8000/api/user/farmer_home/', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
      });
      if (res.ok) {
        const data = await res.json();
        if (data.land_details) setLandDetails(data.land_details);
        if (data.recommendations) setRecommendations(data.recommendations);
        if (data.matches) setMatches(data.matches);
      }
    };
    fetchFarmerHome();
  }, []);

  const renderPage = () => {
    switch (currentPage) {
      case 'dashboard':
        return <FarmerDashboard 
          onNavigate={setCurrentPage} 
          landDetails={landDetails}
          recommendations={recommendations}
          matches={matches}
        />;
      case 'add-land':
        return <AddLandDetails onSubmit={(details) => {
          setLandDetails([...landDetails, details]);
          setCurrentPage('recommendations');
        }} onBack={() => setCurrentPage('dashboard')} />;
      case 'recommendations':
        return <CropRecommendations 
          landDetails={landDetails}
          recommendations={recommendations}
          onSelectCrop={(crop) => {
            setSelectedCrop(crop);
            setCurrentPage('matched-buyers');
          }}
          onBack={() => setCurrentPage('dashboard')} 
        />;
      case 'matched-buyers':
        return <MatchedBuyers 
          selectedCrop={selectedCrop}
          onBack={() => setCurrentPage('recommendations')} 
        />;
      case 'farmer-responses':
        return <FarmerResponses 
          onBack={() => setCurrentPage('dashboard')} 
        />;
      default:
        return <FarmerDashboard onNavigate={setCurrentPage} />;
    }
  };

  return <div>{renderPage()}</div>;
}