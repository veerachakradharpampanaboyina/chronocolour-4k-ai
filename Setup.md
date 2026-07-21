⚠️ Note on standard running commands
In your terminal, running npm start inside backend/ failed because the backend is a Python FastAPI service, not a Node.js package.

Here is how the project components are run:

Backend (Python): Uses uvicorn / docker / celery
Frontend (Next.js): Uses npm run dev or npm run build && npm start inside frontend/
Full Stack (Recommended): Runs via Docker Compose with a single command!
📋 Production Launch Checklist
To bring ChronoColor 4K AI live in a production GPU environment:

1. Hardware & System Requirements
Server: Linux server (Ubuntu 22.04 LTS recommended) or Windows Server with NVIDIA GPU (≥16GB VRAM for 4K AI models).
Drivers: NVIDIA Drivers + NVIDIA Container Toolkit (nvidia-docker2) installed so Docker containers can access GPU resources.
2. Download AI Model Weights
Run the download script to pull model weights into the ./models/ directory:

bash
bash scripts/download_models.sh
3. Configure Production Environment (.env)
Create .env from .env.example and update default security credentials:

bash
cp .env.example .env
Ensure you update:

MONGO_INITDB_ROOT_PASSWORD
MINIO_ROOT_PASSWORD
SECRET_KEY
4. Launch Full Production Stack with Docker Compose
Run all 8 microservices (API, Workers, Beat, Flower, Frontend, Mongo, Redis, MinIO) detached:

bash
docker compose up -d --build
🌐 Accessing Services
Once deployed, your services will be available at:

Service	Port	Description
Web Frontend	http://localhost:3000	Landing page, Upload, & Dashboard
FastAPI Backend API	http://localhost:8000/docs	Swagger Interactive API documentation
Flower (Celery Monitor)	http://localhost:5555	Real-time GPU worker & task monitoring
MinIO Console	http://localhost:9001	Object Storage dashboard for video assets
🛠️ Local Development Quick Commands
If you want to run services individually for testing without Docker:

Backend API:

bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
Celery GPU Worker:

bash
cd backend
celery -A app.workers.celery_app worker --loglevel=info -Q gpu,default
Frontend:

bash
cd frontend
npm run dev
