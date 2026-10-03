"""Transparent screening model for plain-carbon steel.

QuenchIQ is an educational screening tool, not a substitute for an alloy-specific
TTT/CCT dataset or laboratory measurements. The model intentionally exposes its
assumptions so that users can distinguish established relationships from simplified
trend estimates.
"""

from dataclasses import dataclass
from math import exp, sqrt
from typing import Dict

A1_C = 727.0
EUTECTOID_CARBON = 0.76
# Straight-line Fe-C phase-diagram screening approximation from the eutectoid point
# (~0.76 wt%C, 727 °C) toward the Acm boundary near (~2.14 wt%C, 1147 °C).
ACM_SLOPE_C_PER_WT_C = (1147.0 - A1_C) / (2.14 - EUTECTOID_CARBON)
ROOM_TEMPERATURE_C = 25.0
KOISTINEN_MARBURGER_ALPHA = 0.011

MEDIUM_INFO = {
    "Brine": "Very severe quench; agitation and concentration strongly affect the actual heat-transfer rate.",
    "Water": "Severe quench; agitation, temperature and geometry strongly affect the actual rate.",
    "Oil": "Moderate quench; oil type and temperature can change the cooling curve substantially.",
    "Air": "Air cooling; the actual rate depends strongly on section size and airflow.",
    "Furnace": "Very slow cooling; commonly associated with annealing-style cooling.",
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
    """Approximate Ac3 for hypoeutectoid plain-carbon steel."""
    return 910.0 - 203.0 * sqrt(max(carbon, 0.0)) - 15.2 * carbon


def estimate_acm(carbon: float) -> float:
    """Approximate Acm screening temperature for hypereutectoid plain-carbon steel.

    This is a simple straight-line interpolation of the Fe-C diagram's Acm branch,
    not a grade-specific experimental transformation temperature.
    """
    return A1_C + ACM_SLOPE_C_PER_WT_C * (carbon - EUTECTOID_CARBON)


def critical_temperature(carbon: float) -> float:
    """Return the relevant upper critical boundary for austenitizing screening.

    Hypoeutectoid -> Ac3; eutectoid -> A1; hypereutectoid -> Acm.
    """
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
    """Estimate Ms with the carbon-only form of the Barbier relation.

    The full Barbier relation includes alloying-element terms; this interface
    supplies carbon only, so the unavailable terms are set to zero.
    """
    return 545.0 - 601.2 * (1.0 - exp(-0.868 * carbon))


def estimate_mf(ms: float) -> float:
    """Nominal educational Mf screening marker, not an exact material constant."""
    return ms - 215.0


def koistinen_marbürger_martensite(ms: float, final_temperature: float = ROOM_TEMPERATURE_C) -> float:
    """Estimate martensite fraction using K-M when final temperature is below Ms."""
    if final_temperature >= ms:
        return 0.0
    fraction = 1.0 - exp(-KOISTINEN_MARBURGER_ALPHA * (ms - final_temperature))
    return _clamp(fraction * 100.0, 0.0, 100.0)


def screening_nose(carbon: float, aust_temp: float) -> tuple[float, float, float]:
    """Return qualitative nose temperature, time and critical-rate marker."""
    nose_temp = 650.0 - 80.0 * carbon
    nose_time = 8.0 + 6.0 * carbon
    critical_rate = max(0.1, (aust_temp - nose_temp) / nose_time)
    return nose_temp, nose_time, critical_rate


def _screening_phase_fractions(inputs: SimulationInputs, ms: float, mf: float) -> Dict[str, float]:
    """Create a qualitative transformation-product estimate.

    This is not an experimental CCT calculation. Martensite is reserved using the
    K-M room-temperature estimate and a cooling-path bypass factor; remaining products
    are allocated qualitatively according to composition and cooling severity.
    """
    carbon = inputs.carbon
    rate = inputs.cooling_rate

    _nose_temp, _nose_time, critical_rate = screening_nose(carbon, inputs.aust_temp)
    rate_ratio = rate / critical_rate
    slow_factor = _clamp(1.0 - 0.55 * rate_ratio, 0.0, 1.0)
    bypass_factor = 1.0 / (1.0 + exp(-3.0 * (rate_ratio - 1.0)))

    km_martensite = koistinen_marbürger_martensite(ms)
    martensite = km_martensite * bypass_factor

    intermediate = exp(-((rate - 0.65 * critical_rate) / max(0.35 * critical_rate, 0.5)) ** 2)
    bainite = (100.0 - martensite) * 0.35 * intermediate
    remaining = max(0.0, 100.0 - martensite - bainite)

    if carbon < EUTECTOID_CARBON:
        ferrite_share = _clamp((EUTECTOID_CARBON - carbon) / (EUTECTOID_CARBON - 0.10), 0.0, 1.0)
        ferrite_share *= slow_factor
        ferrite = remaining * ferrite_share
        pearlite = remaining - ferrite
        cementite = 0.0
    else:
        cementite_share = _clamp((carbon - EUTECTOID_CARBON) / (1.40 - EUTECTOID_CARBON), 0.0, 1.0)
        cementite_share *= slow_factor
        cementite = remaining * cementite_share
        pearlite = remaining - cementite
        ferrite = 0.0

    return _normalize({
        "Martensite": martensite,
        "Bainite": bainite,
        "Pearlite": pearlite,
        "Ferrite": ferrite,
        "Cementite": cementite,
    })


def _hardness_estimate(carbon: float, phases: Dict[str, float], temper: bool, temper_temp: int) -> float:
    """Educational HRC trend estimate; not a grade-specific property model."""
    hardness = 18.0 + 23.0 * carbon + 0.30 * phases["Martensite"] + 0.12 * phases["Bainite"]
    hardness = _clamp(hardness, 15.0, 68.0)
    if temper:
        hardness -= 0.020 * max(0, temper_temp - 150)
    return _clamp(hardness, 15.0, 68.0)


def simulate(
    carbon: float,
    aust_temp: int,
    medium: str,
    cooling_rate: float,
    temper: bool = False,
    temper_temp: int = 350,
) -> dict:
    inputs = SimulationInputs(carbon, aust_temp, medium, cooling_rate, temper, temper_temp)
    inputs.validate()

    ms = estimate_ms(inputs.carbon)
    mf = estimate_mf(ms)
    phases = _screening_phase_fractions(inputs, ms, mf)
    hardness = _hardness_estimate(inputs.carbon, phases, inputs.temper, inputs.temper_temp)

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

    if primary_phase == "Martensite":
        explanation = "The selected cooling rate strongly favors martensitic transformation after the diffusional-transformation window is avoided."
    elif primary_phase == "Bainite":
        explanation = "The screening model places the cooling condition in an intermediate transformation range; the exact bainite fraction requires alloy-specific CCT data."
    elif primary_phase == "Ferrite":
        explanation = "For this hypoeutectoid composition and relatively slow cooling, proeutectoid ferrite is predicted alongside pearlite."
    elif primary_phase == "Cementite":
        explanation = "For this hypereutectoid composition and relatively slow cooling, proeutectoid cementite is predicted alongside pearlite."
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
        "medium_note": MEDIUM_INFO[inputs.medium],
        "km_martensite_room_temp": koistinen_marbürger_martensite(ms),
        "model_scope": "Plain-carbon steel screening model; no Mn/Si/Cr/Ni/Mo or alloy-specific TTT/CCT data supplied.",
    }
