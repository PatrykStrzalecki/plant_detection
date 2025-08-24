import React, { useState, useEffect } from 'react';
import { Play, Pause, Plus, Minus } from 'lucide-react';

const MachineControlPanel = () => {

  const [isMachineActive, setIsMachineActive] = useState(false);
  const [autoStop, setAutoStop] = useState(true);
  const [speed, setSpeed] = useState(60);

  // Function to increase speed
  const increaseSpeed = () => {
    setSpeed(prevSpeed => prevSpeed + 1);
  };

  // Function to decrease speed
  const decreaseSpeed = () => {
    setSpeed(prevSpeed => prevSpeed - 1);
  };

  const handleStartStop = () => {
    setIsMachineActive(prevState => !prevState);
  };

  return (
    <div className="bg-stone-950/40 p-5 rounded-lg shadow-md flex flex-col items-center justify-between h-full">
      {/* Gray header with button and controls */}
      <div className="bg-gray-300/10 w-full p-4 rounded-md flex items-center justify-center h-24 border-2 border-black">
        <div className="flex items-center gap-2">
          {/* Red light - active when machine is inactive */}
          {/* Additional container ensures consistent size so button doesn't jump */}
          <div className={`flex-none rounded-full p-1 ${isMachineActive ? '' : 'bg-red-500/30'}`}>
            <div className={`size-5 rounded-full bg-red-500 ${isMachineActive ? 'opacity-30' : ''}`}></div>
          </div>
          <button
            className={`flex items-center justify-center h-14 w-28 gap-2 rounded-md text-sm font-medium text-gray-300 hover:text-white border-2 border-black transition-colors duration-300
              ${isMachineActive ? 'bg-red-900 hover:bg-red-700' : 'bg-green-900 hover:bg-green-700'}`}
            onClick={handleStartStop}
          >
            {isMachineActive ? <Pause className="size-4" /> : <Play className="size-4" />}
            {isMachineActive ? 'STOP' : 'START'}
          </button>
          {/* Green light - active when machine is active */}
          {/* Additional container ensures consistent size so button doesn't jump */}
          <div className={`flex-none rounded-full p-1 ${isMachineActive ? 'bg-emerald-500/30' : ''}`}>
            <div className={`size-5 rounded-full bg-emerald-500 ${isMachineActive ? '' : 'opacity-30'}`}></div>
          </div>
        </div>
      </div>

      {/* Container 2: Speed Control */}
      <div className="bg-gray-300/10 p-4 rounded-lg flex flex-col items-center gap-2 p-8 max-w-xs border-2 border-black">
        {/* Button "+" */}
        <button 
          className="bg-green-900 text-gray-300 w-12 h-12 rounded-full flex items-center justify-center text-2xl font-bold hover:bg-green-700 hover:text-white border-2 border-black"
          onClick={increaseSpeed}
        >
          <Plus className="size-4" />
        </button>
        {/* Speed Display */}
        <div className="bg-neutral-700 w-24 h-24 rounded-md flex items-center justify-center text-4xl font-bold border-2 border-black">
          {speed}
        </div>
        {/* Button "-" */}
        <button 
          className="bg-green-900 text-gray-300 w-12 h-12 rounded-full flex items-center justify-center text-2xl font-bold hover:bg-green-700 hover:text-white border-2 border-black"
          onClick={decreaseSpeed}
        >
          <Minus className="size-4" />
        </button>
      </div>

      {/* Container 3: Auto Stop - updated appearance */}
      <div className="bg-gray-300/10 p-4 rounded-lg flex flex-col items-center gap-4 w-full border-2 border-black">
        <div className="flex items-center justify-around w-full">
          <div className="flex flex-col items-center">
            <span className="text-sm font-bold mb-2">AUTO STOP</span>
            <div 
              className={`w-12 h-6 rounded-full cursor-pointer transition-colors 
                ${autoStop ? 'bg-green-600' : 'bg-gray-600'}`}
              onClick={() => setAutoStop(!autoStop)}
            >
              <div className={`w-5 h-5 bg-white rounded-full mt-0.5 transition-transform 
                ${ autoStop ? 'translate-x-6' : 'translate-x-0.5'}`}
              >
              </div>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {/* hours */}
            <div className="bg-neutral-700 w-16 h-16 rounded-md flex items-center justify-center text-3xl font-bold border-2 border-black">
              10
            </div>
            <span className="text-3xl font-bold">:</span>
            {/* minutes */}
            <div className="bg-neutral-700 w-16 h-16 rounded-md flex items-center justify-center text-3xl font-bold border-2 border-black">
              30
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MachineControlPanel;



