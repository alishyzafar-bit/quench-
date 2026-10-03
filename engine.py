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

# Relative screening severities. These are NOT physical heat-transfer coefficients.
# They provide a transparent way to make the selected medium matter while the
# user-entered cooling rate remains the base process input.
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
        if not 0.10 <= self.carbon <= 1.40:
            raise ValueError("Carbon content must be between 0.10 and 1.40 wt%.")
        if not 750 <= self.aust_temp <= 1100:
            raise ValueError("Austenitizing temperature must be between 750 and 1100 °C.")
        if self.medium not in MEDIUMS:
            raise ValueError(f"Unknown cooling medium: {self.medium}.")
        if not 0.5 <= self.cooling_rate <= 100:
            raise ValueError("Cooling rate must be between 0.5 and 100 °C/s.")
        if not 150 <= self.temper_temp <= 650:
            raise ValueError("Tempering temperature must be between 150 and 650 °C.")


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _normalize(values: Dict[str, float]) -> Dict[str, float]:
    cleaned = {key: max(0.0, float(value)) for key, value in values.items()}
    total = sum(cleaned.values())
    if total <= 0:
        return {key: 0.0 for key in cleaned}
    return {key: value * 100.0 / total for key, value in cleaned.items()}


def eutectoid_class(carbon: float) -> str:
    if carbon < EUTECTOID_CARBON:
        return "Hypoeutectoid"
    if carbon > EUTECTOID_CARBON:
        return "Hypereutectoid"
    return "Eutectoid"


def estimate_ac3(carbon: float) -> float:
    return 910.0 - 203.0 * sqrt(max(carbon, 0.0)) - 15.2 * carbon


def estimate_acm(carbon: float) -> float:
    return A1_C + ACM_SLOPE_C_PER_WT_C * (carbon - EUTECTOID_CARBON)


def critical_temperature(carbon: float) -> float:
    classification = eutectoid_class(carbon)
    if classification == "Hypoeutectoid":
        return estimate_ac3(carbon)
    if classification == "Hypereutectoid":
        return estimate_acm(carbon)
    return A1_C


def critical_boundary_label(carbon: float) -> str:
    classification = eutectoid_class(carbon)
    if classification == "Hypoeutectoid":
        return "Ac3"
    if classification == "Hypereutectoid":
        return "Acm"
    return "A1"


def estimate_ms(carbon: float) -> float:
    """Carbon-only form of an empirical Barbier-style Ms relation."""
    return 545.0 - 601.2 * (1.0 - exp(-0.868 * carbon))


def estimate_mf(ms: float) -> float:
    return ms - 215.0


def koistinen_marbürger_martensite(ms: float, final_temperature: float = ROOM_TEMPERATURE_C) -> float:
    if final_temperature >= ms:
        return 0.0
    fraction = 1.0 - exp(-KOISTINEN_MARBURGER_ALPHA * (ms - final_temperature))
    return _clamp(fraction * 100.0, 0.0, 100.0)


def effective_cooling_rate(medium: str, base_rate: float) -> float:
    """Medium-adjusted screening rate; not a measured heat-transfer calculation."""
    return base_rate * MEDIUM_INFO[medium]["factor"]


def screening_nose(carbon: float, aust_temp: float, medium: str = "Water") -> tuple[float, float, float]:
    """Return qualitative nose temperature, time and critical-rate marker."""
    nose_temp = 650.0 - 80.0 * carbon
    nose_time = 8.0 + 6.0 * carbon
    critical_rate = max(0.1, (aust_temp - nose_temp) / nose_time)
    return nose_temp, nose_time, critical_rate


def _screening_phase_fractions(inputs: SimulationInputs, ms: float, mf: float) -> Dict[str, float]:
    carbon = inputs.carbon
    rate = effective_cooling_rate(inputs.medium, inputs.cooling_rate)
    _nose_temp, _nose_time, critical_rate = screening_nose(carbon, inputs.aust_temp, inputs.medium)
    rate_ratio = rate / critical_rate
    slow_factor = _clamp(1.0 - 0.55 * rate_ratio, 0.0, 1.0)
    bypass_factor = 1.0 / (1.0 + exp(-3.0 * (rate_ratio - 1.0)))

    km_martensite = koistinen_marbürger_martensite(ms)
    martensite = km_martensite * bypass_factor

    # Retained austenite is exposed only as a screening estimate where the
    # carbon level and rapid-cooling condition make incomplete K-M conversion relevant.
    high_carbon_factor = _clamp((carbon - 0.65) / 0.75, 0.0, 1.0)
    retained_austenite = max(0.0, 100.0 - km_martensite) * bypass_factor * high_carbon_factor * 0.55

    intermediate = exp(-((rate - 0.65 * critical_rate) / max(0.35 * critical_rate, 0.5)) ** 2)
    bainite = max(0.0, 100.0 - martensite - retained_austenite) * 0.35 * intermediate
    remaining = max(0.0, 100.0 - martensite - retained_austenite - bainite)

    if carbon < EUTECTOID_CARBON:
        ferrite_share = _clamp((EUTECTOID_CARBON - carbon) / (EUTECTOID_CARBON - 0.10), 0.0, 1.0) * slow_factor
        ferrite = remaining * ferrite_share
        pearlite = remaining - ferrite
        cementite = 0.0
    else:
        cementite_share = _clamp((carbon - EUTECTOID_CARBON) / (1.40 - EUTECTOID_CARBON), 0.0, 1.0) * slow_factor
        cementite = remaining * cementite_share
        pearlite = remaining - cementite
        ferrite = 0.0

    phases = {
        "Martensite": martensite,
        "Bainite": bainite,
        "Pearlite": pearlite,
        "Ferrite": ferrite,
        "Cementite": cementite,
        "Retained austenite": retained_austenite,
    }
    return _normalize(phases)


def _hardness_estimate(carbon: float, phases: Dict[str, float], temper: bool, temper_temp: int) -> float:
    hardness = 18.0 + 23.0 * carbon + 0.30 * phases["Martensite"] + 0.12 * phases["Bainite"]
    hardness = _clamp(hardness, 15.0, 68.0)
    if temper:
        # A deliberately broad educational tempering trend. It is not a grade-specific tempering curve.
        reduction = 0.80 * (max(0, temper_temp - 150) / 500.0) * max(0.0, hardness - 18.0)
        hardness -= reduction
    return _clamp(hardness, 15.0, 68.0)


def simulate(carbon: float, aust_temp: int, medium: str, cooling_rate: float, temper: bool = False, temper_temp: int = 350) -> dict:
    inputs = SimulationInputs(carbon, aust_temp, medium, cooling_rate, temper, temper_temp)
    inputs.validate()

    ms = estimate_ms(inputs.carbon)
    mf = estimate_mf(ms)
    phases = _screening_phase_fractions(inputs, ms, mf)
    hardness = _hardness_estimate(inputs.carbon, phases, inputs.temper, inputs.temper_temp)

    if inputs.temper and phases["Martensite"] > 0:
        phases["Tempered martensite"] = phases.pop("Martensite")
        phases = _normalize(phases)

    tensile = max(300.0, 420.0 + 19.0 * hardness + 120.0 * inputs.carbon)
    if inputs.temper:
        tensile = max(300.0, tensile - 0.45 * max(0, inputs.temper_temp - 150))
    yield_strength = 0.82 * tensile

    primary_phase = max(phases, key=phases.get)
    classification = eutectoid_class(inputs.carbon)
    critical = critical_temperature(inputs.carbon)
    boundary = critical_boundary_label(inputs.carbon)
    aust_target = critical + 20.0
    aust_ok = inputs.aust_temp >= aust_target
    effective_rate = effective_cooling_rate(inputs.medium, inputs.cooling_rate)

    if primary_phase in ("Martensite", "Tempered martensite"):
        explanation = "The selected cooling condition strongly favors martensitic transformation after the diffusional-transformation window is bypassed."
    elif primary_phase == "Bainite":
        explanation = "The screening model places the cooling condition in an intermediate transformation range; exact bainite behavior requires alloy-specific CCT data."
    elif primary_phase == "Ferrite":
        explanation = "For this hypoeutectoid composition and relatively slow cooling, proeutectoid ferrite is predicted alongside pearlite."
    elif primary_phase == "Cementite":
        explanation = "For this hypereutectoid composition and relatively slow cooling, proeutectoid cementite is predicted alongside pearlite."
    elif primary_phase == "Retained austenite":
        explanation = "The screening model indicates that some austenite may remain untransformed at room temperature; the estimate is especially sensitive to carbon and cooling history."
    else:
        explanation = "The screening model predicts pearlite as the dominant diffusional product."

    return {
        "inputs": inputs,
        "phases": phases,
        "Ms": ms,
        "Mf": mf,
        "hardness": hardness,
        "tensile": tensile,
        "yield_strength": yield_strength,
        "primary_phase": primary_phase,
        "classification": classification,
        "critical_temperature": critical,
        "critical_boundary": boundary,
        "aust_target": aust_target,
        "aust_temp_ok": aust_ok,
        "explanation": explanation,
        "medium_note": MEDIUM_INFO[inputs.medium]["note"],
        "medium_factor": MEDIUM_INFO[inputs.medium]["factor"],
        "effective_cooling_rate": effective_rate,
        "km_martensite_room_temp": koistinen_marbürger_martensite(ms),
        "model_scope": "Plain-carbon steel screening model; no alloy-specific TTT/CCT data or measured heat-transfer curve supplied.",
    }
