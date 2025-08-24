import React from 'react';

// This component is responsible for displaying the connection status
// with the PLC controller and its IP address.
// In the future, will add logic for changing colors here.
const PLCStatus = () => {
  return (
    <div className="flex-shrink-0 flex items-center gap-2">
      <div className="flex-none rounded-full bg-emerald-500/30 p-1">
        <div className="size-1.5 rounded-full bg-emerald-500"></div>
      </div>
      <span className="text-sm text-gray-400">192.168.1.1</span>
    </div>
  );
};

export default PLCStatus;