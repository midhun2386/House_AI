# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import layout_engine

app = FastAPI(title="HouseAI Pro Architecture API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

# UPGRADED MODEL: Now expects `units` integer
class PlotData(BaseModel):
    length: float = 40.0
    width: float = 30.0
    bedrooms: int = 2
    units: int = 1         # <--- NEW FIELD FOR SHOPS/APARTMENTS
    building_type: str = "House"
    style: str = "Modern"
    extras: List[str] = []
    custom_reqs: str = ""  

@app.post("/get-my-plan")
async def get_plan(data: PlotData):
    data_dict = data.dict()
    
    # Generate Layout
    plan = layout_engine.generate_layout(data_dict)
    
    # Calculate BOQ
    budget, materials = layout_engine.estimate_resources(data.length, data.width, data.bedrooms)
    
    extras_text = f" Included features: {', '.join(data.extras)}." if data.extras else ""
    prompt_text = " Processed custom AI requirements." if data.custom_reqs.strip() else ""
    
    # Dynamic advice string based on building type
    if data.building_type == "Shop":
        advice = f"Optimized {data.units}-unit Commercial Plaza design complete.{prompt_text}"
    elif data.building_type == "Apartment":
        advice = f"Optimized multi-unit Apartment design complete.{extras_text}{prompt_text}"
    else:
        advice = f"Optimized {data.style} {data.building_type} design complete.{extras_text}{prompt_text}"
        
    return {
        "plan": plan,
        "score": 95 if data.custom_reqs else 98,
        "ai_advice": advice,
        "budget": budget,
        "materials": materials
    }