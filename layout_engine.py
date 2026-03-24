# layout_engine.py
import math
from typing import Any, Dict, List

def calculate_zones(length: float):
    """ Dynamically scales the front, middle, and back zones so they never overlap. """
    front_h = max(12.0, length * 0.35)
    back_h = max(10.0, length * 0.40)
    mid_h = length - front_h - back_h
    
    if mid_h < 8.0:
        mid_h = 8.0
        remaining = length - mid_h
        front_h = remaining * 0.45
        back_h = remaining * 0.55
        
    return front_h, mid_h, back_h

def add_architectural_details(rooms, plot_w, plot_h):
    """ Scans the generated rooms and mathematically places doors, windows, and gates. """
    stair_w = min(7.0, plot_w * 0.3)
    
    for r in rooms:
        features = r.get("features", []) 
        name = r["name"]
        
        # 1. MAIN GATE & OPENINGS
        if r.get("is_open"):
            if "PARKING" in name:
                features.append({"type": "gate", "wall": "top", "pos": r["width"]/2, "size": 10.0})
            r["features"] = features
            continue

        is_bath = "BATH" in name
        win_size = 2.0 if is_bath else 4.0 
        
        # 2. WINDOWS
        if abs(r["x"]) < 0.1: 
            features.append({"type": "window", "wall": "left", "pos": r["height"]/2, "size": win_size})
        if abs(r["x"] + r["width"] - plot_w) < 0.1: 
            features.append({"type": "window", "wall": "right", "pos": r["height"]/2, "size": win_size})
        if abs(r["y"]) < 0.1: 
            features.append({"type": "window", "wall": "top", "pos": r["width"]/2, "size": win_size})
        if abs(r["y"] + r["height"] - plot_h) < 0.1: 
            features.append({"type": "window", "wall": "bottom", "pos": r["width"]/2, "size": win_size})
        
        # 3. DOORS
        has_door = any(f["type"] in ["door", "main_door", "arch"] for f in features)
        
        if not has_door:
            if "LIVING" in name:
                features.append({"type": "main_door", "wall": "left", "pos": r["height"] - 3.0, "size": 3.5})
            elif "DINING HALL" in name:
                features.append({"type": "arch", "wall": "top", "pos": r["width"]/2, "size": 6.0})
            elif "KITCHEN" in name:
                if "DINING" in name:
                    features.append({"type": "arch", "wall": "top", "pos": r["width"]/2, "size": 6.0})
                else:
                    features.append({"type": "arch", "wall": "right", "pos": r["height"]/2, "size": 5.0})
            elif "COMMON BATH" in name:
                features.append({"type": "door", "wall": "left", "pos": r["height"] - 2.5, "size": 2.5})
            elif any(k in name for k in ["LOUNGE", "PASSAGE", "STAIRCASE"]):
                pass 
            else:
                door_size = 2.5 if is_bath else 3.0
                
                if r["y"] < 0.1 and "MASTER" in name:
                    features.append({"type": "door", "wall": "bottom", "pos": 3.0, "size": door_size})
                    features.append({"type": "door", "wall": "left", "pos": 3.0, "size": door_size})
                elif r["y"] > plot_h * 0.5 and "BED" in name:
                    if "GUEST" in name:
                        safe_pos = stair_w - r["x"] + 2.0
                        features.append({"type": "door", "wall": "top", "pos": safe_pos, "size": door_size})
                    else:
                        features.append({"type": "door", "wall": "top", "pos": r["width"]/2, "size": door_size})
                else:
                    features.append({"type": "door", "wall": "top", "pos": 2.0, "size": door_size})
            
        r["features"] = features
    return rooms

def pack_bedrooms(start_x, start_y, total_w, total_h, num_beds, floor_level, name_prefix="BED"):
    """ Advanced Space Partitioning with strict 10x10 minimum rule and internal bathroom doors. """
    rooms = []
    if num_beds <= 0 or total_w < 10.0 or total_h < 10.0: return rooms
        
    MIN_W: float = 10.0
    MIN_H: float = 10.0

    max_cols: int = max(1, int(total_w // MIN_W))
    cols: int = min(int(num_beds), max_cols)
    rows: int = math.ceil(int(num_beds) / cols)
    
    if (total_h / rows) < MIN_H:
        rows = max(1, int(total_h // MIN_H))
        cols = math.ceil(int(num_beds) / rows)
        if (total_w / cols) < MIN_W: cols = max(1, int(total_w // MIN_W))
            
    cell_h: float = total_h / rows
    
    for r in range(int(rows)):
        current_row_start: int = r * cols
        beds_left: int = int(num_beds) - current_row_start
        actual_cols: int = min(cols, beds_left)
        cell_w: float = total_w / actual_cols
        
        for c in range(actual_cols):
            x: float = start_x + (c * cell_w)
            y: float = start_y + (r * cell_h)
            current_bed_idx: int = current_row_start + c + 1
            room_name: str = f"{name_prefix} {current_bed_idx}"
            
            if cell_w >= 14.0: 
                bath_w: float = min(5.0, cell_w - MIN_W)
                bath_h_actual: float = min(8.0, cell_h) 
                
                bed_w: float = cell_w - bath_w
                rooms.append({"name": room_name, "x": x, "y": y, "width": bed_w, "height": cell_h, "floor": floor_level})
                
                bath_room: Dict[str, Any] = {"name": "ATTACHED BATH", "x": x + bed_w, "y": y, "width": bath_w, "height": bath_h_actual, "floor": floor_level, "features": [{"type": "door", "wall": "left", "pos": bath_h_actual/2, "size": 2.5}]}
                rooms.append(bath_room)
                
            elif cell_h >= 14.0: 
                bath_h: float = min(5.0, cell_h - MIN_H)
                bath_w_actual: float = min(8.0, cell_w) 
                
                bed_h: float = cell_h - bath_h
                rooms.append({"name": room_name, "x": x, "y": y, "width": cell_w, "height": bed_h, "floor": floor_level})
                
                bath_room2: Dict[str, Any] = {"name": "ATTACHED BATH", "x": x, "y": y + bed_h, "width": bath_w_actual, "height": bath_h, "floor": floor_level, "features": [{"type": "door", "wall": "top", "pos": bath_w_actual/2, "size": 2.5}]}
                rooms.append(bath_room2)
                
            else:
                rooms.append({"name": room_name, "x": x, "y": y, "width": cell_w, "height": cell_h, "floor": floor_level})
                
            if current_bed_idx >= int(num_beds): break
        if current_row_start + actual_cols >= int(num_beds): break
                
    return rooms

def generate_single_floor(data, length, width, bedrooms) -> Dict[str, Any]:
    rooms = []
    front_h, mid_h, back_h = calculate_zones(length)
    
    rooms.append({"name": "CAR PARKING", "x": 0.0, "y": 0.0, "width": 10.0, "height": front_h, "floor": 0, "is_open": True})
    rooms.append({"name": "LIVING ROOM", "x": 10.0, "y": 0.0, "width": width - 10.0, "height": front_h, "floor": 0})
    
    bath_w = 5.0
    kit_w = max(8.0, width * 0.4)
    din_w = width - kit_w - bath_w
    
    rooms.append({"name": "KITCHEN", "x": 0.0, "y": front_h, "width": kit_w, "height": mid_h, "floor": 0})
    rooms.append({"name": "DINING HALL", "x": kit_w, "y": front_h, "width": din_w, "height": mid_h, "floor": 0})
    rooms.append({"name": "COMMON BATH", "x": width - bath_w, "y": front_h, "width": bath_w, "height": mid_h, "floor": 0})
    
    bed_start_y = front_h + mid_h
    rooms.extend(pack_bedrooms(0.0, bed_start_y, width, back_h, bedrooms, 0))
    
    rooms = add_architectural_details(rooms, width, length)
    return {"layout_type": f"Mathematical {bedrooms}BHK Ground Plan", "rooms": rooms}

def generate_duplex(data, length, width, bedrooms) -> Dict[str, Any]:
    rooms = []
    front_h, mid_h, back_h = calculate_zones(length)
    stair_w = min(7.0, width * 0.3)
    
    # GROUND FLOOR
    rooms.append({"name": "CAR PARKING", "x": 0.0, "y": 0.0, "width": 10.0, "height": front_h, "floor": 0, "is_open": True})
    rooms.append({"name": "LIVING HALL", "x": 10.0, "y": 0.0, "width": width - 10.0, "height": front_h, "floor": 0})
    
    rooms.append({"name": "STAIRCASE", "x": 0.0, "y": front_h, "width": stair_w, "height": mid_h, "floor": 0, "is_open": True})
    rooms.append({"name": "KITCHEN & DINING", "x": stair_w, "y": front_h, "width": width - stair_w, "height": mid_h, "floor": 0})
    
    back_y = front_h + mid_h
    rooms.extend(pack_bedrooms(0.0, back_y, width, back_h, 1, 0, "GUEST BED"))

    # FIRST FLOOR
    rooms.append({"name": "BALCONY", "x": 0.0, "y": 0.0, "width": 10.0, "height": front_h, "floor": 1, "is_open": True})
    rooms.extend(pack_bedrooms(10.0, 0.0, width - 10.0, front_h, 1, 1, "MASTER BED"))
    
    rooms.append({"name": "STAIRCASE", "x": 0.0, "y": front_h, "width": stair_w, "height": mid_h, "floor": 1, "is_open": True})
    rooms.append({"name": "LOUNGE", "x": stair_w, "y": front_h, "width": width - stair_w, "height": mid_h, "floor": 1})
    
    remaining_beds = max(1, bedrooms - 2) 
    rooms.extend(pack_bedrooms(0.0, back_y, width, back_h, remaining_beds, 1, "BED"))

    rooms = add_architectural_details(rooms, width, length)
    return {"layout_type": f"Premium {bedrooms}BHK Duplex", "rooms": rooms}

# ==========================================
# 🧠 THE AI KEYWORD BRAIN & LAYOUT ROUTER
# ==========================================
def generate_layout(data):
    length = float(data.get("length", 40))
    width = float(data.get("width", 30))
    bedrooms = max(1, int(data.get("bedrooms", 2)))
    
    # Extract Custom Requirements
    extras = data.get("extras", [])
    custom_reqs = data.get("custom_reqs", "").lower() 
    
    # 🧠 Scan text for keywords and force them into extras
    if "garden" in custom_reqs or "yard" in custom_reqs or "lawn" in custom_reqs:
        if "Garden" not in extras: extras.append("Garden")
    if "pool" in custom_reqs or "swimming" in custom_reqs:
        if "Pool" not in extras: extras.append("Pool")
        
    data["extras"] = extras # Save extracted keywords back to data
    
    # 📐 Smart Space Allocation: Save space at the back of the plot!
    usable_length = length
    backyard_size = 0
    if "Garden" in extras or "Pool" in extras:
        backyard_size = max(8.0, length * 0.2) # Reserve 20% of the plot length for the backyard
        usable_length = length - backyard_size # Shrink the physical house length
    
    area = usable_length * width
    
    # Generate the house using the SHRINKED usable length
    if bedrooms >= 3 or (area < 1000 and bedrooms > 1):
        result: dict = generate_duplex(data, usable_length, width, bedrooms)
    else:
        result: dict = generate_single_floor(data, usable_length, width, bedrooms)
        
    rooms_list: List[Dict[str, Any]] = result.get("rooms", [])
    # 🌳 Append the Backyard features AFTER the house is built
    if "Garden" in extras and "Pool" in extras:
        # Split the backyard into two halves
        rooms_list.append({"name": "GARDEN", "x": 0.0, "y": usable_length, "width": width/2, "height": backyard_size, "floor": 0, "is_open": True})
        rooms_list.append({"name": "SWIMMING POOL", "x": width/2, "y": usable_length, "width": width/2, "height": backyard_size, "floor": 0, "is_open": True})
    elif "Garden" in extras:
        rooms_list.append({"name": "GARDEN", "x": 0.0, "y": usable_length, "width": width, "height": backyard_size, "floor": 0, "is_open": True})
    elif "Pool" in extras:
        rooms_list.append({"name": "SWIMMING POOL", "x": 0.0, "y": usable_length, "width": width, "height": backyard_size, "floor": 0, "is_open": True})

    return result

# ==========================================
# 📊 CIVIL ENGINEERING BOQ ESTIMATOR
# ==========================================
def estimate_resources(length, width, bedrooms):
    """ Calculates precise construction materials and budget using real-world RCC thumb rules. """
    base_area = length * width
    is_duplex = bedrooms >= 3 or (base_area < 1000 and bedrooms > 1)
    total_area = base_area * 1.8 if is_duplex else base_area

    cement_bags = int(total_area * 0.45)     
    steel_kg = int(total_area * 4.0)         
    sand_cft = int(total_area * 0.9)         
    aggregate_cft = int(total_area * 1.42)   
    bricks = int(total_area * 5.25)          
    paint_liters = int(total_area * 0.175)   

    cement_cost = cement_bags * 375
    steel_cost = steel_kg * 65
    sand_cost = sand_cft * 60
    aggregate_cost = aggregate_cft * 60
    bricks_cost = bricks * 9
    
    core_materials_cost = cement_cost + steel_cost + sand_cost + aggregate_cost + bricks_cost
    total_budget = core_materials_cost * 2.1 
    
    budget_str = f"₹ {int(total_budget):,}"
    materials_str = (
        f"🧱 Bricks: {bricks:,} units,"
        f"🏗️ Cement: {cement_bags:,} bags,"
        f"⛓️ Steel: {steel_kg:,} kg,"
        f"⏳ Sand: {sand_cft:,} Cft,"
        f"🪨 Aggregate: {aggregate_cft:,} Cft,"
        f"🎨 Paint: {paint_liters:,} Liters"
    )

    return budget_str, materials_str