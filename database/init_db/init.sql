CREATE TABLE IF NOT EXISTS detection_results (
    id SERIAL PRIMARY KEY,
    original_image_path VARCHAR(255) NOT NULL,
    processed_image_path VARCHAR(255),
    task_status VARCHAR(50) NOT NULL DEFAULT 'pending',
    uploaded_at TIMESTAMP NOT NULL DEFAULT NOW(),
    processed_at TIMESTAMP,
    num_flowers INTEGER,
    category INTEGER,
    bounding_boxes JSONB
)
CREATE INDEX IF NOT EXISTS idx_detection_results_original_image_path ON detection_results (original_image_path);
CREATE INDEX IF NOT EXISTS idx_detection_results_task_status ON detection_results (task_status);