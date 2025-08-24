import React from 'react';
import { Upload, Settings, BarChart3, Eye } from 'lucide-react';
import PLCStatus from './PLCStatus';

const Header = ({ currentView, onViewChange, views }) => {
  // Function for dynamic button styling
  const getButtonClass = (viewName, isEnabled) => {
    let baseClasses = "flex items-center gap-2 rounded-md px-3 py-2 text-sm font-medium transition-colors";
    const isActive = currentView === viewName;
    
    if (isEnabled) {
      baseClasses += isActive ? ' bg-green-700 text-white' : ' bg-green-900 text-gray-300 hover:bg-green-700 hover:text-white';
    } else {
      baseClasses += ' bg-gray-600 text-gray-500 cursor-not-allowed';
    }
    
    return baseClasses;
  };

  return (
    <header className="bg-stone-950/50 after:pointer-events-none after:absolute after:inset-x-0 after:bottom-0 after:h-px after:bg-white/10">
      <nav className="relative flex h-16 items-center justify-between px-4 sm:px-6 lg:px-8">
        <div className="flex space-x-4">
          <button
            className={getButtonClass(views.DASHBOARD, true)}
            onClick={() => onViewChange(views.DASHBOARD)}
          >
            <Eye className="size-4" />
            Detection results
          </button>
          <button
            className={getButtonClass(views.UPLOAD, true)}
            onClick={() => onViewChange(views.UPLOAD)}
          >
            <Upload className="size-4" />
            Upload
          </button>
          <button
            className={getButtonClass(views.ANALYTICS, false)}
          >
            <BarChart3 className="size-4" />
            Analytics
          </button>
          <button
            className={getButtonClass(views.SETTINGS, false)}
          >
            <Settings className="size-4" />
            Settings
          </button>
        </div>
        <PLCStatus />
      </nav>
    </header>
  );
};

export default Header;
