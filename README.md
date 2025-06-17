# House Price Prediction App

A simple machine learning application that predicts house prices based on California housing dataset features.

## Features

- Predicts house prices based on 8 input features
- Simple and responsive user interface
- FastAPI backend with integrated frontend
- Ready for deployment on Render

## Local Development

1. Install requirements:
```bash
pip install -r requirements.txt
```

2. Run the application locally:
```bash
uvicorn main:app --reload
```

3. Open your browser and navigate to `http://localhost:8000`

## Deployment on Render

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Use the following settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Add environment variable:
   - `PYTHON_VERSION` = `3.10` (or your preferred version)

## Project Structure

- `main.py` - FastAPI backend that serves API and frontend
- `model.pkl` - Trained machine learning model
- `train_model.py` - Script to train the model
- `frontend/` - Contains HTML, CSS, and JavaScript files
- `requirements.txt` - Required Python packages