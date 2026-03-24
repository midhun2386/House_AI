# layout_engine.py
import math

def calculate_zones(length):
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
    stair_w = min(7.0, plot_w * 0.3)
    
    for r in rooms:
        features = r.get("features", []) 
        name = r["name"]
        
        if r.get("is_open"):
            if "PARKING" in name:
                features.append({"type": "gate", "wall": "top", "pos": r["width"]/2, "size": 10.0})
            r["features"] = features
            continue

        is_bath = "BATH" in name
        win_size = 2.0 if is_bath else 4.0 
        
        if abs(r["x"]) < 0.1: features.append({"type": "window", "wall": "left", "pos": r["height"]/2, "size": win_size})
        if abs(r["x"] + r["width"] - plot_w) < 0.1: features.append({"type": "window", "wall": "right", "pos": r["height"]/2, "size": win_size})
        if abs(r["y"]) < 0.1: features.append({"type": "window", "wall": "top", "pos": r["width"]/2, "size": win_size})
        if abs(r["y"] + r["height"] - plot_h) < 0.1: features.append({"type": "window", "wall": "bottom", "pos": r["width"]/2, "size": win_size})
        
        has_door = any(f["type"] in ["door", "main_door", "arch", "shutter"] for f in features)
        
        if not has_door:
            if "LIVING" in name:
                features.append({"type": "main_door", "wall": "left", "pos": r["height"] - 3.0, "size": 3.5})
            elif "DINING HALL" in name:
                features.append({"type": "arch", "wall": "top", "pos": r["width"]/2, "size": 6.0})
            elif "KITCHEN" in name:
                if "DINING" in name: features.append({"type": "arch", "wall": "top", "pos": r["width"]/2, "size": 6.0})
                else: features.append({"type": "arch", "wall": "right", "pos": r["height"]/2, "size": 5.0})
            elif "COMMON BATH" in name:
                features.append({"type": "door", "wall": "left", "pos": r["height"] - 2.5, "size": 2.5})
            elif "PUJA" in name or "STORE" in name:
                features.append({"type": "door", "wall": "bottom", "pos": r["width"]/2, "size": 2.5})
            elif any(k in name for k in ["LOUNGE", "PASSAGE", "STAIRCASE", "SHOP"]):
                pass 
            else:
                door_size = 2.5 if is_bath else 3.0
                if r["y"] < 0.1 and "MASTER" in name:
                    features.append({"type": "door", "wall": "bottom", "pos": 3.0, "size": door_size})
                    features.append({"type": "door", "wall": "left", "pos": 3.0, "size": door_size})
                elif r["y"] > plot_h * 0.5 and ("BED" in name or "OFFICE" in name or "GYM" in name or "THEATER" in name):
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
    rooms = []
    if num_beds <= 0 or total_w < 10.0 or total_h < 10.0: return rooms
    MIN_W, MIN_H = 10.0, 10.0
    max_cols = max(1, int(total_w // MIN_W))
    cols = min(num_beds, max_cols)
    rows = math.ceil(num_beds / cols)
    
    if (total_h / rows) < MIN_H:
        rows = max(1, int(total_h // MIN_H))
        cols = math.ceil(num_beds / rows)
        if (total_w / cols) < MIN_W: cols = max(1, int(total_w // MIN_W))
            
    cell_h = total_h / rows
    count = 0
    for r in range(rows):
        beds_left = num_beds - count
        actual_cols = min(cols, beds_left)
        cell_w = total_w / actual_cols
        for c in range(actual_cols):
            x = start_x + (c * cell_w)
            y = start_y + (r * cell_h)
            room_name = f"{name_prefix} {count+1}"
            
            if cell_w >= 14.0: 
                bath_w = min(5.0, cell_w - MIN_W)
                bath_h_actual = min(8.0, cell_h) 
                bed_w = cell_w - bath_w
                rooms.append({"name": room_name, "x": x, "y": y, "width": bed_w, "height": cell_h, "floor": floor_level})
                bath_room = {"name": "ATTACHED BATH", "x": x + bed_w, "y": y, "width": bath_w, "height": bath_h_actual, "floor": floor_level}
                bath_room["features"] = [{"type": "door", "wall": "left", "pos": bath_h_actual/2, "size": 2.5}]
                rooms.append(bath_room)
            elif cell_h >= 14.0: 
                bath_h = min(5.0, cell_h - MIN_H)
                bath_w_actual = min(8.0, cell_w) 
                bed_h = cell_h - bath_h
                rooms.append({"name": room_name, "x": x, "y": y, "width": cell_w, "height": bed_h, "floor": floor_level})
                bath_room = {"name": "ATTACHED BATH", "x": x, "y": y + bed_h, "width": bath_w_actual, "height": bath_h, "floor": floor_level}
                bath_room["features"] = [{"type": "door", "wall": "top", "pos": bath_w_actual/2, "size": 2.5}]
                rooms.append(bath_room)
            else:
                rooms.append({"name": room_name, "x": x, "y": y, "width": cell_w, "height": cell_h, "floor": floor_level})
            count += 1
            if count >= num_beds: break
        if count >= num_beds: break
    return rooms

def generate_single_floor(data, length, width, bedrooms):
    rooms = []
    front_h, mid_h, back_h = calculate_zones(length)
    indoor_extras = data.get("indoor_extras", [])
    
    rooms.append({"name": "CAR PARKING", "x": 0.0, "y": 0.0, "width": 10.0, "height": front_h, "floor": 0, "is_open": True})
    rooms.append({"name": "LIVING ROOM", "x": 10.0, "y": 0.0, "width": width - 10.0, "height": front_h, "floor": 0})
    
    bath_w = 5.0
    kit_w = max(8.0, width * 0.4)
    din_w = width - kit_w - bath_w
    din_x = kit_w
    
    if "PUJA ROOM" in indoor_extras:
        rooms.append({"name": "PUJA ROOM", "x": din_x, "y": front_h, "width": 5.0, "height": mid_h, "floor": 0})
        din_x += 5.0; din_w -= 5.0
        indoor_extras.remove("PUJA ROOM")
    elif "STORE ROOM" in indoor_extras:
        rooms.append({"name": "STORE ROOM", "x": din_x, "y": front_h, "width": 5.0, "height": mid_h, "floor": 0})
        din_x += 5.0; din_w -= 5.0
        indoor_extras.remove("STORE ROOM")
    
    rooms.append({"name": "KITCHEN", "x": 0.0, "y": front_h, "width": kit_w, "height": mid_h, "floor": 0})
    rooms.append({"name": "DINING HALL", "x": din_x, "y": front_h, "width": max(5.0, din_w), "height": mid_h, "floor": 0})
    rooms.append({"name": "COMMON BATH", "x": width - bath_w, "y": front_h, "width": bath_w, "height": mid_h, "floor": 0})
    
    extra_rooms_needed = indoor_extras.copy()
    total_back_rooms = bedrooms + len(extra_rooms_needed)
    
    bed_start_y = front_h + mid_h
    packed_rooms = pack_bedrooms(0.0, bed_start_y, width, back_h, total_back_rooms, 0)
    
    for r in packed_rooms:
        if "BED" in r["name"] and "ATTACHED" not in r["name"] and extra_rooms_needed:
            bed_num = int(r["name"].split(" ")[1])
            if bed_num > bedrooms: r["name"] = extra_rooms_needed.pop(0)
            
    rooms.extend(packed_rooms)
    rooms = add_architectural_details(rooms, width, length)
    return {"layout_type": f"AI Optimized {bedrooms}BHK Ground Plan", "rooms": rooms}

def generate_duplex(data, length, width, bedrooms):
    rooms = []
    front_h, mid_h, back_h = calculate_zones(length)
    stair_w = min(7.0, width * 0.3)
    indoor_extras = data.get("indoor_extras", [])
    
    # === GROUND FLOOR ===
    rooms.append({"name": "CAR PARKING", "x": 0.0, "y": 0.0, "width": 10.0, "height": front_h, "floor": 0, "is_open": True})
    rooms.append({"name": "LIVING HALL", "x": 10.0, "y": 0.0, "width": width - 10.0, "height": front_h, "floor": 0})
    rooms.append({"name": "STAIRCASE", "x": 0.0, "y": front_h, "width": stair_w, "height": mid_h, "floor": 0, "is_open": True})
    
    kit_w = width - stair_w
    kit_x = stair_w
    
    if "PUJA ROOM" in indoor_extras:
        rooms.append({"name": "PUJA ROOM", "x": kit_x, "y": front_h, "width": 5.0, "height": mid_h, "floor": 0})
        kit_x += 5.0; kit_w -= 5.0
        indoor_extras.remove("PUJA ROOM")
    elif "STORE ROOM" in indoor_extras:
        rooms.append({"name": "STORE ROOM", "x": kit_x, "y": front_h, "width": 5.0, "height": mid_h, "floor": 0})
        kit_x += 5.0; kit_w -= 5.0
        indoor_extras.remove("STORE ROOM")
        
    rooms.append({"name": "KITCHEN & DINING", "x": kit_x, "y": front_h, "width": kit_w, "height": mid_h, "floor": 0})
    
    back_y = front_h + mid_h
    rooms.extend(pack_bedrooms(0.0, back_y, width, back_h, 1, 0, "GUEST BED"))

    # === FIRST FLOOR ===
    rooms.append({"name": "BALCONY", "x": 0.0, "y": 0.0, "width": 10.0, "height": front_h, "floor": 1, "is_open": True})
    rooms.extend(pack_bedrooms(10.0, 0.0, width - 10.0, front_h, 1, 1, "MASTER BED"))
    rooms.append({"name": "STAIRCASE", "x": 0.0, "y": front_h, "width": stair_w, "height": mid_h, "floor": 1, "is_open": True})
    rooms.append({"name": "LOUNGE", "x": stair_w, "y": front_h, "width": width - stair_w, "height": mid_h, "floor": 1})
    
    remaining_beds = max(1, bedrooms - 2) 
    extra_rooms_needed = indoor_extras.copy()
    total_ff_rooms = remaining_beds + len(extra_rooms_needed)
    
    packed_ff_rooms = pack_bedrooms(0.0, back_y, width, back_h, total_ff_rooms, 1, "BED")
    
    for r in packed_ff_rooms:
        if "BED" in r["name"] and "ATTACHED" not in r["name"] and extra_rooms_needed:
            bed_num = int(r["name"].split(" ")[1])
            if bed_num > remaining_beds: r["name"] = extra_rooms_needed.pop(0)
            
    rooms.extend(packed_ff_rooms)
    rooms = add_architectural_details(rooms, width, length)
    return {"layout_type": f"AI Premium {bedrooms}BHK Duplex", "rooms": rooms}

# ==========================================
# 🏪 NEW: COMMERCIAL PLAZA GENERATOR
# ==========================================
def generate_commercial(data, length, width, units):
    """ Generates a commercial plaza with an open walkway and multiple storefronts. """
    rooms = []
    
    # Front 30% of the plot is for parking and a walking corridor
    front_walkway_h = max(10.0, length * 0.3)
    shop_h = length - front_walkway_h
    
    rooms.append({
        "name": "PARKING & WALKWAY", 
        "x": 0.0, "y": 0.0, 
        "width": width, "height": front_walkway_h, 
        "floor": 0, "is_open": True
    })
    
    # Divide the rest of the plot evenly into shops
    shop_w = width / units
    for c in range(units):
        x = c * shop_w
        rooms.append({
            "name": f"SHOP UNIT {c+1}", 
            "x": x, "y": front_walkway_h, 
            "width": shop_w, "height": shop_h, 
            "floor": 0,
            # Give every shop a wide rolling shutter facing the walkway!
            "features": [{"type": "shutter", "wall": "top", "pos": shop_w/2, "size": min(8.0, shop_w - 2.0)}]
        })
        
    rooms = add_architectural_details(rooms, width, length)
    return {"layout_type": f"Commercial {units}-Shop Plaza", "rooms": rooms}

# ==========================================
# 🧠 THE AI NLP KEYWORD BRAIN & ROUTER
# ==========================================
def generate_layout(data):
    length = float(data.get("length", 40))
    width = float(data.get("width", 30))
    bedrooms = max(1, int(data.get("bedrooms", 2)))
    
    extras = data.get("extras", [])
    custom_reqs = data.get("custom_reqs", "").lower() 
    indoor_extras = []
    
    # --- NLP KEYWORD SCANNER ---
    if any(k in custom_reqs for k in ["garden", "yard", "lawn"]):
        if "Garden" not in extras: extras.append("Garden")
    if any(k in custom_reqs for k in ["pool", "swimming"]):
        if "Pool" not in extras: extras.append("Pool")
        
    if any(k in custom_reqs for k in ["office", "study", "workspace"]): indoor_extras.append("OFFICE")
    if any(k in custom_reqs for k in ["gym", "workout", "fitness"]): indoor_extras.append("GYM")
    if any(k in custom_reqs for k in ["theater", "cinema", "movie"]): indoor_extras.append("HOME THEATER")
    if any(k in custom_reqs for k in ["puja", "pooja", "prayer", "mandir"]): indoor_extras.append("PUJA ROOM")
    if any(k in custom_reqs for k in ["store", "pantry"]): indoor_extras.append("STORE ROOM")
        
    data["extras"] = extras 
    data["indoor_extras"] = indoor_extras 
    
    # --- OUTDOOR SPACE ALLOCATION ---
    usable_length = length
    backyard_size = 0
    if "Garden" in extras or "Pool" in extras:
        backyard_size = max(8.0, length * 0.2) 
        usable_length = length - backyard_size 
    
    area = usable_length * width
    building_type = data.get("building_type", "House")
    units = max(1, int(data.get("units", 1)))
    
    # 🧠 ROUTER: Decide what kind of building to generate!
    if building_type == "Shop":
        result = generate_commercial(data, usable_length, width, units)
    elif bedrooms >= 3 or (area < 1000 and bedrooms > 1) or building_type == "Apartment":
        # Treating apartments similar to multi-floor layouts for now
        result = generate_duplex(data, usable_length, width, bedrooms)
    else:
        result = generate_single_floor(data, usable_length, width, bedrooms)
        
    # --- DRAW THE BACKYARD ---
    if "Garden" in extras and "Pool" in extras:
        result["rooms"].append({"name": "GARDEN", "x": 0.0, "y": usable_length, "width": width/2, "height": backyard_size, "floor": 0, "is_open": True})
        result["rooms"].append({"name": "SWIMMING POOL", "x": width/2, "y": usable_length, "width": width/2, "height": backyard_size, "floor": 0, "is_open": True})
    elif "Garden" in extras:
        result["rooms"].append({"name": "GARDEN", "x": 0.0, "y": usable_length, "width": width, "height": backyard_size, "floor": 0, "is_open": True})
    elif "Pool" in extras:
        result["rooms"].append({"name": "SWIMMING POOL", "x": 0.0, "y": usable_length, "width": width, "height": backyard_size, "floor": 0, "is_open": True})

    return result

# ==========================================
# 📊 CIVIL ENGINEERING BOQ ESTIMATOR
# ==========================================
def estimate_resources(length, width, bedrooms):
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