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

const App = () => {
  const [currentView, setCurrentView] = useState(VIEWS.DASHBOARD);
  const [processedResult, setProcessedResult] = useState(null);

  const handleViewChange = (view) => {
    setCurrentView(view);
  };

  const handleProcessComplete = (result) => {
    setProcessedResult(result);
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
        return <Dashboard processedResult={processedResult} />;
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
