# MTCARS FastAPI Deployment

Amber Jiang

## Overview

This project trains a linear regression model on the `mtcars.csv` dataset with `mpg` as the response variable and `wt`, `qsec`, and `am` as predictors. The trained model is served through a FastAPI application, containerized with Podman, pushed to Google Artifact Registry, and deployed to Google Cloud Run.

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

### Required Dataset

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

## Local Workflow

```bash
# create virtual environment
uv venv
source .venv/bin/activate

# install dependencies
uv pip install -r requirements.txt

# train your model
uv run python scripts/train_model.py

# run locally
uvicorn app.main:app --host 0.0.0.0 --port 8080

# run tests
pytest tests/test_api.py -v

# or build container
podman build -t mtcars-fastapi .

# run container
podman run --rm -p 8080:8080 mtcars-fastapi
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
- Trained model is saved to: `models/model.pkl`.

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

When the API is running locally, interactive FastAPI documentation is available at:

```text
http://localhost:8080/docs
```

### Input Validation and Error Handling

API includes:

- Pydantic request validation
- helpful errors for invalid input
- graceful handling if the model cannot be loaded

Validation rules:

- `wt` must be greater than `0`
- `qsec` must be greater than `0`
- `am` must be either `0` or `1`

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

Automated API tests are located in `tests/test_api.py`.

The tests check:

- `/health`
- `/ready`
- one successful `/predict` request
- invalid `wt`
- invalid `qsec`
- invalid `am`
- missing required field behavior

Run tests with:

```bash
pytest tests/test_api.py -v
```

Expected result:

```text
7 passed
```

## Container required files

### `Dockerfile`

Dockerfile:

- uses a Python 3.11-slim base image
- copies the application code and model artifact
- installs dependencies
- exposes port `8080`
- starts the FastAPI app when the container runs

### `.dockerignore`

Exclude unnecessary files:

- .git
- .venv
- \_\_pycache\_\_/
- \*.pyc
- scripts/
- tests/
- .python-version
- uv.lock
- pyproject.toml

## Run Locally with Podman

Project runs locally in a container with Podman.

Build the container image:

```bash
podman build -t mtcars-fastapi .
```

Run the container locally on port `8080`:

```bash
podman run --rm -p 8080:8080 mtcars-fastapi
```

The API should be available at:

```text
http://localhost:8080
```

Test the containerized API:

```bash
curl http://localhost:8080/health
curl http://localhost:8080/ready
curl -X POST "http://localhost:8080/predict" \
  -H "Content-Type: application/json" \
  -d '{"wt": 2.62, "qsec": 16.46, "am": 1}'
```

## Deployment

Deploy containerized API to Google Cloud Run.

### Set deployment variables

```bash
PROJECT_ID="mtcars-fastapi"
REGION="us-west2"
REPO_NAME="mtcars-fastapi-api"
IMAGE_NAME="mtcars-fastapi"
```

These values are specific to this deployment. If using a different Google Cloud project, replace `PROJECT_ID`, `REGION`, and `REPO_NAME` accordingly.

Confirm the variables:

```bash
echo $PROJECT_ID
echo $REGION
echo $REPO_NAME
echo $IMAGE_NAME
```

### Authenticate and set project

```bash
gcloud auth login
gcloud config set project $PROJECT_ID
```

### Create Artifact Registry repository

```bash
gcloud artifacts repositories create $REPO_NAME \
  --repository-format=docker \
  --location=$REGION
```

### Tag the local Podman image

```bash
podman tag mtcars-fastapi \
  $REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/$IMAGE_NAME:latest
```

### Log in to Artifact Registry with Podman

If Podman has issues using Docker credential helpers, use a Podman auth file:

```bash
mv ~/.docker/config.json ~/.docker/config.json.bak
mkdir -p ~/.config/containers
```

```bash
gcloud auth print-access-token | podman login \
  -u oauth2accesstoken \
  --password-stdin \
  --authfile ~/.config/containers/auth.json \
  https://$REGION-docker.pkg.dev
```

### Push the image

```bash
podman push \
  --authfile ~/.config/containers/auth.json \
  $REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/$IMAGE_NAME:latest
```

### Deploy to Cloud Run

```bash
gcloud run deploy mtcars-fastapi \
  --image $REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/$IMAGE_NAME:latest \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --port 8080
```

### Deployed API URL

```text
https://mtcars-fastapi-975427797322.us-west2.run.app/
```

Test the deployed API:

```bash
curl https://mtcars-fastapi-975427797322.us-west2.run.app/health
```

```bash
curl https://mtcars-fastapi-975427797322.us-west2.run.app/ready
```

```bash
curl -X POST "https://mtcars-fastapi-975427797322.us-west2.run.app/predict" \
  -H "Content-Type: application/json" \
  -d '{"wt": 2.62, "qsec": 16.46, "am": 1}'
```

## Reproducibility and Code Quality

A user can:

- clone the repo
- install dependencies
- rebuild the model
- run the API locally
- call the API successfully
- understand what each major file does

Code quality practices:

- clear file organization
- meaningful variable names
- type hints where appropriate
- readable, reproducible code
- secrets kept out of version control

## Production-Oriented Features

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
- [✔] API deployed to Cloud Run
- [✔] README is complete
- [✔] at least one automated test is included
- [✔] repo is reproducible for another user
