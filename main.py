# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from ai_logic import evolve_layout

app = FastAPI()

# Allow the browser to talk to the server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

class PlanRequest(BaseModel):
    length: float = Field(..., gt=0)
    width: float = Field(..., gt=0)
    bedrooms: int = Field(default=1, ge=0)

@app.post("/get-my-plan")
async def create_plan(request: PlanRequest):
    # Convert Pydantic model to dict for legacy logic support
    data = request.model_dump()
    
    # Pass the data to your Smart AI Logic
    result = evolve_layout(data)
    
    # Calculate Budget
    total_area = data['length'] * data['width']
    # Dynamic rate based on complexity (more bedrooms = slightly more expensive per sqft)
    base_rate = 1800
    complexity_markup = request.bedrooms * 50 
    budget = total_area * (base_rate + complexity_markup)
    
    # Send everything back to the browser
    return {
        "status": "success",
        "plan": result['plan'],
        "ai_advice": result['analysis_msg'],
        "score": result['plan'].get('ai_score', 100),
        "budget": f"₹{int(budget):,}",
        "materials": f"Cement: {int(total_area * 0.45)} bags, Steel: {int(total_area * 4.2)} kg, Sand: {int(total_area * 1.8)} cu.ft"
    }