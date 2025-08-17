const UPLOAD_URL = "http://localhost:8000/upload-image";
const STATUS_URL = "http://localhost:8000/task-status/";
const WS_URL = "ws://localhost:8000/ws/task-status/";

const navButtons = document.querySelectorAll('.nav-button');
const panels = document.querySelectorAll('.panel');
const uploadButton = document.querySelector('.upload-form-container button');
const fileInput = document.getElementById("image-file");

// Mocked PLC status
const plcStatusIndicator = document.getElementById("plc-status");
plcStatusIndicator.classList.add('connected'); // Mock: always connected

// UI Logic
navButtons.forEach(button => {
    button.addEventListener('click', () => {
        const targetId = button.dataset.target;

        panels.forEach(panel => {
            if (panel.id === targetId) {
                panel.classList.add('visible');
                panel.classList.remove('hidden');
            } else {
                panel.classList.add('hidden');
                panel.classList.remove('visible');
            }
        });

        navButtons.forEach(btn => btn.classList.remove('active'));
        button.classList.add('active');
    });
});

// Mocked machine control logic
const startButton = document.getElementById("start-button");
const redIndicator = document.getElementById("status-red");
const greenIndicator = document.getElementById("status-green");
let isRunning = false;

startButton.addEventListener('click', () => {
    isRunning = !isRunning;
    if (isRunning) {
        greenIndicator.classList.add('active');
        redIndicator.classList.remove('active');
    } else {
        greenIndicator.classList.remove('active');
        redIndicator.classList.add('active');
    }
});

function uploadImage() {
    console.log("Starting image upload process...");
    const formData = new FormData();
    const statusDiv = document.getElementById("status");

    if (!fileInput.files || fileInput.files.length === 0) {
        statusDiv.textContent = "No file selected.";
        return;
    }
    console.log("Selected file:", fileInput.files[0].name);

    formData.append("file", fileInput.files[0]);
    console.log("File details:", {
        name: fileInput.files[0].name,
        size: fileInput.files[0].size,
        type: fileInput.files[0].type
    });
    statusDiv.textContent = "Uploading image...";

    fetch(UPLOAD_URL, {
        method: "POST",
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        const taskId = data.id
        statusDiv.textContent = `Upload successful! Task ID: ${taskId}. Waiting for results...`;
        document.querySelector('[data-target="detection-results"]').click();
        connectWebSocket(taskId);
    })
    .catch(error => {
        statusDiv.textContent = `Error occurred: ${error.message}`;
        console.error("Error during upload:", error);
    });
}


function connectWebSocket(taskId) {
    const statusDiv = document.getElementById("status");
    const socket = new WebSocket(WS_URL + taskId);

    socket.onopen = () => {
        console.log(`WebSocket connection established for task ID: ${taskId}`);
    }

    socket.onmessage = function(event) {
        const data = JSON.parse(event.data);
        const taskStatus = data.status;
        document.getElementById("processing-status").textContent = taskStatus.toUpperCase();

        if (taskStatus === "SUCCESS") {
            getTaskResults(data.task_id);
            document.getElementById("processing-status").textContent = taskStatus.toUpperCase();
            socket.close();
        } else if (taskStatus === "FAILURE") {
            document.getElementById("processing-status").textContent = taskStatus.toUpperCase();
            socket.close();
        }
    };

    socket.onclose = function() {
        console.log(`WebSocket connection closed for task ID: ${taskId}`);
    };

    socket.onerror = function(error) {
        statusDiv.textContent = `WebSocket error: ${error.message}`;
    };
}

function getTaskResults(taskId) {
    fetch(STATUS_URL + taskId)
        .then(response => response.json())
        .then(data => {
            const processedImageURL = 'http://localhost:8000/' + data.processed_image_path;
            const imageDisplayDiv = document.getElementById('image-display');
            imageDisplayDiv.innerHTML = `<img src="${processedImageURL}" alt="Processed Image">`;
            document.getElementById('detected-flowers').textContent = data.num_flowers || 'N/A';
            document.getElementById('assigned-category').textContent = data.category || 'N/A';
            
            const uploadedTime = new Date(data.uploaded_at);
            const processedTime = new Date(data.processed_at);
            const processingDuration = (processedTime - uploadedTime) / 1000;

            document.getElementById('processing-time').textContent = `${processingDuration.toFixed(4)} s`;
        })
        .catch(error => {
            console.error("Error fetching task results:", error);
        });
}
