from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
import sys
import os
import io

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from models.predictor import FatigueClassifier
from models.human_predictor import HumanFatigueClassifier
from services.influxdb_service import InfluxDBService

app = FastAPI(
    title="Fatigue Detection Service",
    description="ML service for human fatigue detection (image + tabular data)",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

image_classifier = FatigueClassifier()
tabular_classifier = HumanFatigueClassifier()
influx_service = InfluxDBService()


class TabularFeatures(BaseModel):
    Hours_Awake: float = Field(..., ge=0, le=48)
    Decisions_Made: float = Field(..., ge=0)
    Task_Switches: float = Field(..., ge=0)
    Avg_Decision_Time_sec: float = Field(..., ge=0)
    Sleep_Hours_Last_Night: float = Field(..., ge=0, le=24)
    Caffeine_Intake_Cups: float = Field(..., ge=0)
    Stress_Level_1_10: float = Field(..., ge=1, le=10)
    Error_Rate: float = Field(..., ge=0, le=1)
    Cognitive_Load_Score: float = Field(..., ge=0, le=1)


class ImagePredictionResponse(BaseModel):
    prediction: str
    confidence: float
    class_id: int


class TabularPredictionResponse(BaseModel):
    prediction: str
    probabilities: dict
    confidence: float


@app.on_event("startup")
async def startup_event():
    try:
        image_classifier.load()
    except Exception as e:
        print(f"Warning: Could not load image model: {e}")
    
    try:
        tabular_classifier.load()
    except Exception as e:
        print(f"Warning: Could not load tabular model: {e}")
    
    try:
        influx_service.connect()
    except Exception as e:
        print(f"Warning: Could not connect to InfluxDB: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    influx_service.disconnect()


@app.get("/")
async def root():
    return {
        "message": "Fatigue Detection Service",
        "version": "2.0.0",
        "models": ["image_classification", "tabular_classification"]
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "image_model_loaded": image_classifier.model is not None,
        "tabular_model_loaded": tabular_classifier.model is not None
    }


@app.post("/predict/image", response_model=ImagePredictionResponse)
async def predict_from_image(file: UploadFile = File(...)):
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    try:
        contents = await file.read()
        predicted, confidence = image_classifier.predict_image_from_bytes(io.BytesIO(contents))
        
        label = "Fatigue" if predicted == 1 else "NonFatigue"
        
        return ImagePredictionResponse(
            prediction=label,
            confidence=round(confidence, 4),
            class_id=predicted
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/predict/tabular", response_model=TabularPredictionResponse)
async def predict_from_tabular(features: TabularFeatures):
    try:
        feature_dict = features.model_dump()
        label, probabilities = tabular_classifier.predict(feature_dict)
        
        class_labels = tabular_classifier.label_encoder.classes_
        prob_dict = {class_labels[i]: round(probabilities[i], 4) for i in range(len(class_labels))}
        
        return TabularPredictionResponse(
            prediction=label,
            probabilities=prob_dict,
            confidence=max(probabilities)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/predict/batch/tabular")
async def predict_batch_tabular(samples: List[TabularFeatures]):
    try:
        features_list = [sample.model_dump() for sample in samples]
        results = tabular_classifier.predict_batch(features_list)
        
        class_labels = tabular_classifier.label_encoder.classes_
        response = []
        for result in results:
            prob_dict = {class_labels[i]: round(result["probabilities"][i], 4) for i in range(len(class_labels))}
            response.append({
                "prediction": result["label"],
                "probabilities": prob_dict,
                "confidence": round(max(result["probabilities"]), 4)
            })
        
        return {"results": response, "total": len(samples)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
