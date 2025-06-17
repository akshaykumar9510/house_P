from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import os
import sys
import traceback
import importlib
import time

# Define the base directory
BASE_DIR = Path(__file__).resolve().parent
print(f"Base directory: {BASE_DIR}")

# Create app
app = FastAPI(title="Debug App")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Display information about Python environment
print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")
print(f"Current working directory: {os.getcwd()}")

# Check if frontend directory exists
frontend_dir = BASE_DIR / "frontend"
print(f"Frontend directory: {frontend_dir}")
print(f"Frontend directory exists: {os.path.isdir(frontend_dir)}")

if os.path.isdir(frontend_dir):
    print(f"Frontend directory contents: {os.listdir(frontend_dir)}")

# Mount the static files
try:
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")
    print(f"Successfully mounted static files from {frontend_dir}")
except Exception as e:
    print(f"Error mounting static files: {str(e)}")
    print(traceback.format_exc())

@app.get("/", response_class=HTMLResponse)
async def read_root():
    try:
        # Read the HTML file
        html_path = frontend_dir / "index.html"
        print(f"Trying to read HTML file from: {html_path}")
        print(f"HTML file exists: {os.path.isfile(html_path)}")
        
        with open(html_path, "r", encoding="utf-8") as file:
            html_content = file.read()
            print(f"Successfully read HTML file, size: {len(html_content)} bytes")
        return html_content
    except Exception as e:
        error_msg = f"Error reading HTML file: {str(e)}"
        print(error_msg)
        print(traceback.format_exc())
        return f"<html><body><h1>Error</h1><p>{error_msg}</p></body></html>"

@app.get("/test")
def test():
    return {"status": "ok", "timestamp": time.time()}

@app.get("/diagnose")
async def diagnose():
    """Comprehensive diagnostic endpoint to help identify issues with the app"""
    result = {
        "environment": {
            "python_version": sys.version,
            "current_directory": os.getcwd(),
            "base_directory": str(BASE_DIR)
        },
        "files": {
            "frontend_directory_exists": os.path.isdir(frontend_dir)
        },
        "model": {}
    }
    
    # Check frontend files
    if result["files"]["frontend_directory_exists"]:
        result["files"]["frontend_files"] = os.listdir(frontend_dir)
        
        # Check each expected frontend file
        for filename in ["index.html", "script.js", "style.css"]:
            file_path = frontend_dir / filename
            result["files"][f"{filename}_exists"] = os.path.isfile(file_path)
            
            if os.path.isfile(file_path):
                try:
                    with open(file_path, "r", encoding="utf-8") as file:
                        content = file.read()
                        result["files"][f"{filename}_size"] = len(content)
                        result["files"][f"{filename}_readable"] = True
                except Exception as e:
                    result["files"][f"{filename}_readable"] = False
                    result["files"][f"{filename}_error"] = str(e)
    
    # Check model file
    model_path = BASE_DIR / "model.pkl"
    result["model"]["exists"] = os.path.isfile(model_path)
    
    if result["model"]["exists"]:
        result["model"]["size"] = os.path.getsize(model_path)
        
        # Try to load the model
        try:
            import joblib
            start_time = time.time()
            model = joblib.load(model_path)
            load_time = time.time() - start_time
            
            result["model"]["load_success"] = True
            result["model"]["load_time"] = load_time
            result["model"]["type"] = str(type(model))
            
            # Try basic prediction if it's a scikit-learn model
            try:
                import numpy as np
                test_input = np.array([[8.3252, 41, 6.98, 1.02, 322, 2.55, 37.88, -122.23]])
                prediction = model.predict(test_input)
                result["model"]["prediction_test"] = "success"
                result["model"]["prediction_value"] = float(prediction[0])
            except Exception as e:
                result["model"]["prediction_test"] = "failed"
                result["model"]["prediction_error"] = str(e)
        
        except Exception as e:
            result["model"]["load_success"] = False
            result["model"]["load_error"] = str(e)
            result["model"]["traceback"] = traceback.format_exc()
    
    # Check for libraries
    libraries = ["fastapi", "uvicorn", "joblib", "numpy", "sklearn"]
    result["libraries"] = {}
    
    for lib in libraries:
        try:
            module = importlib.import_module(lib)
            result["libraries"][lib] = {"installed": True}
            
            # Try to get version if available
            try:
                version = module.__version__
                result["libraries"][lib]["version"] = version
            except AttributeError:
                result["libraries"][lib]["version"] = "unknown"
                
        except ImportError:
            result["libraries"][lib] = {"installed": False}
    
    return result
