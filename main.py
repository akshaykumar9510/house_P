from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import numpy as np

# Load model
model = joblib.load("model.pkl")

# Create app
app = FastAPI(title="🏠 House Price Prediction API")

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

@app.post("/predict")
def predict_price(features: HouseFeatures):
    # Convert input to 2D array
    input_data = np.array([[features.MedInc, features.HouseAge, features.AveRooms,
                            features.AveBedrms, features.Population,
                            features.AveOccup, features.Latitude, features.Longitude]])
    
    # Predict
    prediction = model.predict(input_data)
    return {"predicted_price": round(float(prediction[0]), 2)}
