# QuenchIQ 2.1

QuenchIQ is a Streamlit educational simulator for exploring heat-treatment concepts in **plain-carbon steel**.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Project structure

```text
QuenchIQ_2_0/
├── app.py                    # Streamlit interface
├── requirements.txt          # Python dependencies
├── .streamlit/config.toml    # App theme and server settings
├── simulation/
│   └── engine.py             # Validated calculation model
├── components/
│   ├── charts.py             # Plotly visualizations
│   └── theme.py              # Dashboard styling
└── views/
    ├── guide.py              # Learning/reference content
    └── logbook.py            # Saved-run table and CSV export
```

## Scientific scope

The app intentionally avoids pretending that a generic formula can reproduce a real alloy's CCT diagram.

The current model:

- classifies plain-carbon steel around the approximate 0.76 wt% eutectoid composition;
- uses Ac3/A1/Acm screening boundaries for hypoeutectoid/eutectoid/hypereutectoid steel;
- estimates Ms with a carbon-only form of the Barbier empirical relation;
- estimates room-temperature martensite using the Koistinen–Marburger relationship;
- allocates the remaining transformation products with a transparent qualitative screening model;
- provides clearly labelled trend-only hardness and strength estimates;
- draws a **schematic CCT-style screening map**, not an experimental grade-specific CCT diagram;
- provides saved-run comparison and a live “what changed” cue for learning.

The literature basis includes the Koistinen–Marburger martensite relationship and the Barbier Ms relation. ASM Handbook material is used as a general heat-treatment reference. CCT/TTT behavior remains alloy- and process-specific.

## Important limitations

The app does **not** contain:

- Mn, Si, Cr, Ni, Mo or other alloying chemistry;
- grade-specific measured TTT/CCT datasets;
- section-size heat-transfer calculations;
- agitation-dependent heat-transfer coefficients;
- prior-austenite grain-size effects;
- dilatometry/metallography calibration;
- certified hardness or tensile-property databases.

Therefore, the numerical phase fractions, hardness and strength are educational estimates only.

For engineering design or an actual heat-treatment recipe, use the measured/validated data for the exact steel grade and component.

## Validation performed during this build

- Python AST/syntax validation for every project module.
- `compileall` validation.
- Phase fractions verified to total 100% across edge cases.
- Ms > Mf* checked across the supported carbon range.
- Tempering direction checked so the simplified model does not increase hardness when tempering temperature rises.
- Cooling-rate trend checked so faster cooling does not reduce the model's martensite fraction.
- Plotly phase-chart and transformation-chart smoke tests performed at several cooling rates.
- Duplicate Plotly layout arguments fixed after chart testing exposed the issue.

## Selected references

1. Koistinen, D.P. & Marburger, R.E. (1959), *A general equation prescribing the extent of the austenite-martensite transformation in pure iron-carbon alloys and plain carbon steels*, Acta Metallurgica, 7(1), 59–60. DOI: 10.1016/0001-6160(59)90170-1.
2. Dossett, J.L. & Totten, G.E. (eds.) (2014), *ASM Handbook, Volume 4D: Heat Treating of Irons and Steels*, ASM International.
3. Barbier empirical Ms relationship: implemented in carbon-only form because the current interface does not accept alloying-element chemistry.
