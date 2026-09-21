
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

head_left, head_right = st.columns([4.2, 1.3])

with head_left:
    st.title("Futtertrocknung")
    st.caption("Physikalische Zusammenhänge von Luftfeuchte, Sättigungsdefizit, Tau und Trocknung.")

with head_right:
    with st.popover("ℹ️ Theorie & Annahmen", use_container_width=True):
        st.subheader("Luftzustand")
        st.latex(r"e_s(T)=6.112\cdot \exp\left(\frac{17.62\,T}{243.12+T}\right)")
        st.latex(r"\rho_v = 216.7\cdot\frac{e}{T+273.15}")
        st.latex(r"\Delta\rho = \rho_{v,\mathrm{sat}}-\rho_v")
        st.write(
            "Tau entsteht, wenn die Futteroberfläche den Taupunkt der angrenzenden Luft "
            "erreicht oder unterschreitet. Die gesamte Umgebungsluft muss dabei nicht "
            "auf den Taupunkt abkühlen."
        )

        st.divider()
        st.subheader("Sättigungsdefizit-Summe")
        st.latex(r"\mathrm{SDS}=\int SD(t)\,dt")
        st.write("Bei konstanten Bedingungen:")
        st.latex(r"\mathrm{SDS}=SD\cdot \Delta t")
        st.write(
            "Für die Zeitberechnung wird angenommen, dass Temperatur und relative "
            "Luftfeuchtigkeit konstant bleiben."
        )
        st.write(
            "Die Zielwerte 160 und 200 g/m³·h entsprechen historischen Schweizer "
            "Referenzwerten bis ungefähr zum Belüftungsheu-Stadium; 180 g/m³·h ist "
            "ein Zwischenwert für die Lehre."
        )

        st.divider()
        st.subheader("Vereinfachtes Trocknungsmodell")
        st.latex(r"\lambda = k_0\frac{SD}{10\ \mathrm{g\,m^{-3}}}")
        st.latex(r"M(t)=M_0\,e^{-\lambda t}")
        st.latex(
            r"M(t)=M_0\exp\left[-k_0\frac{\mathrm{SDS}(t)}"
            r"{10\ \mathrm{g\,m^{-3}}}\right]"
        )
        st.write(
            "M ist das Verhältnis Wassermasse zu Trockenmasse. k₀ ist hier ein "
            "didaktischer Effizienzfaktor für Strahlung, Wind, Schwadstruktur und "
            "technische Belüftung. Die k₀-Werte sind keine universellen Stoffkonstanten."
        )

        st.divider()
        st.subheader("Feldtrocknungsstufen")
        field_conditions = pd.DataFrame(
            [
                {
                    "Stufe": "Ungünstig",
                    "Strahlung": "≈ 300 W/m²",
                    "Wind": "≈ 0.5 m/s",
                    "Ablage": "dichter Schwad",
                    "Situation": "bewölkt, wenig Wind, feuchter Boden",
                },
                {
                    "Stufe": "Normal",
                    "Strahlung": "≈ 600 W/m²",
                    "Wind": "≈ 2 m/s",
                    "Ablage": "mittlere Ablage",
                    "Situation": "trockener Sommertag",
                },
                {
                    "Stufe": "Gut",
                    "Strahlung": "≈ 800 W/m²",
                    "Wind": "≈ 3 m/s",
                    "Ablage": "breit und locker",
                    "Situation": "sonnig, trocken, windig; z. B. exponierte Berglage",
                },
            ]
        )
        st.dataframe(field_conditions, use_container_width=True, hide_index=True)
        st.caption(
            "Orientierungswerte. Eine höhere Lage bedeutet nicht automatisch ein "
            "grösseres Sättigungsdefizit. Günstig wirken dort häufig Strahlung, Wind "
            "und die Erwärmung der Futteroberfläche."
        )

        st.divider()
        st.subheader("Modellgrenzen")
        st.write(
            "Die App ist ein didaktisches Modell und keine Wetter- oder Trocknungsprognose. "
            "Reale Verläufe werden zusätzlich durch wechselndes Wetter, Pflanzenart, "
            "Bestandesstruktur, Bodenfeuchte und Bearbeitung beeinflusst."
        )
        st.caption("Grundlagen: Magnus-Formel; Agroscope / Schweizer Lehrunterlagen zur SDS.")

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
    st.success(
        f"Tau möglich: Futteroberfläche {target_T:.1f} °C ≤ Taupunkt {dew_point:.1f} °C."
    )
elif target_T < T:
    st.caption(
        f"Kein Tau: An der Oberfläche steigt die rF auf etwa {target_rh:.0f} %, "
        f"der Taupunkt ({dew_point:.1f} °C) wird aber nicht erreicht."
    )
else:
    st.caption(
        "Die Futteroberfläche ist nicht kälter als die Umgebungsluft."
    )

# -----------------------------
# 2. Sättigungsdefizit-Summe
# -----------------------------

st.subheader("2. Sättigungsdefizit-Summe (SDS)")

st.caption("Aufsummiertes Trocknungspotenzial der Luft über die Zeit.")

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

st.divider()

# -----------------------------
# 3. Vereinfachter Trocknungsverlauf
# -----------------------------

st.subheader("3. Trocknungsverlauf")

st.caption("Start bei 15 % TS. Die Trocknungsart bestimmt, wie wirksam das Luftpotenzial genutzt wird.")

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

st.caption(f"{drying_presets[drying_mode]['description']}")

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

st.caption("Theoretische Zeiten bei konstantem SD und unveränderter Trocknungsart.")


