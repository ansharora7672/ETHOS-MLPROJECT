from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import pandas as pd
import joblib
import io

# 1. Store model in memory
ml_models = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager to load the model exactly once upon startup.
    This prevents memory leaks and ensures lighting-fast inference.
    """
    try:
        # Load from the same folder as main.py
        ml_models["rf_model"] = joblib.load("random_forest_model.pkl")
        print("Random Forest Model loaded successfully!")
    except Exception as e:
        print(f"Failed to load model: {e}")
        
    yield 
    ml_models.clear()

app = FastAPI(
    title="Exoplanet (Talent) Predictor API",
    description="Predicts if a candidate is CONFIRMED (1) or a FALSE POSITIVE (0).",
    lifespan=lifespan
)

# 2. Define the Pydantic Schema
# Note: Even though you stated they are integers, it is safer to use `float` in production ML pipelines. 
# A `float` in Pydantic will happily accept an integer (treating 1 as 1.0), but if you use `int`, 
# it might crash if the frontend accidentally sends `1.5`.
class KeplerData(BaseModel):
    koi_period: float
    koi_impact: float
    koi_duration: float
    koi_depth: float
    koi_ror: float
    koi_srho: float
    koi_prad: float
    koi_sma: float
    koi_incl: float
    koi_teq: float
    koi_insol: float
    koi_dor: float
    koi_max_sngle_ev: float
    koi_max_mult_ev: float
    koi_model_snr: float
    koi_count: float
    koi_num_transits: float
    koi_bin_oedp_sig: float
    koi_steff: float
    koi_slogg: float
    koi_smet: float
    koi_srad: float
    koi_smass: float
    koi_kepmag: float
    koi_fwm_stat_sig: float

# Helper function to map 1 / 0 back to readable strings
def format_prediction(prediction_int):
    return "CONFIRMED" if prediction_int == 1 else "FALSE POSITIVE"

# 3. Endpoint for single Web Requests (JSON)
@app.post("/predict")
async def predict_single(data: KeplerData):
    """
    Takes a single row of JSON data and returns an individual prediction.
    """
    model = ml_models.get("rf_model")
    if not model:
        raise HTTPException(status_code=503, detail="Model unavailable")
    
    # We convert the Pydantic data strictly into a Pandas DataFrame.
    # Why? Because Random Forest was likely trained on a DataFrame and doing this 
    # ensures the column order perfectly matches what the model expects.
    input_df = pd.DataFrame([data.model_dump()])
    
    try:
        # returns an array like [1] or [0]
        prediction_val = model.predict(input_df)[0]
        
        return {
            "prediction": format_prediction(prediction_val),
            "raw_output": int(prediction_val)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 4. Endpoint for Bulk CSV Uploads
@app.post("/predict/csv")
async def predict_csv(file: UploadFile = File(...)):
    """
    Accepts a .csv file upload. Uses the model to predict ALL rows 
    and returns a JSON list of predictions.
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Must be a .csv file!")
        
    model = ml_models.get("rf_model")
    if not model:
        raise HTTPException(status_code=503, detail="Model unavailable")

    try:
        # Read the uploaded file directly into Pandas memory (without saving to hard drive!)
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode("utf-8")))
        
        # Ensure the uploaded CSV has exactly the required columns
        required_cols = list(KeplerData.model_fields.keys())
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            raise HTTPException(
                status_code=400, 
                detail=f"CSV is missing required columns: {missing_cols}"
            )
            
        # Reorder columns to guarantee they match the exact expected order
        df = df[required_cols]

        # Make predictions for every single row instantly
        predictions = model.predict(df)
        
        # Attach the string names back for the user
        results = [{"row_index": i, "result": format_prediction(pred)} for i, pred in enumerate(predictions)]
        
        return {"total_processed": len(df), "predictions": results}

    except Exception as e:
         raise HTTPException(status_code=500, detail=str(e))
