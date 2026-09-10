"""OrbitGuard: synthetic space-debris monitoring MVP.

This is an educational prototype. Real mission systems need authoritative
ephemerides, uncertainty covariance, validated propagators, and review by
qualified flight-dynamics teams before any maneuver decision.
"""

import math
from copy import deepcopy

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st


st.set_page_config(page_title="OrbitGuard", page_icon="🛰️", layout="wide")

st.markdown(
    """
    <style>
    .stApp { background: #07111f; color: #eef6ff; }
    [data-testid="stMetric"] { background: #0d1b2d; border: 1px solid #203652; padding: 14px; border-radius: 12px; }
    .notice { background: #241c0c; border: 1px solid #63502e; color: #e8c98b; padding: 14px; border-radius: 10px; margin: 8px 0 22px; }
    .small-muted { color: #8fa5bd; font-size: 0.85rem; }
    </style>
    """,
    unsafe_allow_html=True,
)


BASE_OBJECTS = [
    {"id": "OG-SAT-01", "name": "Sentinel-1", "type": "Satellite", "altitude": 550, "x": 31, "y": 34, "vx": 0.36, "vy": 0.21},
    {"id": "OG-DEB-17", "name": "Fragment-17", "type": "Debris", "altitude": 548, "x": 63, "y": 43, "vx": -0.27, "vy": -0.19},
    {"id": "OG-DEB-04", "name": "Panel-04", "type": "Debris", "altitude": 565, "x": 72, "y": 68, "vx": -0.12, "vy": -0.08},
    {"id": "OG-DEB-29", "name": "Bolt-29", "type": "Debris", "altitude": 520, "x": 24, "y": 72, "vx": 0.09, "vy": -0.16},
    {"id": "OG-SAT-02", "name": "Relay-2", "type": "Satellite", "altitude": 610, "x": 78, "y": 25, "vx": -0.08, "vy": 0.14},
    {"id": "OG-DEB-31", "name": "Shard-31", "type": "Debris", "altitude": 603, "x": 17, "y": 24, "vx": 0.18, "vy": 0.10},
]


def calculate_encounter(satellite, debris):
    """Estimate closest approach using a simple relative-motion model."""
    relative_x = debris["x"] - satellite["x"]
    relative_y = debris["y"] - satellite["y"]
    relative_vx = debris["vx"] - satellite["vx"]
    relative_vy = debris["vy"] - satellite["vy"]
    speed_squared = relative_vx**2 + relative_vy**2

    # For r(t) = r0 + v*t, this is the time at which distance is minimized.
    raw_time = -((relative_x * relative_vx) + (relative_y * relative_vy)) / speed_squared if speed_squared else 0
    time_hours = max(0, min(72, raw_time * 8))
    closest_x = relative_x + relative_vx * (time_hours / 8)
    closest_y = relative_y + relative_vy * (time_hours / 8)
    distance = math.sqrt(closest_x**2 + closest_y**2)
    relative_speed = math.sqrt(speed_squared) * 7.5
    altitude_delta = abs(debris["altitude"] - satellite["altitude"])
    risk_score = max(0, min(99, round(100 - distance * 1.8 - altitude_delta * 0.55 + relative_speed * 1.5)))
    risk = "HIGH" if risk_score >= 70 else "MEDIUM" if risk_score >= 45 else "LOW"
    return {
        "distance": round(distance, 1),
        "time_hours": round(time_hours, 1),
        "relative_speed": round(relative_speed, 2),
        "risk_score": risk_score,
        "risk": risk,
    }


def build_model():
    objects = deepcopy(BASE_OBJECTS)
    satellite = next(item for item in objects if item["type"] == "Satellite")
    encounters = []
    for debris in (item for item in objects if item["type"] == "Debris"):
        encounters.append({"object": debris, "encounter": calculate_encounter(satellite, debris)})
    return objects, sorted(encounters, key=lambda item: item["encounter"]["risk_score"], reverse=True)


def draw_orbit_map(objects, encounters):
    figure, axis = plt.subplots(figsize=(10, 5), facecolor="#081321")
    axis.set_facecolor("#081321")
    for width, height, color in [(0.82, 0.55, "#2a6683"), (0.59, 0.37, "#3b5674")]:
        orbit = plt.Circle((50, 50), width * 45, fill=False, color=color, alpha=0.7)
        axis.add_patch(orbit)
    earth = plt.Circle((50, 50), 7, color="#24769b", alpha=0.95)
    axis.add_patch(earth)

    highest_risk = encounters[0]["object"]
    hazard = plt.Circle((highest_risk["x"], highest_risk["y"]), 9, fill=False, color="#ff7e8a", linestyle="--", linewidth=1.5)
    axis.add_patch(hazard)
    axis.text(highest_risk["x"], highest_risk["y"] - 12, "synthetic hazard zone", color="#ffadb4", ha="center", fontsize=8)

    for item in objects:
        color = "#64d8ff" if item["type"] == "Satellite" else "#ff7e8a"
        axis.scatter(item["x"], item["y"], color=color, s=70, zorder=3)
        axis.text(item["x"], item["y"] + 4, item["name"], color="#d4e7f8", ha="center", fontsize=8)
    axis.set_xlim(0, 100)
    axis.set_ylim(0, 100)
    axis.axis("off")
    figure.tight_layout()
    return figure


st.title("OrbitGuard")
st.subheader("Space debris risk, made visible.")
st.caption("A synthetic-data demonstrator for tracking orbital objects and prioritizing close-approach alerts.")
st.markdown('<div class="notice"><b>Research prototype:</b> all objects and calculations are synthetic. This dashboard is for education and visualization, not flight operations or maneuver decisions.</div>', unsafe_allow_html=True)

objects, encounters = build_model()
high_risk_count = sum(item["encounter"]["risk"] == "HIGH" for item in encounters)
medium_risk_count = sum(item["encounter"]["risk"] == "MEDIUM" for item in encounters)
closest = encounters[0]["encounter"]

metric_columns = st.columns(4)
metric_columns[0].metric("Tracked objects", len(objects), "Synthetic catalog")
metric_columns[1].metric("High-risk encounters", high_risk_count, "Needs review")
metric_columns[2].metric("Closest approach", f'{closest["distance"]} km', encounters[0]["object"]["name"])
metric_columns[3].metric("Risk horizon", "72 hrs", f"{medium_risk_count} medium-risk event(s)")

left, right = st.columns([1.25, 0.75])
with left:
    st.markdown("### Relative position map")
    st.pyplot(draw_orbit_map(objects, encounters), use_container_width=True)
with right:
    st.markdown("### Close-approach alerts")
    for item in encounters[:3]:
        object_data = item["object"]
        encounter = item["encounter"]
        st.warning(
            f'{object_data["name"]} — {encounter["risk"]}\n\n'
            f'Closest approach: {encounter["distance"]} km · '
            f'TCA: {encounter["time_hours"]} hours · '
            f'Relative speed: {encounter["relative_speed"]} km/s'
        )

st.markdown("### Simulation catalog")
rows = []
for object_data in objects:
    encounter = next((item["encounter"] for item in encounters if item["object"]["id"] == object_data["id"]), None)
    rows.append({
        "Object": f'{object_data["name"]} ({object_data["id"]})',
        "Type": object_data["type"],
        "Altitude (km)": object_data["altitude"],
        "Relative speed (km/s)": encounter["relative_speed"] if encounter else None,
        "Risk": f'{encounter["risk"]} · {encounter["risk_score"]}/100' if encounter else "MONITORED",
        "Time to closest approach (hours)": encounter["time_hours"] if encounter else None,
    })
st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
st.caption("Method: synthetic relative-motion model + distance thresholds. The hazard zone is an illustrative orbital proximity zone, not a geographic ground-impact prediction.")
