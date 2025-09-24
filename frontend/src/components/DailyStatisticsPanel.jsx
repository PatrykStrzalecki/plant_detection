import React, { useState, useEffect } from 'react';

const DailyStatisticsPanel = ({ processedResult }) => {
  // Initial statistics with example categories. You can adjust these to match
  // the categories from your backend.
  const initialStats = {
    '1': 0,
    '2': 0,
    '3': 0,
    '4': 0,
  };

  const [statistics, setStatistics] = useState(initialStats);

  // Use useEffect to update statistics when processedResult changes
  useEffect(() => {
    if (processedResult && processedResult.category) {
      const { category } = processedResult;
      const key = category.toString();
      setStatistics(prevStats => {
        const newStats = { ...prevStats };
        if (newStats.hasOwnProperty(key)) {
          newStats[key] += 1;
        }
        return newStats;
      });
    }
  }, [processedResult]);

  // Function to reset all statistics to zero
  const handleReset = () => {
    setStatistics(initialStats);
  };

  return (
    <div className="bg-stone-950/40 p-5 rounded-lg shadow-md flex flex-col items-center justify-between h-full">
      {/* Gray header with title */}
      <div className="bg-gray-300/10 w-full p-4 rounded-md mb-4 flex items-center justify-center h-24 border-2 border-black">
        <h2 className="text-xl font-bold">DAILY STATISTICS</h2>
      </div>
      <div className="flex flex-col gap-4 w-full flex-grow">
        {Object.keys(statistics).map((category, index) => (
          <div key={index} className="flex justify-between items-center gap-4">
            <div className="bg-gray-300/10 p-4 rounded-md flex-none w-1/4 flex justify-center items-center border-2 border-black">
              <span className="text-xl font-bold">{index + 1}</span>
            </div>
            <div className="bg-gray-300/10 p-4 rounded-md flex-grow flex justify-center items-center border-2 border-black">
              <p className="text-xl font-bold">{statistics[category]}</p>
            </div>
          </div>
        ))}
      </div>
      <button
        onClick={handleReset}
        className="mt-4 w-full bg-red-900 hover:bg-red-700 text-white font-bold py-2 px-4 rounded-md transition-colors duration-300 border-2 border-black"
      >
        Reset All
      </button>
    </div>
  );
};

export default DailyStatisticsPanel;