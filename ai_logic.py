# ai_logic.py
from layout_engine import generate_layout

def evaluate_feasibility(data):
    """
    Checks if the user's request is physically possible.
    Calculates based on minimum functional space for an Indian household.
    """
    length = data.get('length', 0.0)
    width = data.get('width', 0.0)
    bedrooms = data.get('bedrooms', 1)
    
    total_area = length * width
    # Realistic minimums: 1BHK ~ 350-400 sqft. Each extra bed ~ 150-200 sqft.
    min_required_area = 350 + (max(0, bedrooms - 1) * 200)
    
    if bedrooms > 5:
        return {
            "status": "warning",
            "message": "High density request detected. Designing a Multi-Floor plan to ensure structural stability and ventilation."
        }

    if total_area < min_required_area:
        return {
            "status": "warning",
            "message": f"Plot area ({int(total_area)} sqft) is extremely compact for {bedrooms} bedrooms. "
                       f"Switching to a vertical Duplex optimization for better ergonomics."
        }
    return {
        "status": "ok",
        "message": "Plot size is adequate for a spacious architecture layout."
    }


def evolve_layout(data):
    """
    Decides the layout type and provides a professional rating.
    """
    # 1. Feasibility Analysis
    feasibility = evaluate_feasibility(data)
    
    # 2. Layout Generation 
    # The engine now handles floor stacking logic based on these parameters
    final_plan = generate_layout(data)
    
    # 3. Startup-Style Scoring Logic
    total_area = data['length'] * data['width']
    num_elements = len(final_plan['rooms'])
    avg_space_per_room = total_area / num_elements
    
    # Scoring out of 100
    ai_score = 100
    if avg_space_per_room < 120: ai_score -= 30  # Points off for being cramped
    if data['length'] / data['width'] > 2.5: ai_score -= 15 # Points off for narrow plots
    
    final_plan['ai_score'] = max(ai_score, 15)
    
    return {
        "plan": final_plan,
        "analysis_msg": feasibility['message'],
        "efficiency_tag": "High Efficiency" if ai_score > 75 else "Compact Use"
    }