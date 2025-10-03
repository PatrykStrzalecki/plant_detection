import React, { useEffect, useState } from 'react';
import Header from './components/Header';
import Dashboard from './components/Dashboard';
import UploadScreen from './components/UploadScreen';
import Settings from './components/Settings';
import Analytics from './components/Analytics';

// API endpoints
const STATUS_URL = "http://localhost:8000/task-status/";
const WS_URL = "ws://localhost:8000/ws/frontend";

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
  const [frontendWebsocket, setFrontendWebsocket] = useState(null);

  useEffect(() => {
    const ws = new WebSocket(WS_URL);
    setFrontendWebsocket(ws);

    ws.onopen = () => {
      console.log('WebSocket connection established');
      setFrontendWebsocket(ws);
    }

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      const taskStatus = data.status;
      console.log('Message from server:', data);
      if (taskStatus === "SUCCESS") {
        const taskId = data.task_id;
        fetch(STATUS_URL + taskId)
          .then(response => response.json())
          .then(resultData => {
            handleProcessComplete(resultData);
            setCurrentView(VIEWS.DASHBOARD);
          })
          .catch(error => {
            console.error('Error fetching task result:', error);
          });
      } else if (taskStatus === "FAILURE") {
        console.error('Task failed on server side');
      }
    };

    ws.onclose = () => {
      console.log('WebSocket connection closed');
      setFrontendWebsocket(null);
    }

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    }

    return () => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.close();
      }
    };
  }, []);

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
