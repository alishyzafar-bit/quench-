"""Grade library for QuenchIQ.

Composition values are representative mid-range values in wt% for educational
screening. They are not chemistry certificates; users should use certified
heat-analysis values for engineering work.
"""

GRADES = {
    "Custom plain-carbon": {"C": 0.45, "Mn": 0.75, "Si": 0.25, "Cr": 0.0, "Ni": 0.0, "Mo": 0.0, "V": 0.0, "Cu": 0.0, "W": 0.0, "Co": 0.0, "Al": 0.0, "P": 0.0, "S": 0.0, "family": "Plain-carbon steel", "note": "Editable screening chemistry."},
    "AISI 1045": {"C": 0.46, "Mn": 0.75, "Si": 0.25, "Cr": 0.0, "Ni": 0.0, "Mo": 0.0, "V": 0.0, "Cu": 0.0, "W": 0.0, "Co": 0.0, "Al": 0.0, "P": 0.0, "S": 0.0, "family": "Medium-carbon steel", "note": "Representative chemistry centered on common 1045 ranges."},
    "AISI 1080": {"C": 0.80, "Mn": 0.70, "Si": 0.25, "Cr": 0.0, "Ni": 0.0, "Mo": 0.0, "V": 0.0, "Cu": 0.0, "W": 0.0, "Co": 0.0, "Al": 0.0, "P": 0.0, "S": 0.0, "family": "High-carbon steel", "note": "Representative chemistry; verify the supplied heat certificate for a real part."},
    "AISI 4140": {"C": 0.405, "Mn": 0.875, "Si": 0.225, "Cr": 0.95, "Ni": 0.0, "Mo": 0.20, "V": 0.0, "Cu": 0.0, "W": 0.0, "Co": 0.0, "Al": 0.0, "P": 0.0, "S": 0.0, "family": "Cr-Mo alloy steel", "note": "Representative midpoint of common specification ranges."},
    "AISI 4340": {"C": 0.40, "Mn": 0.70, "Si": 0.25, "Cr": 0.80, "Ni": 1.80, "Mo": 0.25, "V": 0.0, "Cu": 0.0, "W": 0.0, "Co": 0.0, "Al": 0.0, "P": 0.0, "S": 0.0, "family": "Ni-Cr-Mo alloy steel", "note": "Representative chemistry; exact heat chemistry can shift transformation temperatures."},
    "AISI 52100": {"C": 1.00, "Mn": 0.35, "Si": 0.25, "Cr": 1.45, "Ni": 0.0, "Mo": 0.0, "V": 0.0, "Cu": 0.0, "W": 0.0, "Co": 0.0, "Al": 0.0, "P": 0.0, "S": 0.0, "family": "High-carbon chromium bearing steel", "note": "Representative chemistry; carbide state is not modeled explicitly."},
    "AISI 8620": {"C": 0.205, "Mn": 0.80, "Si": 0.25, "Cr": 0.50, "Ni": 0.55, "Mo": 0.20, "V": 0.0, "Cu": 0.0, "W": 0.0, "Co": 0.0, "Al": 0.0, "P": 0.0, "S": 0.0, "family": "Ni-Cr-Mo case-hardening steel", "note": "Base chemistry only; carburized-case behavior is not modeled."},
}

ELEMENTS = ["C", "Mn", "Si", "Cr", "Ni", "Mo", "V", "Cu", "W", "Co", "Al", "P", "S"]


def get_grade(name):
    return GRADES[name].copy()


def andrews_ms(c):
    """Andrews-style Ms estimate in °C.

    Ms = 539 - 423C - 30.4Mn - 17.7Ni - 12.1Cr - 7.5Mo
    This is an empirical screening relationship and is not universal.
    """
    return 539.0 - 423.0*c.get("C", 0) - 30.4*c.get("Mn", 0) - 17.7*c.get("Ni", 0) - 12.1*c.get("Cr", 0) - 7.5*c.get("Mo", 0)


def barbier_ms(c):
    """Alternative alloy-sensitive empirical Ms estimate, °C."""
    return (550.0 - 361.0*c.get("C", 0) - 39.0*c.get("Mn", 0) - 20.0*c.get("Cr", 0)
            - 17.0*c.get("Ni", 0) - 10.0*c.get("Cu", 0) - 5.0*(c.get("Mo", 0) + c.get("W", 0))
            - 35.0*c.get("V", 0) + 15.0*c.get("Co", 0) + 30.0*c.get("Al", 0))


def ms_estimates(c):
    return {"Andrews": andrews_ms(c), "Barbier": barbier_ms(c)}


def chemistry_summary(c):
    return "  ".join(f"{e} {c.get(e, 0):.3f}" for e in ELEMENTS if c.get(e, 0) > 0)
