import React from 'react';
import DailyStatisticsPanel from './DailyStatisticsPanel';
import ResultsPanel from './ResultsPanel';
import MachineControlPanel from './MachineControlPanel';

const Dashboard = ({ processedResult, statistics, onResetStatistics }) => {
  return (
    <div className="grid grid-cols-[1fr_2fr_1fr] gap-5 w-full h-full max-h-full overflow-hidden">
        <DailyStatisticsPanel 
          processedResult={processedResult} 
          statistics={statistics} 
          onResetStatistics={onResetStatistics} 
        />
        <ResultsPanel processedResult={processedResult}/>
        <MachineControlPanel />
    </div>
  );
};

export default Dashboard;