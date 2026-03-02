from visualizer import draw_layout
from layout_engine import generate_layout

input_data = {
    "length": 40,
    "width": 30,
    "bedrooms": 1,
    "bathrooms": 1
}

layout = generate_layout(input_data, option=1)

print(layout)

draw_layout(layout)