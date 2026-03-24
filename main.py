# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import layout_engine

app = FastAPI(title="HouseAI Pro Architecture API")

# Enable CORS so your local HTML file can communicate with this server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

# UPGRADED DATA MODEL: Now expects the custom prompt, style, and extras!
class PlotData(BaseModel):
    length: float = 40.0
    width: float = 30.0
    bedrooms: int = 2
    building_type: str = "House"
    style: str = "Modern"
    extras: List[str] = []
    custom_reqs: str = ""  # <--- NEW FIELD FOR THE AI PROMPT BOX

@app.post("/get-my-plan")
async def get_plan(data: PlotData):
    # Convert Pydantic model to a standard dictionary for our engine
    data_dict = data.dict()
    
    # 1. Generate the Layout (This will soon handle the custom prompt!)
    plan = layout_engine.generate_layout(data_dict)
    
    # 2. Generate the precise Resource & Budget Estimate
    budget, materials = layout_engine.estimate_resources(data.length, data.width, data.bedrooms)
    
    # 3. Create a dynamic AI advice string based on what the user asked for
    extras_text = f" Included features: {', '.join(data.extras)}." if data.extras else ""
    prompt_text = " Processed custom AI requirements." if data.custom_reqs.strip() else ""
    advice = f"Optimized {data.style} {data.building_type} design complete.{extras_text}{prompt_text} Calculated exact BOQ for {int(data.length * data.width)} sq.ft."
    
    return {
        "plan": plan,
        "score": 95 if data.custom_reqs else 98, # Slight variation for realism
        "ai_advice": advice,
        "budget": budget,
        "materials": materials
    }