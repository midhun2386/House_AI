# layout_engine.py
import math

def calculate_zones(length):
    """ Dynamically scales the front, middle, and back zones so they never overlap. """
    front_h = max(12.0, length * 0.35)
    back_h = max(10.0, length * 0.40)
    mid_h = length - front_h - back_h
    
    # If the middle gets too squished, steal space from the front and back
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
        
        # 1. MAIN GATE & BALCONY OPENINGS
        if r.get("is_open"):
            if "PARKING" in name:
                features.append({"type": "gate", "wall": "top", "pos": r["width"]/2, "size": 10.0})
            r["features"] = features
            continue

        is_bath = "BATH" in name
        win_size = 2.0 if is_bath else 4.0 
        
        # 2. WINDOWS (Only on exterior walls)
        if abs(r["x"]) < 0.1: 
            features.append({"type": "window", "wall": "left", "pos": r["height"]/2, "size": win_size})
        if abs(r["x"] + r["width"] - plot_w) < 0.1: 
            features.append({"type": "window", "wall": "right", "pos": r["height"]/2, "size": win_size})
        if abs(r["y"]) < 0.1: 
            features.append({"type": "window", "wall": "top", "pos": r["width"]/2, "size": win_size})
        if abs(r["y"] + r["height"] - plot_h) < 0.1: 
            features.append({"type": "window", "wall": "bottom", "pos": r["width"]/2, "size": win_size})
        
        # 3. DOORS (Smart Spatial Placement)
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
                pass # Open spaces, no doors needed
            else:
                door_size = 2.5 if is_bath else 3.0
                
                # Dynamic Door Logic
                if r["y"] < 0.1 and "MASTER" in name:
                    features.append({"type": "door", "wall": "bottom", "pos": 3.0, "size": door_size})
                    # Door directly to the Balcony (Pushed UP so it doesn't crash into the Lounge door!)
                    features.append({"type": "door", "wall": "left", "pos": 3.0, "size": door_size})
                elif r["y"] > plot_h * 0.5 and "BED" in name:
                    # BACK BEDROOMS
                    if "GUEST" in name:
                        # Duplex Guest bed: avoid stairs
                        safe_pos = stair_w - r["x"] + 2.0
                        features.append({"type": "door", "wall": "top", "pos": safe_pos, "size": door_size})
                    else:
                        # Single floor beds or 1st floor beds: Center the door so it never hits a partition wall!
                        features.append({"type": "door", "wall": "top", "pos": r["width"]/2, "size": door_size})
                else:
                    features.append({"type": "door", "wall": "top", "pos": 2.0, "size": door_size})
            
        r["features"] = features
    return rooms

def pack_bedrooms(start_x, start_y, total_w, total_h, num_beds, floor_level, name_prefix="BED"):
    """ Advanced Space Partitioning with strict 10x10 minimum rule and internal bathroom doors. """
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
            
            # ATTACHED BATHROOM LOGIC
            if cell_w >= 14.0: 
                # Limit bathroom size to 5x8 max to stop bowling alleys
                bath_w = min(5.0, cell_w - MIN_W)
                bath_h_actual = min(8.0, cell_h) 
                
                bed_w = cell_w - bath_w
                rooms.append({"name": room_name, "x": x, "y": y, "width": bed_w, "height": cell_h, "floor": floor_level})
                
                bath_room = {"name": "ATTACHED BATH", "x": x + bed_w, "y": y, "width": bath_w, "height": bath_h_actual, "floor": floor_level}
                bath_room["features"] = [{"type": "door", "wall": "left", "pos": bath_h_actual/2, "size": 2.5}]
                rooms.append(bath_room)
                
            elif cell_h >= 14.0: 
                bath_h = min(5.0, cell_h - MIN_H)
                bath_w_actual = min(8.0, cell_w) # Stop bowling alleys
                
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

def generate_duplex(data, length, width, bedrooms):
    rooms = []
    front_h, mid_h, back_h = calculate_zones(length)
    stair_w = min(7.0, width * 0.3)
    
    # ==========================================
    #               GROUND FLOOR
    # ==========================================
    rooms.append({"name": "CAR PARKING", "x": 0.0, "y": 0.0, "width": 10.0, "height": front_h, "floor": 0, "is_open": True})
    rooms.append({"name": "LIVING HALL", "x": 10.0, "y": 0.0, "width": width - 10.0, "height": front_h, "floor": 0})
    
    rooms.append({"name": "STAIRCASE", "x": 0.0, "y": front_h, "width": stair_w, "height": mid_h, "floor": 0, "is_open": True})
    rooms.append({"name": "KITCHEN & DINING", "x": stair_w, "y": front_h, "width": width - stair_w, "height": mid_h, "floor": 0})
    
    back_y = front_h + mid_h
    rooms.extend(pack_bedrooms(0.0, back_y, width, back_h, 1, 0, "GUEST BED"))

    # ==========================================
    #               FIRST FLOOR
    # ==========================================
    rooms.append({"name": "BALCONY", "x": 0.0, "y": 0.0, "width": 10.0, "height": front_h, "floor": 1, "is_open": True})
    rooms.extend(pack_bedrooms(10.0, 0.0, width - 10.0, front_h, 1, 1, "MASTER BED"))
    
    rooms.append({"name": "STAIRCASE", "x": 0.0, "y": front_h, "width": stair_w, "height": mid_h, "floor": 1, "is_open": True})
    rooms.append({"name": "LOUNGE", "x": stair_w, "y": front_h, "width": width - stair_w, "height": mid_h, "floor": 1})
    
    remaining_beds = max(1, bedrooms - 2) 
    rooms.extend(pack_bedrooms(0.0, back_y, width, back_h, remaining_beds, 1, "BED"))

    rooms = add_architectural_details(rooms, width, length)
    return {"layout_type": f"Premium {bedrooms}BHK Duplex", "rooms": rooms}

def generate_layout(data):
    length = float(data.get("length", 40))
    width = float(data.get("width", 30))
    bedrooms = max(1, int(data.get("bedrooms", 2)))
    
    area = length * width
    if bedrooms >= 3 or (area < 1000 and bedrooms > 1):
        return generate_duplex(data, length, width, bedrooms)
    
    return generate_single_floor(data, length, width, bedrooms)