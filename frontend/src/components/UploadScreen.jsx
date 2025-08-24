import React, { useState } from 'react';
import { Upload, X, Check } from 'lucide-react';

const UploadScreen = ({ onViewChange, views }) => {
  const [file, setFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState(false);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      setPreviewUrl(URL.createObjectURL(selectedFile));
      setUploadSuccess(false);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    const selectedFile = e.dataTransfer.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      setPreviewUrl(URL.createObjectURL(selectedFile));
      setUploadSuccess(false);
    }
  };

  const handleRemoveFile = () => {
    setFile(null);
    setPreviewUrl(null);
    setUploadSuccess(false);
  };

  const handleUpload = async () => {
    if (!file) {
      return;
    }

    setIsLoading(true);

    // Simulate file upload to API
    setTimeout(() => {
      setIsLoading(false);
      setUploadSuccess(true);

      // After successful upload, return to Dashboard view
      // Use setTimeout to give the user a moment to see the message
      setTimeout(() => {
        onViewChange(views.DASHBOARD);
      }, 1500);

    }, 2000); // Simulate 2 seconds delay
    
  };

  return (
    <div className="flex flex-col items-center justify-center p-8 bg-gray-800/50 rounded-lg shadow-md w-full max-w-2xl h-96 border-2 border-black">
      {!file ? (
        <label 
          htmlFor="file-upload" 
          className="flex flex-col items-center justify-center w-full h-full cursor-pointer"
          onDragOver={handleDragOver}
          onDrop={handleDrop}
        >
          <div className="flex flex-col items-center justify-center w-full h-full border-2 border-dashed border-gray-400 rounded-lg p-6 hover:bg-gray-700/50 transition-colors">
            <Upload className="size-16 text-gray-400" />
            <span className="mt-4 text-gray-400 text-lg">Drag and drop a file or click to select</span>
          </div>
          <input 
            id="file-upload" 
            type="file" 
            className="hidden" 
            onChange={handleFileChange} 
            accept="image/*"
          />
        </label>
      ) : (
        <div className="flex flex-col items-center justify-center w-full h-full">
          {previewUrl && (
            <div className="relative w-full h-64 overflow-hidden rounded-lg mb-4 border border-gray-600">
              <img src={previewUrl} alt="Podgląd wybranego pliku" className="w-full h-full object-contain" />
              <button 
                onClick={handleRemoveFile} 
                className="absolute top-2 right-2 bg-black/50 text-white rounded-full p-1"
              >
                <X className="size-4" />
              </button>
            </div>
          )}
          {uploadSuccess ? (
            <div className="flex items-center text-green-500 font-bold text-lg">
              <Check className="size-6 mr-2" />
              Uploaded successfully!
            </div>
          ) : (
            <div className="flex items-center justify-between p-4 bg-gray-700 rounded-lg w-full">
              <span className="text-gray-300 text-sm font-semibold truncate max-w-sm">Selected file: {file.name}</span>
              <button 
                className="bg-green-900 text-white font-bold py-2 px-6 rounded-md hover:bg-green-700 transition-colors disabled:bg-gray-500 disabled:cursor-not-allowed"
                onClick={handleUpload}
                disabled={isLoading}
              >
                {isLoading ? 'Uploading...' : 'Upload'}
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default UploadScreen;
