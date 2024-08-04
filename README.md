-Set Up a Virtual Environment:
```bash
cd
python -m venv mlvenv
source mlvenv/bin/activate

-Install Required Libraries:i
```bash
pip install fastapi uvicorn transformers torch

-Run the application using Uvicorn:
```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload

-Test the API:
```bash
curl -X POST "http://localhost:8000/suggestions/" -H "Content-Type: application/json" -d '{"sentence": "have a <blank> day"}'

-Docker Build:
```bash
systemctl start docker
docker build -t mlops .
docker run -p 8000:8000 mlops

-Start the Locust server at http://localhost:8089:
```bash
locust -f locustfile.py --host=http://localhost:8000
