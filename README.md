-Set Up a Virtual Environment:
cd
python -m venv mlvenv
source mlvenv/bin/activate

-Install Required Libraries:i
pip install fastapi uvicorn transformers torch

-Run the application using Uvicorn:
uvicorn app:app --host 0.0.0.0 --port 8000 --reload

-Test the API:
curl -X POST "http://localhost:8000/suggestions/" -H "Content-Type: application/json" -d '{"sentence": "have a <blank> day"}'

-Docker Build:
sudo systemctl start docker
docker build -t mlops .
sudo docker run -p 8000:8000 mlops
