# MLOps Application

This repository contains a FastAPI application that provides text suggestions to fill in blanks in sentences, ensuring that the suggestions are positive. The application utilizes pre-trained NLP models from Hugging Face's Transformers library.

## Table of Contents

- [Requirements](#requirements)
- [Building and Running the Application with Docker](#building-and-running-the-application-with-docker)
- [API Documentation](#api-documentation)
- [Load Testing with Locust](#load-testing-with-locust)
- [Monitoring with Prometheus](#monitoring-with-prometheus)
- [CI/CD with GitHub Actions](#cicd-with-github-actions)

## Requirements

- Docker

## Building and Running the Application with Docker

### Step 1: Start Docker

Make sure Docker is running on your machine. You can start Docker using the following command:

```bash
systemctl start docker
```

### Step 2: Build the Docker Image

Navigate to the directory where the `Dockerfile` is located and build the Docker image for the FastAPI application:

```bash
docker build -t mlops .
```

### Step 3: Run the Docker Container

Run the Docker container, mapping port 8000 of the container to port 8000 on your host machine:

```bash
docker run --network host -p 8000:8000 mlops
```
## API Documentation

### Get Positive Suggestions

- **Endpoint**: `/suggestions/`
- **Method**: `POST`
- **Description**: Accepts a sentence with a `<blank>` placeholder and returns a list of positive suggestions to fill in the blank.

You can also access the interactive API documentation by running your application and navigating to `http://localhost:8000/docs` (Swagger UI) or `http://localhost:8000/redoc` (ReDoc).

#### Request

- **Content-Type**: `application/json`
- **Body**:
    ```json
    {
      "sentence": "have a <blank> day"
    }
    ```

#### Response

- **200 OK**: Returns a list of positive suggestions.
    ```json
    {
      "suggestions": ["good", "excellent", "amazing"]
    }
    ```
- **400 Bad Request**: If the input does not contain `<blank>`.
    ```json
    {
      "detail": "Input must contain '<blank>'"
    }
    ```

### Example Usage

You can test the API using `curl`:

```bash
curl -X POST "http://localhost:8000/suggestions/" -H "Content-Type: application/json" -d '{"sentence": "have a <blank> day"}'

## Load Testing with Locust

To perform load testing, you can use Locust. Follow these steps:

### Step 1: Build the Locust Docker Image

Build the Docker image for Locust:

```bash
docker build -t locust-test -f Dockerfile.locust .
```

### Step 2: Run the Locust Load Test

Run the Locust load test:

```bash
docker run --network host -d --name locust-test locust-test
```

### Step 3: Access the Locust Web Interface

Open your web browser and navigate to `http://localhost:8089` to configure and start the load test.

## Monitoring with Prometheus

To monitor the application with Prometheus, follow these steps:

### Step 1: Create a Prometheus Configuration File

Create a `prometheus.yml` configuration file in the root directory with the following content:

### Step 1: Run Prometheus

Run Prometheus using the following command:

```bash
docker run --network host -p 9090:9090 -v $(pwd)/prometheus.yml:/etc/prometheus/prometheus.yml prom/prometheus
```

### Step 2: Access the Prometheus Web Interface

Open your web browser and navigate to `http://localhost:9090` to access the Prometheus web interface.

## CI/CD with GitHub Actions

This repository includes a GitHub Actions workflow for continuous integration. The workflow builds the Docker image and runs tests on every push and pull request to the `main` branch. Load Testing with Locust is also included.

