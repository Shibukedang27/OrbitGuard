// OrbitGuard MVP: a transparent synthetic-data demo of close-approach analysis.
// Real mission systems use precise ephemerides, covariance matrices, and validated
// orbit propagators. This small model is intentionally safe and easy to understand.

const baseObjects = [
  { id: "OG-SAT-01", name: "Sentinel-1", type: "satellite", altitude: 550, x: 31, y: 34, vx: 0.36, vy: 0.21 },
  { id: "OG-DEB-17", name: "Fragment-17", type: "debris", altitude: 548, x: 63, y: 43, vx: -0.27, vy: -0.19 },
  { id: "OG-DEB-04", name: "Panel-04", type: "debris", altitude: 565, x: 72, y: 68, vx: -0.12, vy: -0.08 },
  { id: "OG-DEB-29", name: "Bolt-29", type: "debris", altitude: 520, x: 24, y: 72, vx: 0.09, vy: -0.16 },
  { id: "OG-SAT-02", name: "Relay-2", type: "satellite", altitude: 610, x: 78, y: 25, vx: -0.08, vy: 0.14 },
  { id: "OG-DEB-31", name: "Shard-31", type: "debris", altitude: 603, x: 17, y: 24, vx: 0.18, vy: 0.10 }
];

function calculateEncounter(satellite, debris) {
  // Relative-motion approximation: r(t) = r0 + v*t. We search a short horizon.
  const rx = debris.x - satellite.x;
  const ry = debris.y - satellite.y;
  const vx = debris.vx - satellite.vx;
  const vy = debris.vy - satellite.vy;
  const speedSquared = vx * vx + vy * vy;
  const rawTime = speedSquared ? -((rx * vx) + (ry * vy)) / speedSquared : 0;
  const timeHours = Math.max(0, Math.min(72, rawTime * 8));
  const closestX = rx + vx * (timeHours / 8);
  const closestY = ry + vy * (timeHours / 8);
  const distance = Math.sqrt(closestX ** 2 + closestY ** 2);
  const relativeSpeed = Math.sqrt(speedSquared) * 7.5;
  const altitudeDelta = Math.abs(debris.altitude - satellite.altitude);
  const riskScore = Math.max(0, Math.min(99, Math.round(100 - distance * 1.8 - altitudeDelta * 0.55 + relativeSpeed * 1.5)));
  const risk = riskScore >= 70 ? "HIGH" : riskScore >= 45 ? "MEDIUM" : "LOW";
  return { distance: distance.toFixed(1), timeHours: timeHours.toFixed(1), relativeSpeed: relativeSpeed.toFixed(2), riskScore, risk };
}

function buildModel() {
  const objects = baseObjects.map((object) => ({ ...object }));
  const satellite = objects.find((object) => object.type === "satellite");
  const debris = objects.filter((object) => object.type === "debris");
  const encounters = debris.map((object) => ({ object, encounter: calculateEncounter(satellite, object) })).sort((a, b) => b.encounter.riskScore - a.encounter.riskScore);
  return { objects, satellite, encounters };
}

function riskColor(risk) { return risk === "HIGH" ? "var(--red)" : risk === "MEDIUM" ? "var(--amber)" : "var(--green)"; }
function render(model) {
  const high = model.encounters.filter((item) => item.encounter.risk === "HIGH").length;
  const medium = model.encounters.filter((item) => item.encounter.risk === "MEDIUM").length;
  document.querySelector("#metrics").innerHTML = [
    ["Tracked objects", model.objects.length, "Synthetic catalog"],
    ["High-risk encounters", high, "Needs immediate review"],
    ["Closest approach", `${model.encounters[0].encounter.distance} km`, model.encounters[0].object.name],
    ["Risk horizon", "72 hrs", `${medium} medium-risk event${medium === 1 ? "" : "s"}`]
  ].map(([label, value, note]) => `<div class="metric"><div class="metric-label">${label}</div><div class="metric-value">${value}</div><div class="metric-note">${note}</div></div>`).join("");

  document.querySelector("#alertCount").textContent = `${model.encounters.length} events`;
  document.querySelector("#alerts").innerHTML = model.encounters.slice(0, 3).map(({ object, encounter }) => `<article class="alert-item"><div class="alert-top"><span>${object.name} <small>(${object.id})</small></span><span class="risk-${encounter.risk.toLowerCase()}">${encounter.risk}</span></div><p>Closest approach: <strong>${encounter.distance} km</strong> · TCA: <strong>${encounter.timeHours} hours</strong> · Relative speed: ${encounter.relativeSpeed} km/s</p></article>`).join("");

  document.querySelector("#objectTable").innerHTML = model.objects.map((object) => {
    const encounter = object.type === "debris" ? model.encounters.find((item) => item.object.id === object.id).encounter : null;
    return `<tr><td>${object.name}<br><small>${object.id}</small></td><td><span class="tag tag-${object.type}">${object.type}</span></td><td>${object.altitude} km</td><td>${encounter ? encounter.relativeSpeed + " km/s" : "—"}</td><td class="risk" style="color:${encounter ? riskColor(encounter.risk) : "var(--cyan)"}">${encounter ? encounter.risk + " · " + encounter.riskScore + "/100" : "MONITORED"}</td><td>${encounter ? encounter.timeHours + " hours" : "—"}</td></tr>`;
  }).join("");

  const map = document.querySelector("#orbitMap");
  const highestRisk = model.encounters[0].object;
  map.innerHTML = `<div class="earth"></div><span class="impact-zone" style="left:${highestRisk.x}%;top:${highestRisk.y}%" title="Synthetic proximity hazard zone"></span>` + model.objects.map((object) => `<span class="object-dot ${object.type}" style="left:${object.x}%;top:${object.y}%" data-label="${object.name}" title="${object.name} · ${object.altitude} km"></span>`).join("");
}

render(buildModel());
document.querySelector("#refreshButton").addEventListener("click", () => render(buildModel()));
