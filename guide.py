import streamlit as st


def render_guide():
    st.markdown("### Phase & heat-treatment guide")
    st.caption("Definitions and model notes so a first-time user can understand what each result means.")

    items = [
        ("Austenite (γ)", "The high-temperature FCC phase from which the transformation products are predicted. QuenchIQ assumes the material has reached an appropriate austenitized condition before the cooling path begins."),
        ("Ferrite (α)", "A relatively soft BCC iron-rich phase. In hypoeutectoid plain-carbon steel, ferrite can form before pearlite during slower cooling."),
        ("Pearlite", "A lamellar ferrite–cementite transformation product formed by diffusional transformation. Its morphology and spacing change with transformation temperature."),
        ("Bainite", "A non-equilibrium transformation product that forms in an intermediate temperature range. Its exact formation range and amount are strongly alloy-dependent, so QuenchIQ treats it as a qualitative tendency rather than a measured fraction."),
        ("Martensite", "A diffusionless transformation product formed when austenite is cooled below Ms. Its amount can be estimated with the Koistinen–Marburger relationship, but real behavior depends on composition and conditions."),
        ("Cementite", "Iron carbide, Fe₃C. In the simplified hypereutectoid branch, QuenchIQ includes proeutectoid cementite as a possible diffusional product."),
        ("Ms and Mf", "Ms is the martensite-start temperature. QuenchIQ estimates Ms from a published empirical carbon-dependent relation. Mf is more composition- and condition-dependent, so QuenchIQ marks Mf* as a nominal screening value rather than an exact measured temperature."),
        ("TTT vs CCT", "TTT describes transformation during isothermal holding. CCT describes transformation during continuous cooling. A true CCT diagram must be specific to the alloy and test condition."),
        ("Quenching medium", "Brine, water, oil, air and furnace cooling have different heat-transfer behavior, but a medium name alone does not uniquely determine the cooling curve. Agitation, temperature, geometry and section thickness matter."),
        ("Tempering", "A post-quench heat treatment used to alter the properties and structure of martensitic steel. The exact response depends on carbon/alloy chemistry and tempering time and temperature."),
    ]

    for title, body in items:
        with st.expander(title):
            st.write(body)

    st.markdown("### References & model basis")
    st.markdown(
        """
        **Core relationships used by QuenchIQ**

        - **Koistinen–Marburger relationship:** used for the temperature-driven martensite estimate below Ms.
        - **Barbier empirical Ms relationship:** used in carbon-only form because the current interface does not accept alloying elements.
        - **Fe–C phase diagram:** used for approximate A1, Ac3 and Acm screening boundaries.
        - **TTT/CCT transformation concepts:** used to frame the cooling-path screening model; the plotted curves are schematic, not experimental.

        **Selected references**

        1. Koistinen, D.P. & Marburger, R.E. (1959), *A general equation prescribing the extent of the austenite-martensite transformation in pure iron-carbon alloys and plain carbon steels*, **Acta Metallurgica**, 7(1), 59–60. DOI: 10.1016/0001-6160(59)90170-1.
        2. Dossett, J.L. & Totten, G.E. (eds.) (2014), *ASM Handbook, Volume 4D: Heat Treating of Irons and Steels*, ASM International.
        3. Barbier empirical Ms relationship: used in carbon-only form in this app; alloying-element terms require additional chemistry inputs.

        **Model status:** the app combines established relationships with transparent educational approximations.
        Hardness, strength, phase allocation and Mf* should not be treated as certified or grade-specific values.
        """
    )

    st.markdown("### What the graph means")
    st.info(
        "The transformation graph in this version is a CCT-style educational screening map. "
        "It is deliberately not presented as an experimental CCT diagram because no steel grade, "
        "alloy chemistry or measured transformation dataset is supplied by the user."
    )

    st.markdown("### What the app does not claim")
    st.markdown(
        "- It does not replace a grade-specific TTT/CCT diagram.\n"
        "- It does not calculate heat-transfer coefficients from a real component.\n"
        "- It does not certify hardness or tensile strength.\n"
        "- It does not account for every alloying element.\n"
        "- It does not replace metallography, dilatometry or laboratory testing."
    )
