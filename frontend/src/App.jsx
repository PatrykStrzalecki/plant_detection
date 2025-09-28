import React, { useState } from 'react';
import Header from './components/Header';
import Dashboard from './components/Dashboard';
import UploadScreen from './components/UploadScreen';
import Settings from './components/Settings';
import Analytics from './components/Analytics';

// Available views in the application
const VIEWS = {
  DASHBOARD: 'dashboard',
  UPLOAD: 'upload',
  SETTINGS: 'settings',
  ANALYTICS: 'analytics',
};

const initialStats = {
  '1': 0,
  '2': 0,
  '3': 0,
  '4': 0,
};

const App = () => {
  const [currentView, setCurrentView] = useState(VIEWS.DASHBOARD);
  const [processedResult, setProcessedResult] = useState(null);
  const [statistics, setStatistics] = useState(initialStats);
  const [processedIds, setProcessedIds] = useState(new Set());

  const handleViewChange = (view) => {
    setCurrentView(view);
  };

  const handleProcessComplete = (result) => {
    setProcessedResult(result);

    if (result && result.id && !processedIds.has(result.id)) {
      const category = result.category || 4;
      const key = category.toString();
      
      if (statistics.hasOwnProperty(key)) {
        setStatistics(prevStats => ({
          ...prevStats,
          [key]: prevStats[key] + 1
        }));
        setProcessedIds(prev => new Set(prev).add(result.id));
      }
    }
  };

  const handleResetStatistics = () => {
    setStatistics({ ...initialStats });
    setProcessedIds(new Set());
  };

  const renderView = () => {
    switch (currentView) {
      case VIEWS.UPLOAD:
        return <UploadScreen onViewChange={handleViewChange} views={VIEWS} onProcessComplete={handleProcessComplete} />;
      case VIEWS.SETTINGS:
        return <Settings />;
      case VIEWS.ANALYTICS:
        return <Analytics />;
      default:
        return <Dashboard processedResult={processedResult} statistics={statistics} onResetStatistics={handleResetStatistics} />;
    }
  };

  return (
    <div className="flex flex-col min-h-screen h-screen bg-stone-900 text-white font-sans overflow-hidden">
      <Header currentView={currentView} onViewChange={handleViewChange} views={VIEWS} />
      <main className="flex-grow p-5 overflow-hidden">
        <div className="h-full w-full flex items-center justify-center">
          {renderView()}
        </div>
      </main>
    </div>
  );
};

export default App;
