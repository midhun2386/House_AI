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

def pack_bedrooms(start_x, start_y, total_w, total_h, num_beds, floor_level, name_prefix="BED"):
    """
    Advanced Space Partitioning with a strict 10x10 minimum rule.
    """
    rooms = []
    if num_beds <= 0 or total_w < 10.0 or total_h < 10.0:
        return rooms
        
    # --- THE 10x10 IRONCLAD RULE ---
    MIN_W, MIN_H = 10.0, 10.0

    # How many columns can we physically fit at 10ft wide each?
    max_cols = max(1, int(total_w // MIN_W))
    cols = min(num_beds, max_cols)
    
    # How many rows do we need?
    rows = math.ceil(num_beds / cols)
    
    # Safety Check: Can we fit this many rows at 10ft high each?
    if (total_h / rows) < MIN_H:
        rows = max(1, int(total_h // MIN_H)) # Force fewer rows
        cols = math.ceil(num_beds / rows)    # Recalculate columns
        if (total_w / cols) < MIN_W:
            cols = max(1, int(total_w // MIN_W)) # Hard limit columns again
            
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
            
            # --- CARVE BATHROOM ONLY IF SPACE PERMITS ---
            # We must leave at least 10ft for the bed.
            if cell_w >= 14.0: 
                # Carve horizontally (e.g. 14ft total = 10ft bed + 4ft bath)
                bath_w = min(5.0, cell_w - MIN_W)
                bed_w = cell_w - bath_w
                rooms.append({"name": room_name, "x": x, "y": y, "width": bed_w, "height": cell_h, "floor": floor_level})
                rooms.append({"name": "BATH", "x": x + bed_w, "y": y, "width": bath_w, "height": cell_h, "floor": floor_level})
            elif cell_h >= 14.0: 
                # Carve vertically
                bath_h = min(5.0, cell_h - MIN_H)
                bed_h = cell_h - bath_h
                rooms.append({"name": room_name, "x": x, "y": y, "width": cell_w, "height": bed_h, "floor": floor_level})
                rooms.append({"name": "BATH", "x": x, "y": y + bed_h, "width": cell_w, "height": bath_h, "floor": floor_level})
            else:
                # Too tight for an attached bath while keeping a 10x10 bed. Pure bedroom!
                rooms.append({"name": room_name, "x": x, "y": y, "width": cell_w, "height": cell_h, "floor": floor_level})
                
            count += 1
            if count >= num_beds: break
        if count >= num_beds: break
                
    return rooms

def generate_single_floor(data, length, width, bedrooms):
    rooms = []
    front_h, mid_h, back_h = calculate_zones(length)
    
    # Zone 1: Front
    rooms.append({"name": "CAR PARKING", "x": 0.0, "y": 0.0, "width": 10.0, "height": front_h, "floor": 0, "is_open": True})
    rooms.append({"name": "LIVING ROOM", "x": 10.0, "y": 0.0, "width": width - 10.0, "height": front_h, "floor": 0})
    
    # Zone 2: Middle Utility
    kit_w = max(10.0, width * 0.6)
    rooms.append({"name": "KITCHEN", "x": 0.0, "y": front_h, "width": kit_w, "height": mid_h, "floor": 0})
    rooms.append({"name": "COMMON BATH", "x": kit_w, "y": front_h, "width": width - kit_w, "height": mid_h, "floor": 0})
    
    # Zone 3: Bedrooms (Using 10x10 Grid Math)
    bed_start_y = front_h + mid_h
    rooms.extend(pack_bedrooms(0.0, bed_start_y, width, back_h, bedrooms, 0))
    
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
    kit_w = max(8.0, (width - stair_w) * 0.5)
    rooms.append({"name": "KITCHEN", "x": stair_w, "y": front_h, "width": kit_w, "height": mid_h, "floor": 0})
    rooms.append({"name": "DINING", "x": stair_w + kit_w, "y": front_h, "width": width - stair_w - kit_w, "height": mid_h, "floor": 0})
    
    # Ground Floor Back (1 Guest Bed)
    back_y = front_h + mid_h
    rooms.extend(pack_bedrooms(0.0, back_y, width, back_h, 1, 0, "GUEST BED"))

    # ==========================================
    #               FIRST FLOOR
    # ==========================================
    rooms.append({"name": "BALCONY", "x": 0.0, "y": 0.0, "width": 10.0, "height": front_h, "floor": 1, "is_open": True})
    rooms.extend(pack_bedrooms(10.0, 0.0, width - 10.0, front_h, 1, 1, "MASTER BED"))
    
    rooms.append({"name": "STAIRCASE", "x": 0.0, "y": front_h, "width": stair_w, "height": mid_h, "floor": 1, "is_open": True})
    rooms.append({"name": "LOUNGE", "x": stair_w, "y": front_h, "width": width - stair_w, "height": mid_h, "floor": 1})
    
    # First Floor Back (Remaining Beds)
    remaining_beds = max(1, bedrooms - 2) 
    rooms.extend(pack_bedrooms(0.0, back_y, width, back_h, remaining_beds, 1, "BED"))

    return {"layout_type": f"Premium {bedrooms}BHK Duplex", "rooms": rooms}

def generate_layout(data):
    length = float(data.get("length", 40))
    width = float(data.get("width", 30))
    bedrooms = max(1, int(data.get("bedrooms", 2)))
    
    if bedrooms >= 3 or (length * width < 1000 and bedrooms > 1):
        return generate_duplex(data, length, width, bedrooms)
    
    return generate_single_floor(data, length, width, bedrooms)