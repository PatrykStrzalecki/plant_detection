import React, { useEffect, useRef, useState } from 'react';

// Hook for automatically adjusting square size
function useSquareSize(containerRef) {
  const [size, setSize] = useState(0);

  useEffect(() => {
    if (!containerRef.current) return;

    const updateSize = () => {
      const rect = containerRef.current.getBoundingClientRect();
      const minDimension = Math.min(rect.width, rect.height);
      setSize(minDimension);
    };

    updateSize();

    const observer = new ResizeObserver(updateSize);
    observer.observe(containerRef.current);

    return () => observer.disconnect();
  }, [containerRef]);

  return size;
}

const ResultsPanel = ({ processedResult }) => {
  const containerRef = useRef(null);
  const size = useSquareSize(containerRef);

  const detectedObjects = processedResult?.num_flowers || 'N/A';
  const uploadedTime = processedResult?.uploaded_at ? new Date(processedResult.uploaded_at) : null;
  const processedTime = processedResult?.processed_at ? new Date(processedResult.processed_at) : null;
  const processingTime = (uploadedTime && processedTime) ? ((processedTime.getTime() - uploadedTime.getTime()) / 1000).toFixed(4) : 'N/A';
  const processedImagePath = processedResult?.processed_image_path || null;

  return (
    <div className="bg-stone-950/40 p-5 rounded-lg shadow-md flex flex-col h-full min-h-0 overflow-hidden">
      <div className="w-full mb-4 flex-shrink-0">
        <div className="flex justify-between items-center gap-4">
          {/* Left header for "Detected flowers" */}
          <div className="bg-gray-300/10 p-4 rounded-md text-sm w-1/2 flex items-center justify-center h-24 border-2 border-black">
            <div className="flex flex-col items-center">
              <span>Detected flowers:</span>
              <span className="font-bold text-2xl">{detectedObjects}</span>
            </div>
          </div>

          {/* Right header for "Processing time" */}
          <div className="bg-gray-300/10 p-4 rounded-md text-sm w-1/2 flex items-center justify-center h-24 border-2 border-black">
            <div className="flex flex-col items-center">
              <span>Processing time:</span>
              <span className="font-bold text-2xl">{processingTime} s</span>
            </div>
          </div>
        </div>
      </div>

      {/* Container for the image - automatically adjusts size while maintaining square aspect ratio */}
      <div
        ref={containerRef}
        className="flex-grow min-h-0 flex items-center justify-center overflow-hidden"
      >
        <div 
          className="bg-gray-800 rounded-md border-2 border-gray-600 flex justify-center items-center"
          style={{ width: `${size}px`, height: `${size}px` }}
        >
          {processedResult ? (
            <img 
              src={`http://localhost:8000/${processedImagePath}`}
              alt="Processed Result" 
              className="w-full h-full object-contain"
            />
          ) : (
            <span className="text-gray-500">No image processed yet.</span>
          )}
        </div>
      </div>
    </div>
  );
};

export default ResultsPanel;