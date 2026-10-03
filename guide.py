import streamlit as st


def render_guide():
    st.markdown("### Phase & heat-treatment guide")
    st.caption("A compact learning layer: what the terms mean, what the model uses, and where the model stops.")

    items = [
        ("Austenite (γ)", "The high-temperature FCC phase from which the cooling transformation is screened. QuenchIQ assumes an appropriate austenitized condition before cooling; the app does not model dissolution, homogenization or prior processing history."),
        ("Ferrite (α)", "A relatively soft BCC iron-rich phase. In hypoeutectoid plain-carbon steel, proeutectoid ferrite can form before pearlite during slower cooling."),
        ("Pearlite", "A lamellar ferrite–cementite transformation product formed by diffusional transformation. Lamellar spacing and morphology vary with transformation temperature; QuenchIQ does not resolve those features."),
        ("Bainite", "An intermediate transformation product formed over a temperature range between diffusional products and martensitic transformation. Its start/finish ranges and fraction are strongly alloy- and condition-dependent, so QuenchIQ treats bainite as a qualitative screening tendency."),
        ("Martensite", "A diffusionless transformation product formed as austenite cools below Ms. QuenchIQ uses a carbon-only empirical Ms estimate and a simplified cooling-path screening factor; actual behavior depends on composition, austenite condition and cooling history."),
        ("Cementite", "Iron carbide, Fe₃C. The simplified hypereutectoid branch allows proeutectoid cementite as a possible diffusional product; actual morphology and amount require alloy-specific transformation data."),
        ("Ms and Mf*", "Ms is the martensite-start temperature. QuenchIQ estimates Ms using a carbon-only form of an empirical Barbier relation because alloying elements are not entered. Mf* is deliberately marked as a screening marker, not an exact measured endpoint."),
        ("Ac1 / Ac3 / Acm", "A1 is the eutectoid critical temperature. Ac3 is the upper critical boundary for hypoeutectoid steel, while Acm is the corresponding screening boundary on the hypereutectoid side. QuenchIQ uses simplified Fe–C screening relationships, not grade-specific dilatometry."),
        ("Fe–Fe₃C vs TTT vs CCT", "The Fe–Fe₃C diagram describes equilibrium phase relationships. TTT describes transformation during isothermal holding. CCT describes transformation during continuous cooling. QuenchIQ's transformation plot is a schematic screening map, not an experimental CCT diagram."),
        ("Cooling condition", "Brine, water, oil, air and furnace cooling differ in heat-transfer severity, but a medium name does not uniquely determine a cooling curve. Geometry, section thickness, agitation, quenchant temperature and position all matter. In QuenchIQ, the entered cooling rate drives the numerical screening model."),
        ("Tempering", "Tempering changes the structure and properties of quenched steel. QuenchIQ represents tempering as a simplified property trend; it does not simulate tempering kinetics, carbide precipitation, retained austenite evolution or alloy-specific tempering reactions."),
    ]

    for title, body in items:
        with st.expander(title):
            st.write(body)

    st.markdown("### What QuenchIQ can do")
    st.markdown(
        """
        **Use it to explore trends, not certify a treatment.**

        - Compare the qualitative effect of carbon content and cooling rate in a plain-carbon steel screening model.
        - Explore Ac1/Ac3/Acm screening boundaries, estimated Ms and a nominal Mf* marker.
        - Visualize a selected cooling path against a schematic transformation map.
        - Compare saved runs and inspect how changing inputs alters the screening outputs.
        - Learn the relationship between composition, heat treatment, cooling and transformation products.
        """
    )

    st.markdown("### Model boundaries")
    st.markdown(
        """
        <div class="limit-card">
        <b>QuenchIQ is an educational screening model — not a production heat-treatment calculator.</b><br><br>
        The current model does <b>not</b> provide grade-specific predictions for:<br>
        • alloy steels with Mn, Si, Cr, Ni, Mo, V, W and other alloying additions<br>
        • experimental TTT/CCT curves or measured transformation kinetics<br>
        • real component cooling curves or heat-transfer coefficients<br>
        • section-size, geometry, agitation or quenchant-temperature effects<br>
        • prior-austenite grain size and detailed austenitizing history<br>
        • retained-austenite evolution<br>
        • detailed bainite, pearlite or carbide morphology/kinetics<br>
        • experimentally measured hardness, yield strength or tensile strength<br>
        • detailed tempering reactions and carbide precipitation
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Why real engineering data matters")
    st.info(
        "For an engineering heat-treatment decision, use the actual steel grade and validated grade-specific "
        "TTT/CCT data, process records and laboratory measurements. Useful validation methods include "
        "dilatometry, hardness testing and metallographic examination; tensile testing may be required when strength "
        "properties are part of the specification. QuenchIQ is designed to help explain the concepts behind those measurements."
    )

    st.markdown("### References & model basis")
    st.markdown(
        """
        **Core relationships and concepts**

        - **Koistinen–Marburger relationship:** used for the temperature-driven martensite estimate below Ms.
        - **Barbier empirical Ms relationship:** used in carbon-only form because the current interface does not accept alloying elements.
        - **Fe–C phase diagram:** used for approximate A1, Ac3 and Acm screening boundaries.
        - **TTT/CCT concepts:** used to frame the educational cooling-path screening map; the plotted curves are schematic.

        **Selected references**

        1. Koistinen, D.P. & Marburger, R.E. (1959), *A general equation prescribing the extent of the austenite-martensite transformation in pure iron-carbon alloys and plain carbon steels*, **Acta Metallurgica**, 7(1), 59–60. DOI: 10.1016/0001-6160(59)90170-1.
        2. Dossett, J.L. & Totten, G.E. (eds.) (2014), *ASM Handbook, Volume 4D: Heat Treating of Irons and Steels*, ASM International.
        3. Barbier empirical Ms relationship: used here in carbon-only form; the unavailable alloying-element terms are intentionally omitted.

        **Model status:** QuenchIQ combines established metallurgical relationships with transparent educational approximations. 
        Hardness, strength, phase allocation and Mf* are not certified or grade-specific values.
        """
    )
