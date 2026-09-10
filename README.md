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

No build step or package installation is required. Open `index.html` in a browser, or serve the folder with any static web server:

```bash
python3 -m http.server 8000
```

Then visit `http://localhost:8000`.

## Important scope note

This is a synthetic-data research demonstrator, not a flight-safety system. The calculation uses a simplified relative-motion model, and the map's hazard zone is an illustrative orbital proximity zone—not a geographic ground-impact prediction. A production system would need authoritative ephemerides, uncertainty/covariance data, an orbital propagator, validated probability-of-collision methods, and human/mission approval before any maneuver recommendation.

## Suggested faculty explanation

“OrbitGuard is an early-stage decision-support prototype. I created a controlled synthetic dataset so the workflow can be demonstrated without claiming access to live spacecraft telemetry. The prototype converts relative position and velocity into an estimated closest approach, ranks events by a transparent risk score, and shows the result in a dashboard. The next research step would be replacing the synthetic model with validated TLE/ephemeris data and uncertainty-aware collision probability.”
