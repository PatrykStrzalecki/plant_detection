# 🚀 **YOLO Image Processing API (FastAPI + Celery + Redis + PostgreSQL + GPU)**

## 📌 **Project Overview**

This project is a microservice-based application for asynchronous image processing using `YOLO` (`Ultralytics`) and `PyTorch` with `NVIDIA GPU` support.
It follows a `FastAPI` + `Celery` + `Redis` + `PostgreSQL` architecture and is fully containerized using `Docker` + `docker-compose`.

🔹 **Key goals:**

- Separated services: Backend (`API`), Worker (`Celery`), `Redis`, `PostgreSQL`.

- Asynchronous job queue – backend remains responsive while heavy tasks are processed in the background.

- Image processing with `YOLO` inference.

- Shared `/data` folder between backend and worker (input/output images).

- Full `GPU` acceleration using `NVIDIA Container Toolkit`.

🛠️ **Tech Stack:**

- **FastAPI** – REST API framework

- **Celery** – asynchronous job queue

- **Redis** – message broker and result backend for Celery

- **PostgreSQL** – database for metadata and task statuses

- **Ultralytics YOLO + PyTorch** – object detection model

- **Docker + NVIDIA Container Toolkit** – containerization with GPU support

## 🔄 **Data Flow & How It Works**

1️⃣ **Image Upload**

- The client uploads an image to the `/upload-image` endpoint (FastAPI backend).
- The backend saves the file into `data/input/` and creates a record in PostgreSQL.

2️⃣ **Task Queueing**

- Backend sends a Celery task to Redis with the file path.
- Redis acts as the broker for queued jobs.

3️⃣ **Image Processing**

- Celery Worker receives the task from Redis.
- Loads YOLO (Ultralytics) and runs inference using GPU.
- Saves processed results into `data/output/`.

4️⃣ **Results & Status Update**

- Worker updates the task status in PostgreSQL `(processing → done)`.
- Output files are ready to be fetched via API.

5️⃣ **Result Retrieval**

- The client fetches results via `/get-result/{task_id}` or checks the status.

## 📊 **System Architecture**

- **Backend** handles API and database operations.

- **Worker** performs heavy GPU-based computations.

- **Redis** passes tasks between backend and worker.

- **PostgreSQL** stores metadata and task statuses.

## 📌 **Requirements**

- **Docker** + **docker-compose**

- **WSL2** (Ubuntu) or native Linux

- **NVIDIA GPU** + drivers

- **nvidia-container-toolkit** installed

## 🚧 **Roadmap**

✅ Initial version – backend + worker + redis + db

🔜 Add frontend (React + Tailwind) for image upload and result preview.

🔜 Support for multiple YOLO versions (v8, v9).

🔜 Celery monitoring with Flower.

🔜 CI/CD pipeline (GitHub Actions).

🔜 User authentication & authorization.