import React from 'react';

const DailyStatisticsPanel = ({ statistics, onResetStatistics }) => {
  
  return (
    <div className="bg-stone-950/40 p-5 rounded-lg shadow-md flex flex-col items-center justify-between h-full">
      {/* Gray header with title */}
      <div className="bg-gray-300/10 w-full p-4 rounded-md mb-4 flex items-center justify-center h-24 border-2 border-black">
        <h2 className="text-xl font-bold">DAILY STATISTICS</h2>
      </div>
      <div className="flex flex-col gap-4 w-full flex-grow">
        {Object.keys(statistics).map((category) => (
          <div key={category} className="flex justify-between items-center gap-4">
            <div className="bg-gray-300/10 p-4 rounded-md flex-none w-1/4 flex justify-center items-center border-2 border-black">
              <span className="text-xl font-bold">{category}</span>
            </div>
            <div className="bg-gray-300/10 p-4 rounded-md flex-grow flex justify-center items-center border-2 border-black">
              <p className="text-xl font-bold">{statistics[category]}</p>
            </div>
          </div>
        ))}
      </div>
      <button
        onClick={onResetStatistics}
        className="mt-4 w-full bg-red-900 hover:bg-red-700 text-white font-bold py-2 px-4 rounded-md transition-colors duration-300 border-2 border-black"
      >
        Reset All
      </button>
    </div>
  );
};

export default DailyStatisticsPanel;