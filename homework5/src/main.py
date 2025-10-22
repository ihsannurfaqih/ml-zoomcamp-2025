import pickle
from typing import Literal
from pydantic import BaseModel, Field


from fastapi import FastAPI
import uvicorn

class Customer(BaseModel):
    lead_source: Literal[
        "ads", "direct_traffic", "email_marketing", "organic_search",
        "referral_traffic", "social_media"
    ] = Field(..., example="organic_search")
    number_of_courses_viewed: int = Field(..., example=4)
    annual_income: float = Field(..., example=80304.0)

class PredictResponse(BaseModel):
    churn_probability: float
    churn: bool


app = FastAPI(title="customer-churn-prediction")

with open('../model/pipeline_v1.bin', 'rb') as f_in:
    pipeline = pickle.load(f_in)


def predict_single(customer):
    result = pipeline.predict_proba(customer)[0, 1]
    return float(result)


@app.post("/predict")
def predict(customer: Customer) -> PredictResponse:
    prob = predict_single(customer.model_dump())

    return PredictResponse(
        churn_probability=prob,
        churn=bool(prob >= 0.5)
    )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9696)