"""Transparent educational screening model for plain-carbon steel.

QuenchIQ is an educational screening tool, not a substitute for alloy-specific
TTT/CCT data or laboratory measurements. Medium effects, phase fractions,
hardness and strength are deliberately presented as screening estimates.
"""

from dataclasses import dataclass
from math import exp, sqrt
from typing import Dict

A1_C = 727.0
EUTECTOID_CARBON = 0.76
ACM_SLOPE_C_PER_WT_C = (1147.0 - A1_C) / (2.14 - EUTECTOID_CARBON)
ROOM_TEMPERATURE_C = 25.0
KOISTINEN_MARBURGER_ALPHA = 0.011

MEDIUM_INFO = {
    "Brine": {"factor": 1.55, "note": "Very severe screening condition; concentration, agitation and temperature can change the real cooling curve."},
    "Water": {"factor": 1.25, "note": "Severe screening condition; agitation, temperature and geometry strongly affect the real rate."},
    "Oil": {"factor": 0.75, "note": "Moderate screening condition; oil type, viscosity and temperature strongly affect the real rate."},
    "Air": {"factor": 0.28, "note": "Gentle screening condition; section size and airflow dominate the real cooling rate."},
    "Furnace": {"factor": 0.10, "note": "Very gentle screening condition; furnace schedule and part size determine the real curve."},
}
MEDIUMS = tuple(MEDIUM_INFO)

@dataclass(frozen=True)
class SimulationInputs:
    carbon: float
    aust_temp: int
    medium: str
    cooling_rate: float
    temper: bool = False
    temper_temp: int = 350

    def validate(self) -> None:
        if not 0.10 <= self.carbon <= 1.40: raise ValueError("Carbon content must be between 0.10 and 1.40 wt%.")
        if not 750 <= self.aust_temp <= 1100: raise ValueError("Austenitizing temperature must be between 750 and 1100 °C.")
        if self.medium not in MEDIUMS: raise ValueError(f"Unknown cooling medium: {self.medium}.")
        if not 0.5 <= self.cooling_rate <= 100: raise ValueError("Cooling rate must be between 0.5 and 100 °C/s.")
        if not 150 <= self.temper_temp <= 650: raise ValueError("Tempering temperature must be between 150 and 650 °C.")

def _clamp(value, low, high): return max(low, min(high, value))

def _normalize(values: Dict[str, float]) -> Dict[str, float]:
    cleaned = {key: max(0.0, float(value)) for key, value in values.items()}
    total = sum(cleaned.values())
    return {key: value * 100.0 / total for key, value in cleaned.items()} if total > 0 else {key: 0.0 for key in cleaned}

def eutectoid_class(carbon):
    return "Hypoeutectoid" if carbon < EUTECTOID_CARBON else ("Hypereutectoid" if carbon > EUTECTOID_CARBON else "Eutectoid")

def estimate_ac3(carbon): return 910.0 - 203.0 * sqrt(max(carbon, 0.0)) - 15.2 * carbon

def estimate_acm(carbon): return A1_C + ACM_SLOPE_C_PER_WT_C * (carbon - EUTECTOID_CARBON)

def critical_temperature(carbon):
    cls = eutectoid_class(carbon)
    return estimate_ac3(carbon) if cls == "Hypoeutectoid" else (estimate_acm(carbon) if cls == "Hypereutectoid" else A1_C)

def critical_boundary_label(carbon):
    cls = eutectoid_class(carbon)
    return "Ac3" if cls == "Hypoeutectoid" else ("Acm" if cls == "Hypereutectoid" else "A1")

def estimate_ms(carbon): return 545.0 - 601.2 * (1.0 - exp(-0.868 * carbon))
def estimate_mf(ms): return ms - 215.0

def koistinen_marbürger_martensite(ms, final_temperature=ROOM_TEMPERATURE_C):
    if final_temperature >= ms: return 0.0
    return _clamp((1.0 - exp(-KOISTINEN_MARBURGER_ALPHA * (ms - final_temperature))) * 100.0, 0.0, 100.0)

def effective_cooling_rate(medium, base_rate): return base_rate * MEDIUM_INFO[medium]["factor"]

def screening_nose(carbon, aust_temp, medium="Water"):
    nose_temp = 650.0 - 80.0 * carbon
    nose_time = 8.0 + 6.0 * carbon
    critical_rate = max(0.1, (aust_temp - nose_temp) / nose_time)
    return nose_temp, nose_time, critical_rate

def _screening_phase_fractions(inputs, ms, mf):
    carbon = inputs.carbon
    rate = effective_cooling_rate(inputs.medium, inputs.cooling_rate)
    nose_temp, nose_time, critical_rate = screening_nose(carbon, inputs.aust_temp, inputs.medium)
    rate_ratio = rate / critical_rate
    slow_factor = _clamp(1.0 - 0.55 * rate_ratio, 0.0, 1.0)
    bypass_factor = 1.0 / (1.0 + exp(-3.0 * (rate_ratio - 1.0)))
    km_martensite = koistinen_marbürger_martensite(ms)
    martensite = km_martensite * bypass_factor
    high_carbon_factor = _clamp((carbon - 0.65) / 0.75, 0.0, 1.0)
    retained_austenite = max(0.0, 100.0 - km_martensite) * bypass_factor * high_carbon_factor * 0.55
    intermediate = exp(-((rate - 0.65 * critical_rate) / max(0.35 * critical_rate, 0.5)) ** 2)
    bainite = max(0.0, 100.0 - martensite - retained_austenite) * 0.35 * intermediate
    remaining = max(0.0, 100.0 - martensite - retained_austenite - bainite)
    if carbon < EUTECTOID_CARBON:
        ferrite = remaining * _clamp((EUTECTOID_CARBON - carbon) / (EUTECTOID_CARBON - 0.10), 0.0, 1.0) * slow_factor
        pearlite, cementite = remaining - ferrite, 0.0
    else:
        cementite = remaining * _clamp((carbon - EUTECTOID_CARBON) / (1.40 - EUTECTOID_CARBON), 0.0, 1.0) * slow_factor
        pearlite, ferrite = remaining - cementite, 0.0
    return _normalize({"Martensite": martensite, "Bainite": bainite, "Pearlite": pearlite, "Ferrite": ferrite, "Cementite": cementite, "Retained austenite": retained_austenite})

def _hardness_estimate(carbon, phases, temper, temper_temp):
    hardness = _clamp(18.0 + 23.0 * carbon + 0.30 * phases["Martensite"] + 0.12 * phases["Bainite"], 15.0, 68.0)
    if temper:
        hardness -= 0.80 * (max(0, temper_temp - 150) / 500.0) * max(0.0, hardness - 18.0)
    return _clamp(hardness, 15.0, 68.0)

def simulate(carbon, aust_temp, medium, cooling_rate, temper=False, temper_temp=350):
    inputs = SimulationInputs(carbon, aust_temp, medium, cooling_rate, temper, temper_temp)
    inputs.validate()
    ms, mf = estimate_ms(inputs.carbon), estimate_mf(estimate_ms(inputs.carbon))
    phases = _screening_phase_fractions(inputs, ms, mf)
    hardness = _hardness_estimate(inputs.carbon, phases, inputs.temper, inputs.temper_temp)
    tensile = max(300.0, 420.0 + 19.0 * hardness + 120.0 * inputs.carbon)
    if inputs.temper: tensile = max(300.0, tensile - 0.45 * max(0, inputs.temper_temp - 150))
    yield_strength = 0.82 * tensile
    primary_phase = max(phases, key=phases.get)
    classification = eutectoid_class(inputs.carbon)
    critical = critical_temperature(inputs.carbon)
    boundary = critical_boundary_label(inputs.carbon)
    aust_target = critical + 20.0
    aust_ok = inputs.aust_temp >= aust_target
    effective_rate = effective_cooling_rate(inputs.medium, inputs.cooling_rate)
    display_primary = "Tempered martensite" if inputs.temper and primary_phase == "Martensite" else primary_phase
    if display_primary in ("Martensite", "Tempered martensite"):
        explanation = "The selected cooling condition strongly favors martensitic transformation after the diffusional-transformation window is bypassed."
    elif primary_phase == "Bainite": explanation = "The screening model places the cooling condition in an intermediate transformation range; exact bainite behavior requires alloy-specific CCT data."
    elif primary_phase == "Ferrite": explanation = "For this hypoeutectoid composition and relatively slow cooling, proeutectoid ferrite is predicted alongside pearlite."
    elif primary_phase == "Cementite": explanation = "For this hypereutectoid composition and relatively slow cooling, proeutectoid cementite is predicted alongside pearlite."
    elif primary_phase == "Retained austenite": explanation = "The screening model indicates that some austenite may remain untransformed at room temperature; the estimate is especially sensitive to carbon and cooling history."
    else: explanation = "The screening model predicts pearlite as the dominant diffusional product."
    return {"inputs": inputs, "phases": phases, "Ms": ms, "Mf": mf, "hardness": hardness, "tensile": tensile, "yield_strength": yield_strength, "primary_phase": display_primary, "phase_primary_key": primary_phase, "classification": classification, "critical_temperature": critical, "critical_boundary": boundary, "aust_target": aust_target, "aust_temp_ok": aust_ok, "explanation": explanation, "medium_note": MEDIUM_INFO[inputs.medium]["note"], "medium_factor": MEDIUM_INFO[inputs.medium]["factor"], "effective_cooling_rate": effective_rate, "km_martensite_room_temp": koistinen_marbürger_martensite(ms), "model_scope": "Plain-carbon steel screening model; no alloy-specific TTT/CCT data or measured heat-transfer curve supplied."}
