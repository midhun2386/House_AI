
# layout_engine.py

def linear_layout(data):
    length = data["length"]
    width = data["width"]
    bedrooms = data["bedrooms"]

    if width < 20 or length < 30:
        return {"error": "Plot too small for proper 2BHK layout"}

    if data["bedrooms"] * 9 > width:
        return {"error": "Too many bedrooms for given plot width"}
    

    living_height = length * 0.3
    service_height = length * 0.3
    corridor_height = 4
    bedroom_zone_height = (length * 0.4)

    rooms = []

    # 1️⃣ Living Room
    rooms.append({
        "name": "Living Room",
        "x": 0,
        "y": length - living_height,
        "width": width,
        "height": living_height
    })

    # bedroom
    bedroom_width = width / bedrooms

    for i in range(bedrooms):
        base_x = i * bedroom_width

        if i == 0:
            # Master Bedroom
            master_room_width = bedroom_width * 0.7
            master_bath_width = bedroom_width * 0.3

            rooms.append({
                "name": "Master Bedroom",
                "x": base_x,
                "y": service_height,
                "width": master_room_width,
                "height": bedroom_zone_height
                })

            rooms.append({
                "name": "Attached Bath",
                "x": base_x + master_room_width,
                "y": service_height,
                "width": master_bath_width,
                "height": bedroom_zone_height
                })

        else:
            rooms.append({
                "name": f"Bedroom {i+1}",
                "x": base_x,
                "y": service_height,
                "width": bedroom_width,
                "height": bedroom_zone_height
                 })

    # 3️⃣ Service Zone Split (Kitchen + Bathroom)
    kitchen_width = width * 0.6
    bathroom_width = width * 0.4

    rooms.append({
        "name": "Kitchen",
        "x": 0,
        "y": 0,
        "width": kitchen_width,
        "height": service_height
    })
    
    rooms.append({
        "name": "Corridor",
        "x": 0,
        "y": service_height,
        "width": width,
        "height": corridor_height
        })

    rooms.append({
        "name": "Common Bathroom",
        "x": kitchen_width,
        "y": 0,
        "width": bathroom_width,
        "height": service_height
    })

    return {
        "layout_type": "Linear",
        "rooms": rooms
    }


def side_corridor_layout(data):
    length = data["length"]
    width = data["width"]

    return {
        "layout_type": "Side Corridor",
        "plot_size": f"{length}x{width}"
    }


def central_layout(data):
    length = data["length"]
    width = data["width"]

    return {
        "layout_type": "Central Hall",
        "plot_size": f"{length}x{width}"
    }


def generate_layout(data, option=1):
    if option == 1:
        return linear_layout(data)
    elif option == 2:
        return side_corridor_layout(data)
    else:
        return central_layout(data)