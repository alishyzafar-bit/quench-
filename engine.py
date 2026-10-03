"""Grade-aware educational heat-treatment screening model for QuenchIQ."""
from dataclasses import dataclass
from math import exp, sqrt
from typing import Dict, Optional
from grade_library import get_grade, andrews_ms, barbier_ms

A1_C=727.0; EUTECTOID_CARBON=0.76; ACM_SLOPE_C_PER_WT_C=(1147.0-A1_C)/(2.14-EUTECTOID_CARBON); ROOM_TEMPERATURE_C=25.0; KOISTINEN_MARBURGER_ALPHA=0.011
MEDIUM_INFO={"Brine":{"factor":1.55,"note":"Very severe screening condition; concentration, agitation and temperature can change the real cooling curve."},"Water":{"factor":1.25,"note":"Severe screening condition; agitation, temperature and geometry strongly affect the real rate."},"Oil":{"factor":0.75,"note":"Moderate screening condition; oil type, viscosity and temperature strongly affect the real rate."},"Air":{"factor":0.28,"note":"Gentle screening condition; section size and airflow dominate the real cooling rate."},"Furnace":{"factor":0.10,"note":"Very gentle screening condition; furnace schedule and part size determine the real curve."}}
MEDIUMS=tuple(MEDIUM_INFO)
@dataclass(frozen=True)
class SimulationInputs:
    carbon:float; aust_temp:int; medium:str; cooling_rate:float; temper:bool=False; temper_temp:int=350; grade:str="Custom plain-carbon"; composition:Optional[Dict[str,float]]=None
    def validate(self):
        if not .10<=self.carbon<=1.40: raise ValueError("Carbon content must be between 0.10 and 1.40 wt%.")
        if not 750<=self.aust_temp<=1100: raise ValueError("Austenitizing temperature must be between 750 and 1100 °C.")
        if self.medium not in MEDIUMS: raise ValueError(f"Unknown cooling medium: {self.medium}.")
        if not .5<=self.cooling_rate<=100: raise ValueError("Cooling rate must be between 0.5 and 100 °C/s.")
        if not 150<=self.temper_temp<=650: raise ValueError("Tempering temperature must be between 150 and 650 °C.")
def _clamp(v,lo,hi): return max(lo,min(hi,v))
def _normalize(values):
    cleaned={k:max(0.0,float(v)) for k,v in values.items()}; total=sum(cleaned.values()); return {k:v*100/total for k,v in cleaned.items()} if total else {k:0.0 for k in cleaned}
def eutectoid_class(c): return "Hypoeutectoid" if c<EUTECTOID_CARBON else ("Hypereutectoid" if c>EUTECTOID_CARBON else "Eutectoid")
def estimate_ac3(c): return 910.0-203.0*sqrt(max(c,0.0))-15.2*c
def estimate_acm(c): return A1_C+ACM_SLOPE_C_PER_WT_C*(c-EUTECTOID_CARBON)
def critical_temperature(c): return estimate_ac3(c) if eutectoid_class(c)=="Hypoeutectoid" else (estimate_acm(c) if eutectoid_class(c)=="Hypereutectoid" else A1_C)
def critical_boundary_label(c): return "Ac3" if eutectoid_class(c)=="Hypoeutectoid" else ("Acm" if eutectoid_class(c)=="Hypereutectoid" else "A1")
def estimate_ms(c): return 545.0-601.2*(1.0-exp(-0.868*c))
def estimate_mf(ms): return ms-215.0
def koistinen_marbürger_martensite(ms,final_temperature=ROOM_TEMPERATURE_C):
    if final_temperature>=ms:return 0.0
    return _clamp((1.0-exp(-KOISTINEN_MARBURGER_ALPHA*(ms-final_temperature)))*100,0,100)
def effective_cooling_rate(medium,base_rate): return base_rate*MEDIUM_INFO[medium]["factor"]
def screening_nose(carbon,aust_temp,medium="Water"):
    nose_temp=650.0-80.0*carbon; nose_time=8.0+6.0*carbon; critical_rate=max(.1,(aust_temp-nose_temp)/nose_time); return nose_temp,nose_time,critical_rate
def _screening_phase_fractions(inputs,ms):
    c=inputs.carbon; rate=effective_cooling_rate(inputs.medium,inputs.cooling_rate); nose_temp,nose_time,critical_rate=screening_nose(c,inputs.aust_temp,inputs.medium); ratio=rate/critical_rate; slow=_clamp(1-.55*ratio,0,1); bypass=1/(1+exp(-3*(ratio-1))); km=koistinen_marbürger_martensite(ms); mart=km*bypass; high_c=_clamp((c-.65)/.75,0,1); ra=max(0,100-km)*bypass*high_c*.55; bain=max(0,100-mart-ra)*.35*exp(-((rate-.65*critical_rate)/max(.35*critical_rate,.5))**2); remaining=max(0,100-mart-ra-bain)
    if c<EUTECTOID_CARBON: ferrite=remaining*_clamp((EUTECTOID_CARBON-c)/(EUTECTOID_CARBON-.10),0,1)*slow; pearlite=remaining-ferrite; cementite=0
    else: cementite=remaining*_clamp((c-EUTECTOID_CARBON)/(1.40-EUTECTOID_CARBON),0,1)*slow; pearlite=remaining-cementite; ferrite=0
    return _normalize({"Martensite":mart,"Bainite":bain,"Pearlite":pearlite,"Ferrite":ferrite,"Cementite":cementite,"Retained austenite":ra})
def _hardness_estimate(c,phases,temper,temper_temp):
    h=_clamp(18+23*c+.30*phases["Martensite"]+.12*phases["Bainite"],15,68)
    if temper:h-=.80*(max(0,temper_temp-150)/500)*max(0,h-18)
    return _clamp(h,15,68)
def simulate(carbon,aust_temp,medium,cooling_rate,temper=False,temper_temp=350,grade="Custom plain-carbon",composition=None):
    comp=(composition or get_grade(grade)).copy(); comp["C"]=carbon; inputs=SimulationInputs(carbon,aust_temp,medium,cooling_rate,temper,temper_temp,grade,comp); inputs.validate(); ms_a=andrews_ms(comp); ms_b=barbier_ms(comp); ms=.5*(ms_a+ms_b); mf=ms-215; phases=_screening_phase_fractions(inputs,ms); hardness=_hardness_estimate(carbon,phases,temper,temper_temp); tensile=max(300,420+19*hardness+120*carbon); tensile=max(300,tensile-.45*max(0,temper_temp-150)) if temper else tensile; yield=.82*tensile; primary=max(phases,key=phases.get); classification=eutectoid_class(carbon); critical=critical_temperature(carbon); boundary=critical_boundary_label(carbon); target=critical+20; effective=effective_cooling_rate(medium,cooling_rate); display="Tempered martensite" if temper and primary=="Martensite" else primary
    explanations={"Martensite":"The selected cooling condition strongly favors martensitic transformation after the diffusional-transformation window is bypassed.","Bainite":"The screening model places cooling in an intermediate transformation range; exact bainite behavior requires grade-specific CCT data.","Ferrite":"For this hypoeutectoid composition and relatively slow cooling, proeutectoid ferrite is predicted alongside pearlite.","Cementite":"For this hypereutectoid composition and relatively slow cooling, proeutectoid cementite is predicted alongside pearlite.","Retained austenite":"The screening model indicates that some austenite may remain untransformed at room temperature; this is sensitive to chemistry and cooling history.","Pearlite":"The screening model predicts pearlite as the dominant diffusional product."}
    return {"inputs":inputs,"phases":phases,"Ms":ms,"Mf":mf,"Ms_andrews":ms_a,"Ms_barbier":ms_b,"hardness":hardness,"tensile":tensile,"yield_strength":yield,"primary_phase":display,"phase_primary_key":primary,"classification":classification,"critical_temperature":critical,"critical_boundary":boundary,"aust_target":target,"aust_temp_ok":aust_temp>=target,"explanation":explanations[primary],"medium_note":MEDIUM_INFO[medium]["note"],"medium_factor":MEDIUM_INFO[medium]["factor"],"effective_cooling_rate":effective,"km_martensite_room_temp":koistinen_marbürger_martensite(ms),"composition":comp,"grade":grade,"model_scope":"Grade-aware educational screening: alloy-sensitive Ms estimates use Andrews and Barbier-style empirical relationships. Transformation kinetics, cooling curves and properties remain screening estimates; no grade-specific experimental CCT/TTT dataset is used yet."}
