"""
main.py 

FastAPI app for serving a linear regression model trained on mtcars.csv.
Implements logging, rate limiting, validation, error handling, and model readiness checks.

Endpoints:
1. GET /health
- returns a success response if the API is running
- no authentication required
2. GET /ready
- returns a success response if the model is loaded and ready
- returns a non-200 response if the model is missing or unavailable
3. POST /predict
- accepts input values for the predictor variables used by your model
- validates input with Pydantic
- returns the predicted mpg

Predictors: weight (wt), quarter-mile time (qsec), and transmission type (am)
Response: mpg 
"""
# -- Setup --

import logging
import joblib

from pathlib import Path
from typing import Literal
from contextlib import asynccontextmanager

import pandas as pd

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Define model path
MODEL_PATH = Path('models/model.pkl')


# Store models and its resources 
# -> Allows efficient cleanup later
models = {}

# Load model 
# -> Without startup loading model gets reloaded from disk every time someone calls /predict -> inefficient 
# -> Reference: https://fastapi.tiangolo.com/advanced/events/#lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Load trained model before handling prediction requests.
    """
    # Load model
    try:
        models['model'] = joblib.load(MODEL_PATH)
        logger.info(f'Model loaded from {MODEL_PATH}.')
    except FileNotFoundError:
        models['model'] = None
        logger.error(f'Model file not found at {MODEL_PATH}.')
    except Exception as e:
        models['model'] = None
        logger.error(f'Error loading model: {e}.')

    # Yield: keep app running and serving requests 
    # -> Yield separates startup code from shutdown
    yield

    # Clear model when app shuts down
    models.clear()
    logger.info('Model resources cleared.')


# Create app
app = FastAPI(
    title="Car MPG Prediction API",
    description="Predicts mpg using a linear regression model trained on mtcars.csv.",
    version="1.0.0",
    lifespan=lifespan,
)


# Setup rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

# Return a proper rate-limit error response 
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add middleware 
# -> code that runs around each request 
# -> track requests, attach rate-limit behavior consistently, include info about limit
app.add_middleware(SlowAPIMiddleware)


# -- Pydantic models --

class PredictionRequest(BaseModel):
    """
    Request for mpg prediction.

    Predictors must match the variables and order used during training:
    wt, qsec, am
    """
    # Define required fields 
    # -> Use Field for extra validation and documentation metadata 
    # --> ... means required 
    # --> gt=0 means greater than 0 -> stricter validation
    # --> description appears in the automatic FastAPI docs -> extra documentation
    wt: float = Field(..., gt=0, description='Weight in 1000 lbs')
    qsec: float = Field(..., gt=0, description='1/4 mile time')
    am: Literal[0, 1] = Field(..., description='Transmission: 0 = automatic, 1 = manual')

# Pydantic response model gives cleaner API docs and an explicit output format
class PredictionResponse(BaseModel):
    """
    Response for mpg prediction.
    """
    predicted_mpg: float
    model_version: str


# -- Endpoints --

# GET is usually for asking for info; usually do not send a JSON body
@app.get("/health")
@limiter.limit("100/minute") # higher limit bc cheap
def health(request: Request):
    """
    Health check to check API is running.
    """
    return {"status": "ok"}


@app.get("/ready")
@limiter.limit("100/minute") # higher limit bc cheap
def ready(request: Request):
    """
    Readiness check to confirm the model is loaded and usable.
    """
    model = models.get('model')

    if model is None:
        raise HTTPException(status_code=503,detail='Model is not loaded.')

    try:
        # Test prediction using first row in data
        test_features = pd.DataFrame([{ # df to remove sklearn warning that input does not include original feature names
            "wt": 2.62,
            "qsec": 16.46,
            "am": 1,
        }])
        _ = model.predict(test_features)

        return {"status": "ready"}
    except Exception as e:
        raise HTTPException(status_code=503,detail=f'Model is loaded but prediction failed: {e}')


# POST is usually for sending data to the API so it can do something with it
@app.post("/predict", response_model=PredictionResponse)
@limiter.limit("30/minute") # lower limit bc model prediction is more expensive
def predict(request: Request, prediction_request: PredictionRequest):
    """
    Predict mpg from weight (wt), quarter-mile time (qsec), and transmission type (am).
    """
    model = models.get('model')

    if model is None:
        raise HTTPException(status_code=503,detail="Model is not loaded. Prediction is unavailable.")

    features = pd.DataFrame([{ # df to remove sklearn warning that input does not include original feature names
        "wt": prediction_request.wt,
        "qsec": prediction_request.qsec,
        "am": prediction_request.am
    }])

    logger.info(
        f'Prediction request: wt={prediction_request.wt}, '
        f'qsec={prediction_request.qsec}, am={prediction_request.am}'
    ) # cleaner log (to not print a mini table in the logs)

    try:
        pred = model.predict(features)[0]
        logger.info('Prediction completed.')

        return PredictionResponse(
            predicted_mpg=round(float(pred), 1),
            model_version='v1.0'
        )

    except Exception as e:
        logger.error(f'Prediction failed: {e}')
        raise HTTPException(status_code=500,detail=f'Prediction failed: {e}')