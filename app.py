import streamlit as st
from PIL import Image, ImageDraw
import io
import json

st.set_page_config(page_title="Clinical Mapper Pro", layout="wide")

# Room scale: 100 pixels per foot (10ft x 12ft room)
SCALE = 100

def draw_room(objs):
    img = Image.new('RGB', (10 * SCALE, 12 * SCALE), 'white')
    draw = ImageDraw.Draw(img)
    
    # Draw Grid
    for x in range(0, 1001, SCALE): draw.line([(x, 0), (x, 1200)], fill="#f1f5f9", width=2)
    for y in range(0, 1201, SCALE): draw.line([(0, y), (1000, y)], fill="#f1f5f9", width=2)

    # Fixtures Matched to Photo
    draw.rectangle([150, 0, 400, 15], fill="#78350f") # Door
    draw.rectangle([500, 0, 720, 180], fill="#f8fafc", outline="#cbd5e1", width=5) # Sink
    draw.rectangle([720, 0, 1000, 180], fill="#e2e8f0", outline="#94a3b8", width=5) # Workstation
    # Wall units on left wall
    draw.rectangle([0, 250, 30, 330], fill="#1e293b") # Towel
    draw.rectangle([0, 350, 25, 410], fill="#ef4444") # Sharps

    # Draw Personnel Tokens
    for code, info in objs.items():
        x, y = info['x'] * SCALE, info['y'] * SCALE
        # Field of View Cone (Only for Nurse 'N' and Parent 'P')
        if info['fov']:
            draw.pieslice([x-300, y-300, x+300, y+300], start=info['r']-45, end=info['r']+45, fill="#dbeafe")
        # Token Circle
        draw.ellipse([x-35, y-35, x+35, y+35], fill=info['color'], outline="white", width=4)
        draw.text((x-10, y-12), code, fill="white")
    return img

st.title("🏥 Clinical Incident Reconstruction")

if 'objs' not in st.session_state:
    st.session_state.objs = {
        'N':  {'name': 'Nurse (Witness)', 'x': 1.5, 'y': 4.5, 'r': 0,   'color': '#10b981', 'fov': True},
        'P':  {'name': 'Parent (Witness)', 'x': 8.0, 'y': 8.5, 'r': 270, 'color': '#8b5cf6', 'fov': True},
        'PT': {'name': 'Patient',         'x': 4.5, 'y': 6.5, 'r': 0,   'color': '#f97316', 'fov': False},
        'D':  {'name': 'Doctor',          'x': 7.0, 'y': 3.5, 'r': 180, 'color': '#3b82f6', 'fov': False}
    }

with st.sidebar:
    st.header("Controls")
    target = st.selectbox("Select Token", list(st.session_state.objs.keys()))
    st.session_state.objs[target]['x'] = st.slider("X Position (ft)", 0.0, 10.0, float(st.session_state.objs[target]['x']))
    st.session_state.objs[target]['y'] = st.slider("Y Position (ft)", 0.0, 12.0, float(st.session_state.objs[target]['y']))
    st.session_state.objs[target]['r'] = st.slider("Rotation (Facing)", 0, 360, st.session_state.objs[target]['r'])

final_map = draw_room(st.session_state.objs)
st.image(final_map, use_container_width=True)


if st.button("💾 Export Layout"):
    buf = io.BytesIO()
    final_map.save(buf, format="PNG")
    st.download_button("Download Image", buf.getvalue(), "reconstruction.png", "image/png")
