# MTCARS FastAPI Deployment

## Overview

This project trains a linear regression model trained on the `mtcars.csv` dataset with `mpg` as the response variable and `wt`, `qsec`, and `am` as predictors. The trained model is served through a FastAPI application, containerized with Podman, and deployed to Google Cloud Run.

## Description

Pipeline for **MTCARS FastAPI API**:

1. Use `mtcars.csv` dataset
2. Train a predictive linear model in Python with:
   - response variable: `mpg`
   - predictors: weight (`wt`), quarter-mile time (`qsec`), and transmission type (`am`)
3. Build a FastAPI application that serves predictions from that model
4. Run the API locally with Podman
5. Push container image to a registry
6. Deploy the API to Google Cloud Run
7. Make the repo reproducible for cloning and running

## Required Dataset

`mtcars.csv`

## Repo Structure

```text
mtcars-fastapi-repo/
├── README.md
├── mtcars.csv
├── Dockerfile
├── .dockerignore
├── requirements.txt
├── app/
│   └── main.py
├── models/
│   └── model.pkl
├── scripts/
│   └── train_model.py
└── tests/
    └── test_api.py
```

## Local Setup

Create and activate a virtual environment:

```bash
uv venv
source .venv/bin/activate
```

Install dependencies:

```bash
uv pip install -r requirements.txt
```

## Modeling

Train a linear regression model in Python using `mtcars.csv`.

### Pipeline

- Load `mtcars.csv`
- Use `mpg` as the response
- Use weight (`wt`), quarter-mile time (`qsec`), and transmission type (`am`) as predictor variables
- Train a linear regression model in Python
- Save the trained model to disk

### Libraries

- `pandas`
- `scikit-learn`
- `joblib` or `pickle`

### Workflow

- Trained in a Python script: `scripts/train_model.py`.
- Trained model is saved to: `models/model.pkl.`

Train the model with:

```bash
uv run python scripts/train_model.py
```

## FastAPI Application

Create a FastAPI application that loads the trained model and serves predictions.

### Endpoints

1. **GET `/health`**
   - returns a success response if the API is running
   - no authentication required

2. **GET `/ready`**
   - returns a success response if the model is loaded and ready
   - returns a non-200 response if the model is missing or unavailable

3. **POST `/predict`**
   - accepts input values for the predictor variables used by your model
   - validates input with Pydantic
   - returns the predicted `mpg`

## Input Validation and Error Handling

API includes:

- Pydantic request validation
- helpful errors for invalid input
- graceful handling if the model cannot be loaded

Validation rules:

- `wt` must be greater than `0`
- `qsec` must be greater than `0`
- `am` must be either `0` or `1`

## Run Locally with Podman

Project runs locally in a container with Podman.

### Required files

#### `Dockerfile`

Dockerfile:

- uses a Python 3.11-slim base image
- copies the application code and model artifact
- installs dependencies
- exposes port `8080`
- starts the FastAPI app when the container runs

#### `.dockerignore`

Exclude unnecessary files:

- .git
- .venv
- **pycache**
- \*.pyc
- scripts/
- tests/
- .python-version
- uv.lock
- pyproject.toml

### Run locally with Podman

Build the container image:

```bash
podman build -t mtcars-fastapi .
```

Run the container locally on port `8080`:

```bash
podman run --rm -p 8080:8080 mtcars-fastapi
```

The API should now be available at:

```text
http://localhost:8080
```

## Deployment

Deploy containerized API to Google Cloud Run.

Your README must include:

- how to build the image
- how to run it locally
- how to tag and push the image
- how to deploy it to Cloud Run
- your deployed API URL

## Reproducibility and Documentation

Should be able to:

- clone repo
- install dependencies
- rebuild model
- run API locally
- call API successfully
- understand what files are doing what

### This README includes

- project overview
- description of the model
- variables used for prediction
- local setup instructions
- Podman build and run commands
- API endpoint documentation
- example request and response
- deployment instructions
- deployed API URL
- short explanation of repo structure

### Example API calls

#### Health Check

Request:

```bash
curl http://localhost:8080/health
```

Expected response:

```json
{
  "status": "ok"
}
```

#### Readiness Check

Request:

```bash
curl http://localhost:8080/ready
```

Expected response:

```json
{
  "status": "ready"
}
```

#### Predict MPG

Request:

```bash
curl -X POST "http://localhost:8080/predict" \
  -H "Content-Type: application/json" \
  -d '{"wt": 2.62, "qsec": 16.46, "am": 1}'
```

Example response:

```json
{
  "predicted_mpg": 21.0,
  "model_version": "v1.0"
}
```

The response should show a predicted `mpg`. The exact `predicted_mpg` value may differ depending on the trained model.

## Testing

Automated API tests in `tests/test_api.py`:

- test `/health`
- test readiness endpoint
- test one successful `/predict` request
- test invalid input
- test missing field behavior

Run tests with:

```bash
pytest tests/test_api.py -v
```

Expected result:

```text
7 passed
```

## Production-Oriented Features

Include or clearly discuss the following:

- health check endpoint
- readiness check endpoint
- request/response validation with Pydantic
- clear error handling
- automatic FastAPI docs
- environment-based configuration
- containerization with Podman
- deployment documentation
- tests
- logging
- rate limiting

## Technical Requirements

### Repo includes

- FastAPI app
- trained model artifact
- model training workflow
- `mtcars.csv`
- `Dockerfile`
- `.dockerignore`
- dependency file
- README
- automated tests

### Code quality

- clear file organization
- meaningful variable names
- type hints where appropriate
- readable, reproducible code
- secrets kept out of version control

## Deployment Checklist

- [✔] model trained from `mtcars.csv`
- [✔] `mpg` used as the response
- [✔] FastAPI app works locally
- [✔] `/health` works
- [✔] `/ready` works
- [✔] `/predict` works
- [✔] request validation works
- [✔] Podman container builds successfully
- [✔] Podman container runs locally
- [ ] API deployed to Cloud Run
- [ ] README is complete
- [✔] at least one automated test is included
- [✔] repo is reproducible for another user

## Local Workflow

```bash
# create virtual environment
uv venv
source .venv/bin/activate

# install dependencies
uv pip install -r requirements.txt

# train your model
uv run scripts/train_model.py

# run locally
uvicorn app.main:app --host 0.0.0.0 --port 8080

# or build container
podman build -t mtcars-fastapi .

# run container
podman run --rm -p 8080:8080 mtcars-fastapi
```
