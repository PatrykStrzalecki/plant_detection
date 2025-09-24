import React, { useState } from 'react';
import { Upload, X, Check } from 'lucide-react';

// API endpoints
const UPLOAD_URL = "http://localhost:8000/upload-image";
const STATUS_URL = "http://localhost:8000/task-status/";
const WS_URL = "ws://localhost:8000/ws/task-status/";

const UploadScreen = ({ onViewChange, views, onProcessComplete }) => {
  const [file, setFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState("idle"); // idle | uploading | processing | success | error

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      setPreviewUrl(URL.createObjectURL(selectedFile));
      setUploadStatus("idle");
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
      setUploadStatus("idle");
    }
  };

  const handleRemoveFile = () => {
    setFile(null);
    setPreviewUrl(null);
    setUploadStatus("idle");
  };

  const handleUpload = async () => {
    if (!file) {
      return;
    }

    setUploadStatus("uploading");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch(UPLOAD_URL, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      const taskId = data.id;
      setUploadStatus("processing");

      const socket = new WebSocket(WS_URL + taskId);

      socket.onopen = () => {
        console.log(`WebSocket connection established for task ID: ${taskId}`);
      };

      socket.onmessage = async (event) => {
        const socketData = JSON.parse(event.data);
        const taskStatus = socketData.status;

        if (taskStatus === "SUCCESS") {
          setUploadStatus("success");
          socket.close();

          const resultResponse = await fetch(STATUS_URL + taskId);
          const resultData = await resultResponse.json();

          onProcessComplete(resultData);
          
          setTimeout(() => {
            onViewChange(views.DASHBOARD);
          }, 500);
        } else if (taskStatus === "FAILURE") {
          setUploadStatus("error");
          socket.close();
        }
      };

      socket.onclose = () => {
        console.log(`WebSocket connection closed for task ID: ${taskId}`);
      };

      socket.onerror = (error) => {
        console.error(`WebSocket error: ${error.message}`);
        setUploadStatus("error");
      };

    } catch (error) {
      console.error("Error during upload or processing:", error);
      setUploadStatus("error");
    }
  };

  let buttonText = "Upload";
  if (uploadStatus === "uploading") {
    buttonText = "Uploading...";
  } else if (uploadStatus === "processing") {
    buttonText = "Processing...";
  } else if (uploadStatus === "success") {
    buttonText = "Uploaded Successfully!";
  } else if (uploadStatus === "error") {
    buttonText = "Upload Failed";
  }

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
              <img src={previewUrl} alt="Image preview" className="w-full h-full object-contain" />
              <button 
                onClick={handleRemoveFile} 
                className="absolute top-2 right-2 bg-black/50 text-white rounded-full p-1"
              >
                <X className="size-4" />
              </button>
            </div>
          )}
          {uploadStatus === "success" ? (
            <div className="flex items-center text-green-500 font-bold text-lg">
              <Check className="size-6 mr-2" />
              Uploaded successfully!
            </div>
          ) : uploadStatus === "error" ? (
            <div className="flex items-center text-red-500 font-bold text-lg">
              <X className="size-6 mr-2" />
              An error occurred. Please try again.
            </div>
          ) : (
            <div className="flex items-center justify-between p-4 bg-gray-700 rounded-lg w-full">
              <span className="text-gray-300 text-sm font-semibold truncate max-w-sm">Selected file: {file.name}</span>
              <button 
                className="bg-green-900 text-white font-bold py-2 px-6 rounded-md hover:bg-green-700 transition-colors disabled:bg-gray-500 disabled:cursor-not-allowed"
                onClick={handleUpload}
                disabled={isLoading}
              >
                {buttonText}
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default UploadScreen;
