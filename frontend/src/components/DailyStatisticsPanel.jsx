import React from 'react';

const DailyStatisticsPanel = () => {
  return (
    <div className="bg-stone-950/40 p-5 rounded-lg shadow-md flex flex-col items-center">
      {/* Gray header with title */}
      <div className="bg-gray-300/10 w-full p-4 rounded-md mb-4 flex items-center justify-center h-24 border-2 border-black">
        <h2 className="text-xl font-bold">DAILY STATISTICS</h2>
      </div>
      <div className="flex flex-col gap-4 w-full">
        {/* Row 1 */}
        <div className="flex justify-between items-center gap-4">
          <div className="bg-gray-300/10 p-4 rounded-md flex-none w-1/4 flex justify-center items-center border-2 border-black">
            <span className="text-xl font-bold">1</span>
          </div>
          <div className="bg-gray-300/10 p-4 rounded-md flex-grow flex justify-center items-center border-2 border-black">
            <p className="text-xl font-bold">2957</p>
          </div>
        </div>
        {/* Row 2 */}
        <div className="flex justify-between items-center gap-4">
          <div className="bg-gray-300/10 p-4 rounded-md flex-none w-1/4 flex justify-center items-center border-2 border-black">
            <span className="text-xl font-bold">2</span>
          </div>
          <div className="bg-gray-300/10 p-4 rounded-md flex-grow flex justify-center items-center border-2 border-black">
            <p className="text-xl font-bold">3647</p>
          </div>
        </div>
        {/* Row 3 */}
        <div className="flex justify-between items-center gap-4">
          <div className="bg-gray-300/10 p-4 rounded-md flex-none w-1/4 flex justify-center items-center border-2 border-black">
            <span className="text-xl font-bold">3</span>
          </div>
          <div className="bg-gray-300/10 p-4 rounded-md flex-grow flex justify-center items-center border-2 border-black">
            <p className="text-xl font-bold">1957</p>
          </div>
        </div>
        {/* Row 4 */}
        <div className="flex justify-between items-center gap-4">
          <div className="bg-gray-300/10 p-4 rounded-md flex-none w-1/4 flex justify-center items-center border-2 border-black">
            <span className="text-xl font-bold">4</span>
          </div>
          <div className="bg-gray-300/10 p-4 rounded-md flex-grow flex justify-center items-center border-2 border-black">
            <p className="text-xl font-bold">4538</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DailyStatisticsPanel;