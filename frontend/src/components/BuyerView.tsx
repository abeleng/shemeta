import React, { useState } from 'react';
import BuyerDashboard from './buyer/BuyerDashboard';
import PostCropRequirement from './buyer/PostCropRequirement';
import MatchedFarmers from './buyer/MatchedFarmers';

type BuyerPage = 'dashboard' | 'post-requirement' | 'matched-farmers';

export default function BuyerView() {
  const [currentPage, setCurrentPage] = useState<BuyerPage>('dashboard');
  const [cropRequirement, setCropRequirement] = useState(null);

  const renderPage = () => {
    switch (currentPage) {
      case 'dashboard':
        return <BuyerDashboard onNavigate={setCurrentPage} />;
      case 'post-requirement':
        return <PostCropRequirement 
          onSubmit={(requirement) => {
            setCropRequirement(requirement);
            setCurrentPage('matched-farmers');
          }}
          onBack={() => setCurrentPage('dashboard')} 
        />;
      case 'matched-farmers':
        return <MatchedFarmers 
          cropRequirement={cropRequirement}
          onBack={() => setCurrentPage('dashboard')} 
        />;
      default:
        return <BuyerDashboard onNavigate={setCurrentPage} />;
    }
  };

  return <div>{renderPage()}</div>;
}