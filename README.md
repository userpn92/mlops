```bash
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

-Start the Locust server at http://localhost:8089:
locust -f locustfile.py --host=http://localhost:8000

-Docker Build:
systemctl start docker
docker build -t mlops .
#docker run -p 8000:8000 mlops
docker run -it --network host -p 8000:8000 mlops

-Locust Docker Build:
docker build -t locust-test -f Dockerfile.locust .
docker run --network host -d --name locust-test

-Run Prometheus:
docker run --network host -p 9090:9090 -v $(pwd)/prometheus.yml:/etc/prometheus/prometheus.yml prom/prometheus

