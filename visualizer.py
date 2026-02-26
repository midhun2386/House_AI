import matplotlib.pyplot as plt

def draw_layout(layout_data):
    if "error" in layout_data:
        print(layout_data["error"])
        return

    rooms = layout_data["rooms"]

    fig, ax = plt.subplots()

    for room in rooms:
        x = room["x"]
        y = room["y"]
        width = room["width"]
        height = room["height"]

        # Draw rectangle
        # Choose color based on room type
        if "Bedroom" in room["name"]:
            color = "#90caf9"   # light blue
        elif "Bath" in room["name"]:
            color = "#ffcc80"   # light orange
        elif "Kitchen" in room["name"]:
            color = "#a5d6a7"   # light green
        elif "Living" in room["name"]:
            color = "#ce93d8"   # light purple
        else:
            color = "#eeeeee"

        rect = plt.Rectangle(
            (x, y),
            width,
            height,
            facecolor=color,
            edgecolor="black",
            alpha=0.6
        )

        ax.add_patch(rect)

    # Add room name text
        ax.text(
            x + width / 2,
            y + height / 2,
            room["name"],
            ha='center',
            va='center',
            fontsize=9, 
            fontweight='bold'
        )

    ax.set_aspect('equal', 'box')
    ax.set_xlim(0, max(r["x"] + r["width"] for r in rooms))
    ax.set_ylim(0, max(r["y"] + r["height"] for r in rooms))
    ax.invert_yaxis()
    
    plt.title(layout_data["layout_type"] + " Layout")
    plt.xlabel("Width")
    plt.ylabel("Length")
    plt.grid(True)
    plt.show()