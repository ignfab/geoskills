# Helicopter handoff

Use this reference when the request links an elevation screen to helicopter landing.
The workflow answers “which mapped terrain cells satisfy these supplied criteria?”
It does not answer whether an aircraft can land there.

## Interpret the criteria

Confirm the AOI and meaning of height. An altitude ceiling, maximum local height difference,
obstacle clearance and height above ground are different quantities. Obtain the actual
numeric terrain criteria from the user/operator and keep their units and height reference.
Do not invent a universal maximum slope, landing-pad diameter, obstacle buffer or aircraft
performance limit. If only altitude is supplied, produce only that screen and identify the
unassessed criteria. Missing operational criteria do not prevent a clearly labelled
altitude-only GIS result.

## Explain the remaining assessment

- **Footprint:** connected area does not prove that the required shape/width fits. A narrow
  strip, holes or a sloping patch may pass an area test. Any requested footprint test needs
  supplied dimensions and orientation rules and must stay within the valid candidate area.
- **Obstacles and surface:** a bare-earth DEM does not establish clearance from wires,
  trees, poles, buildings or temporary objects, nor ground bearing capacity or condition.
  Current imagery, inventories and site inspection are separate evidence; an absent map
  feature is not evidence of an obstacle-free site.
- **Operations:** approaches/departures, weather/wind, aircraft configuration and performance,
  access and permissions require current site and operator assessment. Do not infer their
  validity from terrain altitude, a slope map or a geographic overlay.

Include these limitations in the delivery in proportion to the request. Use “candidate
terrain under the stated raster criteria” in the report/map. List applied filters and
unknown coverage, then identify remaining checks for the qualified pilot/operator.
Do not issue a landing clearance or a safe/suitable-site conclusion. For specific
operational or regulatory questions, consult current authoritative aviation sources;
this skill contains no flight procedure or jurisdiction-specific authorization rules.
