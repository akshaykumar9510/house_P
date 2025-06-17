from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel
import joblib
import numpy as np
from pathlib import Path
import os
import sys
import traceback

print("Starting application...")

# Define the base directory
BASE_DIR = Path(__file__).resolve().parent
print(f"Base directory: {BASE_DIR}")

try:
    # Load model with error handling
    model_path = BASE_DIR / "model.pkl"
    print(f"Looking for model at: {model_path}")
    print(f"Model exists: {os.path.isfile(model_path)}")
    
    if os.path.isfile(model_path):
        print(f"Model size: {os.path.getsize(model_path)} bytes")
        try:
            model = joblib.load(model_path)
            print(f"Model loaded successfully, type: {type(model)}")
        except Exception as e:
            print(f"Error loading model: {str(e)}")
            print(traceback.format_exc())            # Create a simple model for testing
            from sklearn.linear_model import LinearRegression
            model = LinearRegression()
            model.fit([[0, 0, 0, 0, 0]], [0])
            print("Created a simple model for testing")
    else:
        print("Model file not found, creating a simple test model")
        # Create a simple model for testing
        from sklearn.linear_model import LinearRegression
        model = LinearRegression()
        model.fit([[0, 0, 0, 0, 0]], [0])
        print("Created a simple model for testing")
except Exception as e:
    print(f"Critical error in model loading: {str(e)}")
    print(traceback.format_exc())
    sys.exit(1)

try:
    # Create app
    app = FastAPI(title="🏠 House Price Prediction API")
    print("Created FastAPI app")

    # Add CORS middleware
    from fastapi.middleware.cors import CORSMiddleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    print("Added CORS middleware")

    # Check frontend directory
    frontend_dir = BASE_DIR / "frontend"
    print(f"Frontend directory: {frontend_dir}")
    print(f"Frontend directory exists: {os.path.isdir(frontend_dir)}")
    
    if os.path.isdir(frontend_dir):
        print(f"Frontend contents: {os.listdir(frontend_dir)}")

    # Mount the static files with error handling
    try:
        app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")
        print("Static files mounted successfully")
    except Exception as e:
        print(f"Error mounting static files: {str(e)}")
        print(traceback.format_exc())    # Input model using Pydantic
    class HouseFeatures(BaseModel):
        MedInc: float
        HouseAge: float
        AveRooms: float
        AveBedrms: float
        Population: float

    @app.get("/", response_class=HTMLResponse)
    async def read_root():
        try:
            # Read the HTML file
            html_path = frontend_dir / "index.html"
            print(f"Reading HTML from: {html_path}")
            print(f"HTML file exists: {os.path.isfile(html_path)}")
            
            with open(html_path, "r", encoding="utf-8") as file:
                html_content = file.read()
                print(f"HTML file read successfully, size: {len(html_content)} bytes")
            return html_content
        except Exception as e:
            error_msg = f"Error reading HTML file: {str(e)}"
            print(error_msg)
            print(traceback.format_exc())
            return f"<html><body><h1>Error</h1><p>{error_msg}</p></body></html>"

    @app.get("/health")
    def health_check():
        """Health check endpoint to verify the API is running"""
        return {"status": "healthy", "model_type": str(type(model))}    @app.post("/predict")
    def predict_price(features: HouseFeatures):
        try:
            # Convert input to 2D array
            input_data = np.array([[
                features.MedInc, 
                features.HouseAge, 
                features.AveRooms,
                features.AveBedrms, 
                features.Population
            ]])
            
            # Predict
            prediction = model.predict(input_data)
            return {"predicted_price": round(float(prediction[0]), 2)}
        except Exception as e:
            print(f"Error making prediction: {str(e)}")
            print(traceback.format_exc())
            raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

except Exception as e:
    print(f"Critical error in setup: {str(e)}")
    print(traceback.format_exc())
    sys.exit(1)
