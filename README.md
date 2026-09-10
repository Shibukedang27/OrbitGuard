# OrbitGuard

OrbitGuard is a small educational MVP that demonstrates how a space-debris monitoring workflow can be presented to a human operator.

## What it demonstrates

- A synthetic catalog of satellites and debris fragments.
- Relative-motion analysis to estimate time to closest approach (TCA).
- A simple risk score based on distance, altitude difference, and relative speed.
- A visual orbital map and a prioritized close-approach queue.
- A synthetic proximity hazard zone around the highest-priority encounter.
- A table that makes every tracked object and its calculated state inspectable.

## Run it

This version is Python-based and uses Streamlit:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Streamlit will open the dashboard in a browser.

## Important scope note

This is a synthetic-data research demonstrator, not a flight-safety system. The calculation uses a simplified relative-motion model, and the map's hazard zone is an illustrative orbital proximity zone—not a geographic ground-impact prediction. A production system would need authoritative ephemerides, uncertainty/covariance data, an orbital propagator, validated probability-of-collision methods, and human/mission approval before any maneuver recommendation.

## Faculty report

The faculty-facing explanation, technology choices, methodology, limitations, and viva prompts are available in [`docs/OrbitGuard_Faculty_Report.pdf`](docs/OrbitGuard_Faculty_Report.pdf).
