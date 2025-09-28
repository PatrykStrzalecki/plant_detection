// import React, { useState, useEffect } from 'react';

// // Initial statistics with example categories. You can adjust these to match
// // the categories from your backend.


// const DailyStatisticsPanel = ({ processedResult }) => {
//   const [statistics, setStatistics] = useState(initialStats);
//   const [lastProcessedId, setLastProcessedId] = useState(null);

//   console.log('=== DailyStatisticsPanel RENDER ===');
//   console.log('processedResult:', processedResult);
//   console.log('current statistics:', statistics);
//   console.log('lastProcessedId:', lastProcessedId);

//   // Use useEffect to update statistics when processedResult changes
//   useEffect(() => {
//     console.log('=== useEffect TRIGGERED ===');
//     console.log('processedResult in effect:', processedResult);
//     console.log('statistics in effect:', statistics);
//     console.log('lastProcessedId in effect:', lastProcessedId);
//     if (processedResult && processedResult.id) {
//       const currentDetectionId = processedResult.id;
//       console.log('currentDetectionId:', currentDetectionId);
//       console.log('lastProcessedId comparison:', lastProcessedId);
//       if (currentDetectionId === lastProcessedId) {
//         console.log('SKIPPING - ID already processed');
//         return; // Skip if this result has already been processed
//       }
//       const { category } = processedResult;
//       console.log('category from processedResult:', category);
//       console.log('typeof category:', typeof category);
//       if (!category) {
//         console.log('NO CATEGORY FOUND!');
//         return;
//       }
//       const key = category.toString();
//       console.log('key for statistics:', key);
//       console.log('statistics object keys:', Object.keys(statistics));
//       console.log('hasOwnProperty check:', statistics.hasOwnProperty(key));
//       setStatistics(prevStats => {
//         console.log('=== INSIDE setStatistics ===');
//         console.log('prevStats:', prevStats);
//         const newStats = { ...prevStats };
//         console.log('newStats before update:', newStats);
//         if (newStats.hasOwnProperty(key)) {
//           console.log('INCREMENTING category:', key, 'from', newStats[key], 'to', newStats[key] + 1);
//           newStats[key] += 1;
//         } else {
//           console.log('KEY NOT FOUND in statistics:', key);
//         }
//         console.log('newStats after update:', newStats);
//         return newStats;
//       });
//       console.log('Setting lastProcessedId to:', currentDetectionId);
//       setLastProcessedId(currentDetectionId);
//     } else {
//       console.log('NO processedResult or ID found');
//     }
//   }, [processedResult, lastProcessedId]);

//   // Function to reset all statistics to zero
//   const handleReset = () => {
//     setStatistics({ ...initialStats });
//     setLastProcessedId(null);
//   };

//   return (
//     <div className="bg-stone-950/40 p-5 rounded-lg shadow-md flex flex-col items-center justify-between h-full">
//       {/* Gray header with title */}
//       <div className="bg-gray-300/10 w-full p-4 rounded-md mb-4 flex items-center justify-center h-24 border-2 border-black">
//         <h2 className="text-xl font-bold">DAILY STATISTICS</h2>
//       </div>
//       <div className="flex flex-col gap-4 w-full flex-grow">
//         {Object.keys(statistics).map((category) => (
//           <div key={category} className="flex justify-between items-center gap-4">
//             <div className="bg-gray-300/10 p-4 rounded-md flex-none w-1/4 flex justify-center items-center border-2 border-black">
//               <span className="text-xl font-bold">{category}</span>
//             </div>
//             <div className="bg-gray-300/10 p-4 rounded-md flex-grow flex justify-center items-center border-2 border-black">
//               <p className="text-xl font-bold">{statistics[category]}</p>
//             </div>
//           </div>
//         ))}
//       </div>
//       <button
//         onClick={handleReset}
//         className="mt-4 w-full bg-red-900 hover:bg-red-700 text-white font-bold py-2 px-4 rounded-md transition-colors duration-300 border-2 border-black"
//       >
//         Reset All
//       </button>
//     </div>
//   );
// };

// export default DailyStatisticsPanel;



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