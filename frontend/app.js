const UPLOAD_URL = "http://localhost:8000/upload-image";
const STATUS_URL = "http://localhost:8000/task-status/";
const WS_URL = "ws://localhost:8000/ws/task-status/";

function uploadImage() {
    const fileInput = document.getElementById("image-file");
    const formData = new FormData();
    const statusDiv = document.getElementById("status");
    const resultDetailsDiv = document.getElementById("result-details");

    if (!fileInput.files || fileInput.files.length === 0) {
        statusDiv.textContent = "No file selected.";
        return;
    }

    formData.append("image", fileInput.files[0]);
    statusDiv.textContent = "Uploading image...";
    resultDetailsDiv.innerText = '';

    fetch(UPLOAD_URL, {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        const taskId = data.id
        statusDiv.textContent = `Upload successful! Task ID: ${taskId}. Waiting for results...`;
        connectWebSocket(taskId);
    })
    .catch(error => {
        statusDiv.textContent = `Error occurred: ${error.message}`;
    });
}


function connectWebSocket(taskId) {
    const statusDiv = document.getElementById("status");
    const resultDetailsDiv = document.getElementById("result-details");
    const socket = new WebSocket(WS_URL + taskId);

    socket.onopen = () => {
        console.log(`WebSocket connection established for task ID: ${taskId}`);
    }

    socket.onmessage = function(event) {
        const data = JSON.parse(event.data);
        if (data.status === "SUCCESS") {
            statusDiv.textContent = "Processing complete! Fetching results...";
            resultDetailsDiv.innerHTML = `<h3>Results:</h3><pre>${JSON.stringify(data.results, null, 2)}</pre>`;
            getTaskResults(data.task_id);
        } else if (data.status === "FAILURE") {
            statusDiv.textContent = "Task failed.";
        }
        socket.close();
    };

    socket.onclose = function() {
        console.log(`WebSocket connection closed for task ID: ${taskId}`);
    };

    socket.onerror = function(error) {
        statusDiv.textContent = `WebSocket error: ${error.message}`;
    };
}

function getTaskResults(taskId) {
    const resultDetailsDiv = document.getElementById("result-details");

    fetch(STATUS_URL + taskId)
        .then(response => response.json())
        .then(data => {
            const processedImageURL = 'http://localhost:8000' + data.processed_image_path;
            resultDetailsDiv.innerHTML = `
                <p>Status: <strong>${data.task_status}</strong></p>
                <p>Uploaded at: <strong>${data.uploaded_at}</strong></p>
                <p>Processed at: <strong>${data.processed_at}</strong></p>
                <p>Original image: <strong>${data.original_image_path}</strong></p>
                <p>Processed image: <strong>${data.processed_image_path}</strong></p>
                <h3>Results:</h3><img src="${processedImageURL}" id="result-image" alt="Processed Image">
            `;
        })
        .catch(error => {
            resultDetailsDiv.innerHTML = `<p>Error fetching task results: ${error.message}</p>`;
        });
}
