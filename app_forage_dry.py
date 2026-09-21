
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="Futtertrocknung: Luftfeuchte und Sättigungsdefizit",
    layout="wide",
)

st.markdown(
    """
    <style>
        .block-container {
            max-width: 1100px;
            margin-left: auto;
            margin-right: auto;
            padding-top: 2rem;
            padding-bottom: 3rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Futtertrocknung: Luftfeuchte und Sättigungsdefizit")

st.markdown(
    """
Diese App zeigt, wie viel Wasserdampf Luft bei einer gegebenen Temperatur aufnehmen kann
und wie gross das **Sättigungsdefizit** ist. Zusätzlich wird ein vereinfachter
Trocknungsverlauf von Futter berechnet.
"""
)

# -----------------------------
# Physikalische Funktionen
# -----------------------------

def saturation_vapor_pressure_hpa(T_c):
    """
    Sättigungsdampfdruck über Wasser nach Magnus.
    T in °C, Ergebnis in hPa.
    """
    return 6.112 * np.exp((17.62 * T_c) / (243.12 + T_c))


def absolute_humidity_g_m3(T_c, rh_percent):
    """
    Absolute Feuchte in g/m³.
    rho_v = 216.7 * e / T_K
    mit e in hPa.
    """
    e_s = saturation_vapor_pressure_hpa(T_c)
    e = (rh_percent / 100.0) * e_s
    return 216.7 * e / (T_c + 273.15)


def saturation_absolute_humidity_g_m3(T_c):
    return absolute_humidity_g_m3(T_c, 100.0)


def dew_point_c(T_c, rh_percent):
    """
    Taupunkt aus Magnus-Gleichung.
    """
    rh = np.clip(rh_percent, 0.1, 100.0)
    gamma = np.log(rh / 100.0) + (17.62 * T_c) / (243.12 + T_c)
    return 243.12 * gamma / (17.62 - gamma)


# -----------------------------
# Eingaben
# -----------------------------

st.sidebar.header("Luftzustand")

T = st.sidebar.slider(
    "Lufttemperatur [°C]",
    min_value=-5.0,
    max_value=40.0,
    value=20.0,
    step=0.5,
)

rh = st.sidebar.slider(
    "Relative Luftfeuchte [%]",
    min_value=10,
    max_value=100,
    value=60,
    step=1,
)


target_T = st.sidebar.slider(
    "Oberflächentemperatur des Futters [°C]",
    min_value=-5.0,
    max_value=40.0,
    value=12.0,
    step=0.5,
    help=(
        "Die Umgebungsluft hat die oben eingestellte Temperatur und relative Feuchte. "
        "Die Luft direkt an der Futteroberfläche wird auf die Oberflächentemperatur "
        "des Futters abgekühlt. Erreicht die Oberfläche den Taupunkt, kann Tau entstehen."
    ),
)

rho_sat = float(saturation_absolute_humidity_g_m3(T))
rho_actual = float(absolute_humidity_g_m3(T, rh))
deficit = rho_sat - rho_actual
dew_point = float(dew_point_c(T, rh))

target_rho_sat = float(saturation_absolute_humidity_g_m3(target_T))
target_rho = min(rho_actual, target_rho_sat)
target_rh = min(100.0, 100.0 * target_rho / target_rho_sat)
condensed_g_m3 = max(0.0, rho_actual - target_rho_sat)

# -----------------------------
# Kennwerte
# -----------------------------

st.subheader("1. Luftzustand")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Sättigungsfeuchte", f"{rho_sat:.1f} g/m³")
c2.metric("Absolute Feuchte", f"{rho_actual:.1f} g/m³")
c3.metric("Sättigungsdefizit", f"{deficit:.1f} g/m³")
c4.metric("Taupunkt", f"{dew_point:.1f} °C")

c5, c6, c7 = st.columns(3)
c5.metric("Futteroberfläche", f"{target_T:.1f} °C")
c6.metric("rF an der Oberfläche", f"{target_rh:.0f} %")
c7.metric("Kondensatpotenzial", f"{condensed_g_m3:.1f} g/m³")

st.caption(
    "Das Sättigungsdefizit ist hier als Differenz der absoluten Wasserdampfgehalte "
    "ρᵥ,sat − ρᵥ in g/m³ definiert."
)


st.caption(
    "Für Tau auf dem Futter ist nicht entscheidend, dass die gesamte Umgebungsluft "
    "auf den Taupunkt abkühlt. Entscheidend ist, dass die Futteroberfläche den "
    "Taupunkt der angrenzenden Luft erreicht oder unterschreitet."
)

# -----------------------------
# Grafik 1: Sättigungskurve
# -----------------------------

T_curve = np.linspace(-5, 40, 300)
rho_curve = saturation_absolute_humidity_g_m3(T_curve)

# Grenzschicht an der Futteroberfläche:
# Die Umgebungsluft wird an der kühleren Oberfläche abgekühlt.
# Bis zum Taupunkt bleibt der Wasserdampfgehalt näherungsweise konstant.
# Darunter kondensiert Wasser und der Zustand folgt der Sättigungskurve.
process_T = np.linspace(T, target_T, 160)
process_rho_sat = saturation_absolute_humidity_g_m3(process_T)
process_rho = np.minimum(rho_actual, process_rho_sat)


fig1 = go.Figure()

fig1.add_trace(
    go.Scatter(
        x=T_curve,
        y=rho_curve,
        mode="lines",
        name="Sättigung, rF = 100 %",
        line=dict(width=3),
    )
)

fig1.add_trace(
    go.Scatter(
        x=process_T,
        y=process_rho,
        mode="lines",
        name="Luft an der Futteroberfläche",
        line=dict(width=3, dash="dash"),
    )
)

fig1.add_trace(
    go.Scatter(
        x=[target_T],
        y=[target_rho],
        mode="markers",
        name="Zustand an der Futteroberfläche",
        marker=dict(size=11),
    )
)

fig1.add_vline(
    x=dew_point,
    line_dash="dot",
    annotation_text=f"Taupunkt {dew_point:.1f} °C",
    annotation_position="top",
)

fig1.add_trace(
    go.Scatter(
        x=[T],
        y=[rho_actual],
        mode="markers",
        name="Aktueller Luftzustand",
        marker=dict(size=12),
    )
)

fig1.add_trace(
    go.Scatter(
        x=[T, T],
        y=[rho_actual, rho_sat],
        mode="lines",
        name="Sättigungsdefizit",
        line=dict(dash="dot", width=3),
    )
)

fig1.add_hline(
    y=rho_actual,
    line_dash="dash",
    annotation_text=f"absolute Feuchte = {rho_actual:.1f} g/m³",
    annotation_position="bottom right",
)

fig1.update_layout(
    xaxis_title="Lufttemperatur [°C]",
    yaxis_title="Wasserdampfgehalt [g/m³]",
    legend_title="",
    margin=dict(l=55, r=85, t=20, b=55),
    height=500,
)

_, fig1_col, _ = st.columns([0.04, 0.92, 0.04])
with fig1_col:
    st.plotly_chart(fig1, use_container_width=True)

if target_T <= dew_point:
    st.info(
        f"Die Umgebungsluft hat **{T:.1f} °C** und **{rh:.0f} % rF**. "
        f"Ihr Taupunkt liegt bei **{dew_point:.1f} °C**. "
        f"Die Futteroberfläche ist mit **{target_T:.1f} °C** kälter als der Taupunkt. "
        f"Die Luft direkt an der Oberfläche erreicht daher **100 % rF** und Tau kann entstehen. "
        f"Das Kondensatpotenzial beträgt etwa **{condensed_g_m3:.1f} g/m³**."
    )
elif target_T < T:
    st.info(
        f"Die Umgebungsluft hat **{T:.1f} °C** und **{rh:.0f} % rF**. "
        f"Ihr Taupunkt liegt bei **{dew_point:.1f} °C**. "
        f"Die Futteroberfläche kühlt die angrenzende Luft auf **{target_T:.1f} °C** ab. "
        f"Dort steigt die relative Feuchtigkeit auf etwa **{target_rh:.0f} %**, "
        f"der Taupunkt wird aber noch nicht erreicht."
    )
else:
    st.info(
        f"Die Futteroberfläche ist mit **{target_T:.1f} °C** nicht kälter als die Umgebungsluft "
        f"(**{T:.1f} °C**). Durch nächtliche Oberflächenabkühlung ist unter diesen "
        f"Einstellungen keine Tauentstehung zu erwarten."
    )

with st.expander("Formeln"):
    st.latex(
        r"e_s(T)=6.112\cdot \exp\left(\frac{17.62\,T}{243.12+T}\right)"
    )
    st.latex(
        r"\rho_v = 216.7\cdot\frac{e}{T+273.15}"
    )
    st.latex(
        r"e=\frac{\mathrm{rF}}{100}\,e_s"
    )
    st.latex(
        r"\Delta\rho = \rho_{v,\mathrm{sat}}-\rho_v"
    )
    st.markdown(
        """
- T: Lufttemperatur in °C
- eₛ: Sättigungsdampfdruck in hPa
- e: aktueller Dampfdruck in hPa
- ρᵥ: absolute Feuchte in g/m³
- Δρ: Sättigungsdefizit in g/m³
"""
    )

# -----------------------------
# 2. Sättigungsdefizit-Summe
# -----------------------------

st.subheader("2. Sättigungsdefizit-Summe (SDS)")

st.write("Die SDS beschreibt das über die Zeit aufsummierte Sättigungsdefizit.")

st.latex(r"\mathrm{SDS}=\int SD(t)\,dt")

st.write("Bei konstanten Bedingungen gilt vereinfacht:")

st.latex(r"\mathrm{SDS}=SD\cdot \Delta t")

sds_presets = {
    "160 g/m³·h – Naturwiese, Referenz Belüftungsheu": 160.0,
    "180 g/m³·h – mittlerer Vergleichswert": 180.0,
    "200 g/m³·h – Kunstwiese, Referenz Belüftungsheu": 200.0,
}

sds_col1, sds_col2, sds_col3 = st.columns([1.8, 1, 1])

with sds_col1:
    sds_choice = st.selectbox(
        "SDS-Zielwert",
        options=list(sds_presets.keys()),
        index=1,
    )

sds_target = sds_presets[sds_choice]

if deficit > 1e-6:
    duration = sds_target / deficit
    duration_text = f"{duration:.1f} h"
    if duration >= 24:
        duration_text += f"  ({duration / 24:.1f} d)"
else:
    duration = 0.0
    duration_text = "nicht erreichbar"

sds_col2.metric("Aktuelles SD", f"{deficit:.2f} g/m³")
sds_col3.metric("Zeit bis SDS-Ziel", duration_text)

if deficit > 1e-6:
    st.caption(
        f"Berechnung: {sds_target:.0f} g/m³·h ÷ {deficit:.2f} g/m³ "
        f"= {duration:.1f} h"
    )

st.caption(
    "Annahme für die Zeitberechnung: Temperatur und relative Luftfeuchtigkeit bleiben konstant. "
    "Die Werte 160 und 200 g/m³·h stammen aus einem historischen Schweizer Feldversuch: "
    "Bis zum Belüftungsheu-Stadium mit etwa 60 % TS benötigte Naturwiesenfutter rund 160, "
    "Kunstwiesenfutter rund 200 SDS-Einheiten. 180 g/m³·h dient hier als Zwischenwert."
)

st.caption(
    "Die SDS beschreibt nur das luftseitige Trocknungspotenzial. "
    "Strahlung, Wind, Futtertemperatur und Schwadstruktur sind darin nicht enthalten. "
    "Deshalb kann derselbe Trocknungsgrad unter günstigen Bedingungen bei kleinerer SDS erreicht werden."
)

st.divider()

# -----------------------------
# 3. Vereinfachter Trocknungsverlauf
# -----------------------------

st.subheader("3. Vereinfachter Trocknungsverlauf")

st.markdown(
    """
Der Trocknungsverlauf startet fest bei **15 % TS**. Das Modell verbindet die
oben berechnete SDS mit der gewählten Trocknungsart.
"""
)

initial_dm = 15.0

drying_presets = {
    "Feldtrocknung, ungünstig": {
        "k": 0.107,
        "description": "Dichter Schwad, wenig Strahlung, wenig Wind oder feuchter Boden."
    },
    "Feldtrocknung, normal": {
        "k": 0.119,
        "description": "Mittlere Ablage, mässige Strahlung und Luftbewegung."
    },
    "Feldtrocknung, gut": {
        "k": 0.134,
        "description": "Breite, lockere Ablage, starke Strahlung und gute Luftbewegung."
    },
    "Belüftungstrocknung, Kaltluft": {
        "k": 0.145,
        "description": "Kontinuierliche Luftbewegung durch das Futter."
    },
    "Belüftungstrocknung, Warmluft / Entfeuchter": {
        "k": 0.180,
        "description": "Starke Luftbewegung und hohe Trocknungsleistung."
    },
}

ctrl1, ctrl2 = st.columns([1, 2])

ctrl1.metric("Startwert", "15 % TS")

with ctrl2:
    drying_mode = st.selectbox(
        "Trocknungsart",
        options=list(drying_presets.keys()),
        index=2,
    )

k0 = drying_presets[drying_mode]["k"]

st.caption(
    f"**{drying_mode}:** {drying_presets[drying_mode]['description']} "
    f"Der Faktor k₀ beschreibt vereinfacht, wie wirksam das vorhandene "
    f"luftseitige Trocknungspotenzial genutzt wird. Die drei Feldstufen sind "
    f"didaktisch so kalibriert, dass etwa 60 % TS bei ungefähr 200, 180 bzw. "
    f"160 g/m³·h erreicht werden."
)


with st.expander("Was bedeuten die drei Feldtrocknungsstufen?", expanded=False):
    field_conditions = pd.DataFrame(
        [
            {
                "Stufe": "Ungünstig",
                "Globalstrahlung*": "ca. 300 W/m²",
                "Wind*": "ca. 0.5 m/s",
                "Ablage*": "dichter Schwad, ~30 % Feldbedeckung",
                "Boden": "eher feucht",
                "Typische Situation": "bewölkt, wenig Luftbewegung, nach Niederschlag",
            },
            {
                "Stufe": "Normal",
                "Globalstrahlung*": "ca. 600 W/m²",
                "Wind*": "ca. 2 m/s",
                "Ablage*": "mittlere Ablage, ~60 % Feldbedeckung",
                "Boden": "mittel",
                "Typische Situation": "normaler trockener Sommertag",
            },
            {
                "Stufe": "Gut",
                "Globalstrahlung*": "ca. 800 W/m²",
                "Wind*": "ca. 3 m/s",
                "Ablage*": "breit und locker, ~80 % Feldbedeckung",
                "Boden": "eher trocken",
                "Typische Situation": "sonnig, trocken und windig; z. B. exponierte Berglage",
            },
        ]
    )
    st.dataframe(field_conditions, use_container_width=True, hide_index=True)

    st.caption(
        "* Orientierungswerte, keine festen Grenzwerte. "
        "Eine höhere Lage bedeutet nicht automatisch eine bessere Trocknung. "
        "Bei gleicher Lufttemperatur und relativer Feuchtigkeit ist das "
        "Sättigungsdefizit praktisch gleich. Günstig können in Berglagen "
        "stärkere Strahlung, mehr Wind und eine höhere Futteroberflächentemperatur sein."
    )

# Wassergehalt auf Trockenbasis: M = m_W / m_TS
m0_db = (100.0 - initial_dm) / initial_dm

# Referenz-Sättigungsdefizit 10 g/m³
lambda_eff = k0 * deficit / 10.0

def theoretical_time_to_ts(target_ts):
    """Theoretische Zeit bis zum Ziel-TS bei konstantem SD."""
    if lambda_eff <= 0:
        return np.inf
    m_target = (100.0 - target_ts) / target_ts
    return np.log(m0_db / m_target) / lambda_eff

t40_theory = theoretical_time_to_ts(40.0)
t60_theory = theoretical_time_to_ts(60.0)
t85_theory = theoretical_time_to_ts(85.0)

# Grafik immer mindestens bis 85 % TS anzeigen.
if np.isfinite(t85_theory):
    plot_duration = max(duration, 1.05 * t85_theory, 0.1)
else:
    plot_duration = max(duration, 24.0)

t = np.linspace(0, plot_duration, 500)
sds_t = deficit * t
m_db_t = m0_db * np.exp(-lambda_eff * t)
dm_t = 100.0 / (1.0 + m_db_t)

fig2 = go.Figure()

fig2.add_trace(
    go.Scatter(
        x=t,
        y=dm_t,
        mode="lines",
        name="TS-Gehalt",
        line=dict(width=3),
    )
)

for target, label in [
    (40, "40 % TS – Anwelksilage"),
    (60, "60 % TS – Belüftungsheu"),
    (85, "85 % TS – trockenes Heu"),
]:
    fig2.add_hline(
        y=target,
        line_dash="dot",
        annotation_text=label,
        annotation_position="right",
    )


if duration > 0:
    fig2.add_vline(
        x=duration,
        line_dash="dash",
        annotation_text=f"SDS-Ziel: {sds_target:.0f} g/m³·h",
        annotation_position="top",
    )

fig2.update_layout(
    xaxis_title="Zeit [h]",
    yaxis_title="TS-Gehalt [%]",
    yaxis_range=[0, 100],
    legend_title="",
    margin=dict(l=55, r=95, t=20, b=55),
    height=500,
)

_, fig2_col, _ = st.columns([0.04, 0.92, 0.04])
with fig2_col:
    st.plotly_chart(fig2, use_container_width=True)

# Zustand genau beim gewählten SDS-Ziel
m_db_at_sds = m0_db * np.exp(-lambda_eff * duration)
ts_at_sds = 100.0 / (1.0 + m_db_at_sds)

e1, e2, e3, e4 = st.columns(4)
e1.metric("TS beim SDS-Ziel", f"{ts_at_sds:.1f} %")
e2.metric("40 % TS", "∞" if not np.isfinite(t40_theory) else f"{t40_theory:.1f} h")
e3.metric("60 % TS", "∞" if not np.isfinite(t60_theory) else f"{t60_theory:.1f} h")
e4.metric("85 % TS", "∞" if not np.isfinite(t85_theory) else f"{t85_theory:.1f} h")

st.caption(
    "Die Zeiten sind theoretische Werte bei konstantem Sättigungsdefizit und "
    "unveränderter Trocknungsart. Die Grafik wird deshalb unabhängig vom gewählten "
    "SDS-Ziel bis mindestens 85 % TS weitergeführt."
)

st.caption(
    f"Effektive Trocknungskonstante: λ = {lambda_eff:.3f} 1/h "
    f"bei Δρ = {deficit:.1f} g/m³."
)

with st.expander("Trocknungsmodell"):
    st.write("Die SDS bis zu einem Zeitpunkt t ist:")

    st.latex(r"\mathrm{SDS}(t)=\int_0^t SD(\tau)\,d\tau")

    st.write("Die vereinfachte Trocknungskonstante lautet:")

    st.latex(r"\lambda = k_0\frac{SD}{10\ \mathrm{g\,m^{-3}}}")

    st.write("Der Wassergehalt auf Trockenbasis nimmt im Modell exponentiell ab:")

    st.latex(r"M(t)=M_0\,e^{-\lambda t}")

    st.write("Bei konstantem SD kann der Zusammenhang direkt über die SDS geschrieben werden:")

    st.latex(
        r"M(t)=M_0\exp\left[-k_0\frac{\mathrm{SDS}(t)}"
        r"{10\ \mathrm{g\,m^{-3}}}\right]"
    )

    st.markdown(
        """
M ist das Verhältnis Wassermasse zu Trockenmasse.

- **SDS:** Trocknungspotenzial der Luft über die Zeit.
- **k₀:** didaktischer Effizienzfaktor für Strahlung, Wind, Schwadstruktur und Belüftung.

Die Feldwerte von k₀ sind keine Literaturkonstanten. Sie sind hier so kalibriert,
dass das Modell die in der Vorlesung diskutierte Grössenordnung der SDS bis zum
Belüftungsheu-Stadium nachvollziehbar abbildet.
"""
    )

st.divider()
st.caption(
    "Sättigungsdampfdruck: Magnus-Formel. "
    "Für die Lehre geeignet im üblichen meteorologischen Temperaturbereich."
)
