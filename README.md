# AI Product Agent – Python Backend

Welcome to the Python backend for **AI Product Agent**! This service delivers advanced AI-driven analysis and automation for your product management platform, integrating seamlessly as the intelligent backend. It is inteh=grated into the application [product_agent_node](https://github.com/YUGESHKARAN/product_agent_node.git).

---

## 🚀 Overview

This backend is built with **Flask** and leverages state-of-the-art LLMs (e.g., Llama 3 70B) to provide intelligent analysis and automation capabilities. It exposes RESTful APIs consumed by the main application.

---

## 🔥 Features

- **LLM-Powered Analysis:** Integrates Llama 3 70B or similar models for deep data analysis and smart recommendations.
- **RESTful API:** Clean, documented endpoints for easy integration with Node.js/React frontend and backend.
- **CORS-Enabled:** Out-of-the-box support for cross-origin requests.
- **Secure:** Designed for secure communication within your stack.
- **Configurable Model Path:** Easily switch or update AI models as needed.
- **Flexible Image Generation:**  
  - **SerpAPI Integration:** Use [SerpAPI](https://serpapi.com/) for AI-powered image generation. Implemented in `image_tools.py`.
  - **Unsplash API Integration:** Alternatively, generate images via [Unsplash API](https://unsplash.com/developers). Implemented in `image_tools2.py`.
  - **Image backend selection:** Modify the import on `mongodb_database.py`  
    ```python
    from image_tools2 import search_and_download_image
    ```
    to select either method based on your preferences and API accessibility.
- **Automatic AWS S3 Storage:** Downloaded images are automatically stored in your configured AWS S3 bucket. Ensure you provide your AWS S3 access keys for proper configuration.

---

## 🛠️ Tech Stack

- **Backend Framework:** Python 3.8+, Flask
- **AI Model:** Llama 3 70B (or compatible LLM)
- **Image Generation:** SerpAPI, Unsplash API (selectable)
- **Dependencies:** See [requirements.txt](./requirements.txt)

---

## 📁 Directory Structure

```
flask-ai/
├── app.py                # Main Flask application
├── model/                # Model utilities and loading
├── routes/               # API endpoints (analysis, inference, etc.)
├── image_tools.py        # Image generation via SerpAPI
├── image_tools2.py       # Image generation via Unsplash API
├── mongodb_database.py   # Database operations (modify import for image backend)
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables (model path, API keys, etc.)
└── ...
```

---

## ⚡ Getting Started

### Prerequisites

- [Python 3.8+](https://www.python.org/)
- (Optional) [CUDA](https://developer.nvidia.com/cuda-zone) for GPU inference
- Llama 3 70B or compatible model weights
- [SerpAPI Key](https://serpapi.com/manage-api-key) (for SerpAPI image generation)
- [Unsplash Access Key](https://unsplash.com/developers) (for Unsplash image generation)
- **AWS S3 credentials (for storing images in S3)**

### Installation

1. **Clone this repository:**
   ```bash
   git clone https://github.com/YUGESHKARAN/ai_product_agent.git
   cd ai_product_agent/flask-ai
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment:**
   - Create a `.env` file in `flask-ai/`:
     ```
     MODEL_PATH=/absolute/path/to/llama3-70b
     SERPAPI_KEY=your_serpapi_key        # Optional, for SerpAPI image generation
     UNSPLASH_ACCESS_KEY=your_unsplash_key  # Optional, for Unsplash image generation
     AWS_ACCESS_KEY_ID=your_aws_access_key_id      # Required, for S3 image storage
     AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key  # Required, for S3 image storage
     AWS_S3_BUCKET_NAME=your_bucket_name           # Required, for S3 image storage
     ```
   - (Adjust `MODEL_PATH`, API keys, and AWS S3 credentials as needed for your environment.)

### Running the Server

```bash
python app.py
```
- The API will default to `http://localhost:8000` unless otherwise configured.

---

## 🌐 Usage

- The Flask backend exposes endpoints for AI-powered analysis, inference, and image generation.
- Integrate with your main backend/frontend via HTTP requests.

### Image Generation

- You can choose which image generation backend to use:
  - **SerpAPI:** Utilizes `image_tools.py`—requires `SERPAPI_KEY`.
  - **Unsplash:** Utilizes `image_tools2.py`—requires `UNSPLASH_ACCESS_KEY`.
- To select your preferred backend, modify the import in `mongodb_database.py` as described above.
- Downloaded images will be stored in your configured AWS S3 bucket. Ensure your AWS credentials are set in the `.env` file.

### Example API Usage

- **Analysis Endpoint:**
  ```
  POST /analyze
  {
    "product_data": {...}
  }
  ```
  Response:
  ```json
  {
    "analysis": "LLM-powered insights here."
  }
  ```

- **Image Generation (Example):**
  ```
  POST /generate-image
  {
    "prompt": "modern workspace"
  }
  ```
  Response (URL or image data, depending on backend and implementation).

---

## 🛡️ Security

- The backend is intended for internal use behind your main application’s authentication layer.
- Set up firewall rules and/or JWT authentication if exposing to public networks.

---

## 🤝 Contributing

Contributions are welcome! Open issues or submit pull requests for improvements, bug fixes, or new features.

---

## 📄 License

This project is licensed under the [MIT License](../LICENSE).

---

**Empowering your product management with AI-powered analysis, smart automation, and flexible image generation!**
