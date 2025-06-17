from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
import joblib
import numpy as np
from pathlib import Path
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the base directory
BASE_DIR = Path(__file__).resolve().parent
logger.info(f"Base directory: {BASE_DIR}")

# Verify frontend directory exists
FRONTEND_DIR = BASE_DIR / "frontend"
INDEX_PATH = FRONTEND_DIR / "index.html"
logger.info(f"Frontend directory exists: {FRONTEND_DIR.exists()}")
logger.info(f"Index path exists: {INDEX_PATH.exists()}")

# Load model
try:
    model = joblib.load(BASE_DIR / "model.pkl")
    logger.info(f"Model loaded successfully: {type(model)}")
except Exception as e:
    logger.error(f"Error loading model: {str(e)}")
    raise

# Create app
app = FastAPI(title="🏠 House Price Prediction API")

# Add CORS middleware
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the static files
try:
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")
    logger.info("Static files mounted successfully")
except Exception as e:
    logger.error(f"Error mounting static files: {str(e)}")
    raise

# Input model using Pydantic
class HouseFeatures(BaseModel):
    MedInc: float
    HouseAge: float
    AveRooms: float
    AveBedrms: float
    Population: float
    AveOccup: float
    Latitude: float
    Longitude: float

@app.get("/")
async def read_root():
    # Serve the HTML file using FileResponse
    index_path = INDEX_PATH
    logger.info(f"Serving index.html from: {index_path}")
    
    if not index_path.exists():
        logger.error("❌ index.html not found!")
        return {"error": "index.html not found"}
    
    return FileResponse(str(index_path))

@app.post("/predict")
def predict_price(features: HouseFeatures):
    # Convert input to 2D array
    input_data = np.array([[features.MedInc, features.HouseAge, features.AveRooms,
                            features.AveBedrms, features.Population,
                            features.AveOccup, features.Latitude, features.Longitude]])
    
    # Predict
    prediction = model.predict(input_data)
    return {"predicted_price": round(float(prediction[0]), 2)}
