import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st


# -----------------------------
# Page setup
# -----------------------------

st.set_page_config(
    page_title="Futtertrocknung / Séchage des herbages",
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

        .stTabs [data-baseweb="tab-list"] {
            gap: 0.8rem;
        }

        .stTabs [data-baseweb="tab"] {
            height: 3.4rem;
            padding-left: 1.4rem;
            padding-right: 1.4rem;
        }

        .stTabs [data-baseweb="tab"] p {
            font-size: 1.15rem;
            font-weight: 600;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# -----------------------------
# Language texts
# -----------------------------

TXT = {
    "DE": {
        "title": "Futtertrocknung",
        "subtitle": (
            "Physikalische Zusammenhänge von Luftfeuchte, "
            "Sättigungsdefizit, Tau und Trocknung."
        ),
        "theory_button": "ℹ️ Theorie & Annahmen",
        "air_state": "Luftzustand",
        "dew_text": (
            "Tau entsteht, wenn die Futteroberfläche den Taupunkt der angrenzenden Luft "
            "erreicht oder unterschreitet. Die gesamte Umgebungsluft muss dabei nicht "
            "auf den Taupunkt abkühlen."
        ),
        "sds_title": "Sättigungsdefizitsumme",
        "constant_conditions": "Bei konstanten Bedingungen:",
        "sds_explanation": (
            "Die SDS beschreibt das aus Temperatur und Luftfeuchtigkeit "
            "abgeleitete kumulierte Trocknungspotenzial. "
            "Strahlung und Wind werden dabei nicht vollständig erfasst."
        ),
        "time_assumption": (
            "Für die Zeitberechnung wird angenommen, dass Temperatur und relative "
            "Luftfeuchtigkeit konstant bleiben."
        ),
        "sds_refs": (
            "Die Zielwerte 160 und 200 g/m³·h entsprechen historischen Schweizer "
            "Referenzwerten bis ungefähr zum Belüftungsheu-Stadium; 180 g/m³·h ist "
            "ein Zwischenwert für die Lehre."
        ),
        "model_title": "Vereinfachtes Trocknungsmodell",
        "model_text": (
            "M ist das Verhältnis Wassermasse zu Trockenmasse. k₀ ist hier ein "
            "didaktischer Effizienzfaktor für Strahlung, Wind und Schwadstruktur. "
            "Die k₀-Werte sind keine universellen Stoffkonstanten."
        ),
        "field_title": "Feldtrocknungsstufen",
        "field_columns": {
            "level": "Stufe",
            "radiation": "Strahlung",
            "wind": "Wind",
            "swath": "Ablage",
            "situation": "Situation",
        },
        "field_rows": [
            {
                "level": "Ungünstig",
                "radiation": "≈ 300 W/m²",
                "wind": "≈ 0.5 m/s",
                "swath": "dichter Schwad",
                "situation": "bewölkt, wenig Wind, feuchter Boden",
            },
            {
                "level": "Normal",
                "radiation": "≈ 600 W/m²",
                "wind": "≈ 2 m/s",
                "swath": "mittlere Ablage",
                "situation": "trockener Sommertag",
            },
            {
                "level": "Gut",
                "radiation": "≈ 800 W/m²",
                "wind": "≈ 3 m/s",
                "swath": "breit und locker",
                "situation": "sonnig, trocken, windig; z. B. exponierte Berglage",
            },
        ],
        "field_caption": (
            "Orientierungswerte. Eine höhere Lage bedeutet nicht automatisch ein "
            "grösseres Sättigungsdefizit. Günstig wirken dort häufig Strahlung, Wind "
            "und die Erwärmung der Futteroberfläche."
        ),
        "limits_title": "Modellgrenzen",
        "limits_text": (
            "Die App ist ein didaktisches Modell und keine Wetter- oder Trocknungsprognose. "
            "Reale Verläufe werden zusätzlich durch wechselndes Wetter, Pflanzenart, "
            "Bestandesstruktur, Bodenfeuchte und Bearbeitung beeinflusst."
        ),
        "sources": "Grundlagen: Magnus-Formel; Agroscope / Schweizer Lehrunterlagen zur SDS.",
        "sidebar_title": "Luftzustand",
        "air_temp": "Lufttemperatur [°C]",
        "rh": "Relative Luftfeuchte [%]",
        "surface_temp": "Oberflächentemperatur des Futters [°C]",
        "surface_help": (
            "Die Umgebungsluft hat die oben eingestellte Temperatur und relative Feuchte. "
            "Die Luft direkt an der Futteroberfläche wird auf die Oberflächentemperatur "
            "des Futters abgekühlt. Erreicht die Oberfläche den Taupunkt, kann Tau entstehen."
        ),
        "tab_air": "Wasserdampf & Tau",
        "tab_sds": "SDS",
        "tab_drying": "Trocknung",
        "metric_sat": "Sättigungsfeuchte",
        "metric_abs": "Absolute Feuchte",
        "metric_sd": "Sättigungsdefizit",
        "metric_dew": "Taupunkt",
        "metric_surface": "Futteroberfläche",
        "metric_surface_rh": "rF an der Oberfläche",
        "metric_cond": "Kondensatpotenzial",
        "legend_sat": "Sättigung, rF = 100 %",
        "legend_surface_air": "Luft an der Futteroberfläche",
        "legend_surface_state": "Zustand an der Futteroberfläche",
        "legend_current": "Aktueller Luftzustand",
        "legend_sd": "Sättigungsdefizit",
        "dew_annotation": "Taupunkt",
        "x_temp": "Lufttemperatur [°C]",
        "y_rho": "Wasserdampfdichte ρᵥ [g/m³]",
        "dew_possible": "Tau möglich",
        "no_dew": "Kein Tau",
        "surface_not_colder": "Die Futteroberfläche ist nicht kälter als die Umgebungsluft.",
        "sds_subtitle": "Kumuliertes Trocknungspotenzial aus Temperatur und Luftfeuchtigkeit.",
        "sds_presets": {
            "160 g/m³·h – Naturwiese, Referenz Belüftungsheu": 160.0,
            "180 g/m³·h – mittlerer Vergleichswert": 180.0,
            "200 g/m³·h – Kunstwiese, Referenz Belüftungsheu": 200.0,
        },
        "sds_target": "SDS-Zielwert",
        "not_reachable": "nicht erreichbar",
        "current_sd": "Aktuelles SD",
        "time_to_sds": "Zeit bis SDS-Ziel",
        "calculation": "Berechnung",
        "dry_title": "Trocknungsverlauf",
        "dry_caption": (
            "Start bei 15 % TS. Die Trocknungsbedingungen bestimmen, wie wirksam "
            "das vorhandene Trocknungspotenzial genutzt wird."
        ),
        "dry_presets": {
            "Ungünstig": {
                "k": 0.07,
                "description": "Dichter Schwad, wenig Strahlung, wenig Wind oder feuchter Boden.",
            },
            "Normal": {
                "k": 0.12,
                "description": "Mittlere Ablage, mässige Strahlung und Luftbewegung.",
            },
            "Gut": {
                "k": 0.18,
                "description": "Breite, lockere Ablage, starke Strahlung und gute Luftbewegung.",
            },
        },
        "start_value": "Startwert",
        "start_value_text": "15 % TS",
        "dry_conditions": "Trocknungsbedingungen",
        "ts_curve": "TS-Gehalt",
        "targets": [
            (40, "40 % TS – Anwelksilage"),
            (60, "60 % TS – Einfuhr Belüftungsheu"),
            (75, "75 % TS – Einfuhr Bodenheu"),
        ],
        "sds_goal_plot": "SDS-Ziel",
        "x_time": "Zeit [h]",
        "y_dm": "TS-Gehalt [%]",
        "dm_at_sds": "TS beim SDS-Ziel",
        "metric_40": "40 % TS",
        "metric_60": "60 % TS",
        "metric_75": "75 % TS",
        "theory_times": (
            "Theoretische Zeiten bei konstantem SD und unveränderten Trocknungsbedingungen."
        ),
        "sd_symbol": "SD",
        "dm_abbr": "TS",
    },

    "FR": {
        "title": "Séchage des herbages",
        "subtitle": (
            "Relations physiques entre humidité de l’air, déficit de saturation, "
            "rosée et séchage."
        ),
        "theory_button": "ℹ️ Théorie et hypothèses",
        "air_state": "État de l’air",
        "dew_text": (
            "La rosée peut se former lorsque la surface du fourrage atteint ou passe sous "
            "le point de rosée de l’air adjacent. Il n’est pas nécessaire que tout l’air "
            "ambiant se refroidisse jusqu’au point de rosée."
        ),
        "sds_title": "Somme des déficits de saturation",
        "constant_conditions": "Pour des conditions constantes :",
        "sds_explanation": (
            "La SDS décrit le potentiel cumulé de séchage déduit de la température "
            "et de l’humidité de l’air. Le rayonnement et le vent ne sont pas "
            "entièrement pris en compte."
        ),
        "time_assumption": (
            "Pour le calcul du temps, on suppose que la température et l’humidité "
            "relative restent constantes."
        ),
        "sds_refs": (
            "Les valeurs cibles de 160 et 200 g/m³·h correspondent à des valeurs "
            "historiques suisses de référence jusqu’au stade du foin ventilé ; "
            "180 g/m³·h est une valeur intermédiaire utilisée pour l’enseignement."
        ),
        "model_title": "Modèle simplifié de séchage",
        "model_text": (
            "M est le rapport entre la masse d’eau et la masse sèche. k₀ est ici un "
            "facteur d’efficacité didactique pour le rayonnement, le vent et la structure "
            "de l’andain. Les valeurs de k₀ ne sont pas des constantes universelles."
        ),
        "field_title": "Conditions de séchage au champ",
        "field_columns": {
            "level": "Niveau",
            "radiation": "Rayonnement",
            "wind": "Vent",
            "swath": "Disposition",
            "situation": "Situation",
        },
        "field_rows": [
            {
                "level": "Défavorables",
                "radiation": "≈ 300 W/m²",
                "wind": "≈ 0.5 m/s",
                "swath": "andain dense",
                "situation": "couvert, peu de vent, sol humide",
            },
            {
                "level": "Normales",
                "radiation": "≈ 600 W/m²",
                "wind": "≈ 2 m/s",
                "swath": "andain moyennement étalé",
                "situation": "journée d’été sèche",
            },
            {
                "level": "Favorables",
                "radiation": "≈ 800 W/m²",
                "wind": "≈ 3 m/s",
                "swath": "large et aéré",
                "situation": "ensoleillé, sec, venteux ; p. ex. site de montagne exposé",
            },
        ],
        "field_caption": (
            "Valeurs indicatives. Une altitude plus élevée n’implique pas automatiquement "
            "un déficit de saturation plus important. Le rayonnement, le vent et le "
            "réchauffement de la surface du fourrage y sont souvent favorables."
        ),
        "limits_title": "Limites du modèle",
        "limits_text": (
            "Cette application est un modèle didactique et non une prévision météorologique "
            "ou de séchage. Les conditions réelles dépendent également des variations "
            "météorologiques, des espèces végétales, de la structure du peuplement, "
            "de l’humidité du sol et des interventions mécaniques."
        ),
        "sources": "Bases : formule de Magnus ; Agroscope / supports de cours suisses sur la SDS.",
        "sidebar_title": "État de l’air",
        "air_temp": "Température de l’air [°C]",
        "rh": "Humidité relative [%]",
        "surface_temp": "Température de surface du fourrage [°C]",
        "surface_help": (
            "L’air ambiant présente la température et l’humidité relative réglées ci-dessus. "
            "L’air directement au contact du fourrage est refroidi à la température de "
            "surface du fourrage. Si la surface atteint le point de rosée, de la rosée "
            "peut se former."
        ),
        "tab_air": "Vapeur d’eau & rosée",
        "tab_sds": "SDS",
        "tab_drying": "Séchage",
        "metric_sat": "Humidité à saturation",
        "metric_abs": "Humidité absolue",
        "metric_sd": "Déficit de saturation",
        "metric_dew": "Point de rosée",
        "metric_surface": "Surface du fourrage",
        "metric_surface_rh": "Humidité relative à la surface",
        "metric_cond": "Potentiel de condensation",
        "legend_sat": "Saturation, φ = 100 %",
        "legend_surface_air": "Air à la surface du fourrage",
        "legend_surface_state": "État à la surface du fourrage",
        "legend_current": "État actuel de l’air",
        "legend_sd": "Déficit de saturation",
        "dew_annotation": "Point de rosée",
        "x_temp": "Température de l’air [°C]",
        "y_rho": "Densité de vapeur d’eau ρᵥ [g/m³]",
        "dew_possible": "Rosée possible",
        "no_dew": "Pas de rosée",
        "surface_not_colder": "La surface du fourrage n’est pas plus froide que l’air ambiant.",
        "sds_subtitle": (
            "Potentiel cumulé de séchage déduit de la température et de l’humidité de l’air."
        ),
        "sds_presets": {
            "160 g/m³·h – prairie naturelle, référence foin ventilé": 160.0,
            "180 g/m³·h – valeur de comparaison intermédiaire": 180.0,
            "200 g/m³·h – prairie artificielle, référence foin ventilé": 200.0,
        },
        "sds_target": "Valeur cible SDS",
        "not_reachable": "non atteignable",
        "current_sd": "DS actuel",
        "time_to_sds": "Temps jusqu’à la valeur cible SDS",
        "calculation": "Calcul",
        "dry_title": "Évolution du séchage",
        "dry_caption": (
            "Départ à 15 % MS. Les conditions de séchage déterminent l’efficacité "
            "avec laquelle le potentiel de séchage disponible est utilisé."
        ),
        "dry_presets": {
            "Défavorables": {
                "k": 0.07,
                "description": "Andain dense, faible rayonnement, peu de vent ou sol humide.",
            },
            "Normales": {
                "k": 0.12,
                "description": "Andain moyennement étalé, rayonnement et mouvement de l’air modérés.",
            },
            "Favorables": {
                "k": 0.18,
                "description": "Andain large et aéré, fort rayonnement et bonne circulation de l’air.",
            },
        },
        "start_value": "Valeur initiale",
        "start_value_text": "15 % MS",
        "dry_conditions": "Conditions de séchage",
        "ts_curve": "Teneur en MS",
        "targets": [
            (40, "40 % MS – ensilage préfané"),
            (60, "60 % MS – rentrée du foin ventilé"),
            (75, "75 % MS – rentrée du foin au sol"),
        ],
        "sds_goal_plot": "Objectif SDS",
        "x_time": "Temps [h]",
        "y_dm": "Teneur en MS [%]",
        "dm_at_sds": "MS à l’objectif SDS",
        "metric_40": "40 % MS",
        "metric_60": "60 % MS",
        "metric_75": "75 % MS",
        "theory_times": (
            "Temps théoriques pour un DS constant et des conditions de séchage inchangées."
        ),
        "sd_symbol": "DS",
        "dm_abbr": "MS",
    },
}


# -----------------------------
# Header and language selector
# -----------------------------

head_left, head_lang, head_right = st.columns([4.0, 1.1, 1.6])

with head_lang:
    lang = st.radio(
        "Sprache / Langue",
        options=["DE", "FR"],
        horizontal=True,
        label_visibility="visible",
    )

t = TXT[lang]

with head_left:
    st.title(t["title"])
    st.caption(t["subtitle"])

with head_right:
    with st.popover(t["theory_button"], use_container_width=True):
        st.subheader(t["air_state"])
        st.latex(r"e_s(T)=6.112\cdot \exp\left(\frac{17.62\,T}{243.12+T}\right)")
        st.latex(r"\rho_v = 216.7\cdot\frac{e}{T+273.15}")

        if lang == "DE":
            st.latex(r"SD = \rho_{v,\mathrm{sat}}-\rho_v")
        else:
            st.latex(r"DS = \rho_{v,\mathrm{sat}}-\rho_v")

        st.write(t["dew_text"])

        st.divider()

        st.subheader(t["sds_title"])
        if lang == "DE":
            st.latex(r"\mathrm{SDS}=\int SD(t)\,dt")
            st.write(t["constant_conditions"])
            st.latex(r"\mathrm{SDS}=SD\cdot \Delta t")
        else:
            st.latex(r"\mathrm{SDS}=\int DS(t)\,dt")
            st.write(t["constant_conditions"])
            st.latex(r"\mathrm{SDS}=DS\cdot \Delta t")

        st.write(t["sds_explanation"])
        st.write(t["time_assumption"])
        st.write(t["sds_refs"])

        st.divider()

        st.subheader(t["model_title"])

        if lang == "DE":
            st.latex(r"\lambda = k_0\frac{SD}{10\ \mathrm{g\,m^{-3}}}")
        else:
            st.latex(r"\lambda = k_0\frac{DS}{10\ \mathrm{g\,m^{-3}}}")

        st.latex(r"M(t)=M_0\,e^{-\lambda t}")
        st.latex(
            r"M(t)=M_0\exp\left[-k_0\frac{\mathrm{SDS}(t)}"
            r"{10\ \mathrm{g\,m^{-3}}}\right]"
        )

        st.write(t["model_text"])

        st.divider()

        st.subheader(t["field_title"])

        rows = []
        c = t["field_columns"]
        for row in t["field_rows"]:
            rows.append(
                {
                    c["level"]: row["level"],
                    c["radiation"]: row["radiation"],
                    c["wind"]: row["wind"],
                    c["swath"]: row["swath"],
                    c["situation"]: row["situation"],
                }
            )

        field_conditions = pd.DataFrame(rows)
        st.dataframe(field_conditions, use_container_width=True, hide_index=True)
        st.caption(t["field_caption"])

        st.divider()

        st.subheader(t["limits_title"])
        st.write(t["limits_text"])
        st.caption(t["sources"])


# -----------------------------
# Physical functions
# -----------------------------

def saturation_vapor_pressure_hpa(T_c):
    """Saturation vapour pressure over water using the Magnus equation."""
    return 6.112 * np.exp((17.62 * T_c) / (243.12 + T_c))


def absolute_humidity_g_m3(T_c, rh_percent):
    """Water vapour density in g/m³."""
    e_s = saturation_vapor_pressure_hpa(T_c)
    e = (rh_percent / 100.0) * e_s
    return 216.7 * e / (T_c + 273.15)


def saturation_absolute_humidity_g_m3(T_c):
    return absolute_humidity_g_m3(T_c, 100.0)


def dew_point_c(T_c, rh_percent):
    """Dew point from the Magnus equation."""
    rh = np.clip(rh_percent, 0.1, 100.0)
    gamma = np.log(rh / 100.0) + (17.62 * T_c) / (243.12 + T_c)
    return 243.12 * gamma / (17.62 - gamma)


# -----------------------------
# Inputs
# -----------------------------

st.sidebar.header(t["sidebar_title"])

T = st.sidebar.slider(
    t["air_temp"],
    min_value=-5.0,
    max_value=40.0,
    value=20.0,
    step=0.5,
)

rh = st.sidebar.slider(
    t["rh"],
    min_value=10,
    max_value=100,
    value=60,
    step=1,
)

target_T = st.sidebar.slider(
    t["surface_temp"],
    min_value=-5.0,
    max_value=40.0,
    value=12.0,
    step=0.5,
    help=t["surface_help"],
)


# -----------------------------
# Shared calculations
# -----------------------------

rho_sat = float(saturation_absolute_humidity_g_m3(T))
rho_actual = float(absolute_humidity_g_m3(T, rh))
deficit = rho_sat - rho_actual
dew_point = float(dew_point_c(T, rh))

target_rho_sat = float(saturation_absolute_humidity_g_m3(target_T))
target_rho = min(rho_actual, target_rho_sat)
target_rh = min(100.0, 100.0 * target_rho / target_rho_sat)
condensed_g_m3 = max(0.0, rho_actual - target_rho_sat)


# -----------------------------
# Main views
# -----------------------------

tab_air, tab_sds, tab_drying = st.tabs(
    [
        t["tab_air"],
        t["tab_sds"],
        t["tab_drying"],
    ]
)


# =========================================================
# TAB 1: Air / water vapour / dew
# =========================================================

with tab_air:
    st.subheader(t["air_state"])

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(t["metric_sat"], f"{rho_sat:.1f} g/m³")
    c2.metric(t["metric_abs"], f"{rho_actual:.1f} g/m³")
    c3.metric(t["metric_sd"], f"{deficit:.1f} g/m³")
    c4.metric(t["metric_dew"], f"{dew_point:.1f} °C")

    c5, c6, c7 = st.columns(3)

    c5.metric(t["metric_surface"], f"{target_T:.1f} °C")
    c6.metric(t["metric_surface_rh"], f"{target_rh:.0f} %")
    c7.metric(t["metric_cond"], f"{condensed_g_m3:.1f} g/m³")

    T_curve = np.linspace(-5, 40, 300)
    rho_curve = saturation_absolute_humidity_g_m3(T_curve)

    process_T = np.linspace(T, target_T, 160)
    process_rho_sat = saturation_absolute_humidity_g_m3(process_T)
    process_rho = np.minimum(rho_actual, process_rho_sat)

    fig1 = go.Figure()

    fig1.add_trace(
        go.Scatter(
            x=T_curve,
            y=rho_curve,
            mode="lines",
            name=t["legend_sat"],
            line=dict(width=3),
        )
    )

    fig1.add_trace(
        go.Scatter(
            x=process_T,
            y=process_rho,
            mode="lines",
            name=t["legend_surface_air"],
            line=dict(width=3, dash="dash"),
        )
    )

    fig1.add_trace(
        go.Scatter(
            x=[target_T],
            y=[target_rho],
            mode="markers",
            name=t["legend_surface_state"],
            marker=dict(size=11),
        )
    )

    fig1.add_vline(
        x=dew_point,
        line_dash="dot",
        annotation_text=f"{t['dew_annotation']} {dew_point:.1f} °C",
        annotation_position="top",
    )

    fig1.add_trace(
        go.Scatter(
            x=[T],
            y=[rho_actual],
            mode="markers",
            name=t["legend_current"],
            marker=dict(size=12),
        )
    )

    fig1.add_trace(
        go.Scatter(
            x=[T, T],
            y=[rho_actual, rho_sat],
            mode="lines",
            name=t["legend_sd"],
            line=dict(dash="dot", width=3),
        )
    )

    fig1.add_hline(
        y=rho_actual,
        line_dash="dash",
        annotation_text=f"ρᵥ = {rho_actual:.1f} g/m³",
        annotation_position="bottom right",
    )

    fig1.update_layout(
        xaxis_title=t["x_temp"],
        yaxis_title=t["y_rho"],
        legend_title="",
        margin=dict(l=55, r=85, t=20, b=55),
        height=500,
    )

    _, fig1_col, _ = st.columns([0.04, 0.92, 0.04])

    with fig1_col:
        st.plotly_chart(fig1, use_container_width=True)

    if target_T <= dew_point:
        if lang == "DE":
            st.success(
                f"{t['dew_possible']}: Futteroberfläche {target_T:.1f} °C "
                f"≤ Taupunkt {dew_point:.1f} °C."
            )
        else:
            st.success(
                f"{t['dew_possible']} : surface du fourrage {target_T:.1f} °C "
                f"≤ point de rosée {dew_point:.1f} °C."
            )

    elif target_T < T:
        if lang == "DE":
            st.caption(
                f"{t['no_dew']}: An der Oberfläche steigt die rF auf etwa "
                f"{target_rh:.0f} %, der Taupunkt ({dew_point:.1f} °C) "
                f"wird aber nicht erreicht."
            )
        else:
            st.caption(
                f"{t['no_dew']} : à la surface, l’humidité relative atteint environ "
                f"{target_rh:.0f} %, mais le point de rosée ({dew_point:.1f} °C) "
                f"n’est pas atteint."
            )

    else:
        st.caption(t["surface_not_colder"])


# =========================================================
# TAB 2: SDS
# =========================================================

with tab_sds:
    st.subheader(f"{t['sds_title']} (SDS)")
    st.caption(t["sds_subtitle"])

    sds_presets = t["sds_presets"]

    sds_col1, sds_col2, sds_col3 = st.columns([1.8, 1, 1])

    with sds_col1:
        sds_choice = st.selectbox(
            t["sds_target"],
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
        duration_text = t["not_reachable"]

    sds_col2.metric(t["current_sd"], f"{deficit:.2f} g/m³")
    sds_col3.metric(t["time_to_sds"], duration_text)

    if deficit > 1e-6:
        st.caption(
            f"{t['calculation']}: {sds_target:.0f} g/m³·h ÷ "
            f"{deficit:.2f} g/m³ = {duration:.1f} h"
        )


# =========================================================
# TAB 3: Drying
# =========================================================

with tab_drying:
    st.subheader(t["dry_title"])
    st.caption(t["dry_caption"])

    initial_dm = 15.0
    drying_presets = t["dry_presets"]

    ctrl1, ctrl2 = st.columns([1, 2])

    ctrl1.metric(t["start_value"], t["start_value_text"])

    with ctrl2:
        drying_mode = st.selectbox(
            t["dry_conditions"],
            options=list(drying_presets.keys()),
            index=2,
        )

    k0 = drying_presets[drying_mode]["k"]
    st.caption(drying_presets[drying_mode]["description"])

    # Water content on dry basis: M = m_W / m_DM
    m0_db = (100.0 - initial_dm) / initial_dm

    # Reference saturation deficit: 10 g/m³
    lambda_eff = k0 * deficit / 10.0

    def theoretical_time_to_ts(target_ts):
        if lambda_eff <= 0:
            return np.inf

        m_target = (100.0 - target_ts) / target_ts
        return np.log(m0_db / m_target) / lambda_eff

    t40_theory = theoretical_time_to_ts(40.0)
    t60_theory = theoretical_time_to_ts(60.0)
    t75_theory = theoretical_time_to_ts(75.0)

    if np.isfinite(t75_theory):
        plot_duration = max(duration, 1.05 * t75_theory, 0.1)
    else:
        plot_duration = max(duration, 24.0)

    time_axis = np.linspace(0, plot_duration, 500)
    m_db_t = m0_db * np.exp(-lambda_eff * time_axis)
    dm_t = 100.0 / (1.0 + m_db_t)

    fig2 = go.Figure()

    fig2.add_trace(
        go.Scatter(
            x=time_axis,
            y=dm_t,
            mode="lines",
            name=t["ts_curve"],
            line=dict(width=3),
        )
    )

    for target, label in t["targets"]:
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
            annotation_text=f"{t['sds_goal_plot']}: {sds_target:.0f} g/m³·h",
            annotation_position="top",
        )

    fig2.update_layout(
        xaxis_title=t["x_time"],
        yaxis_title=t["y_dm"],
        yaxis_range=[0, 100],
        legend_title="",
        margin=dict(l=55, r=95, t=20, b=55),
        height=500,
    )

    _, fig2_col, _ = st.columns([0.04, 0.92, 0.04])

    with fig2_col:
        st.plotly_chart(fig2, use_container_width=True)

    m_db_at_sds = m0_db * np.exp(-lambda_eff * duration)
    ts_at_sds = 100.0 / (1.0 + m_db_at_sds)

    e1, e2, e3, e4 = st.columns(4)

    e1.metric(t["dm_at_sds"], f"{ts_at_sds:.1f} %")
    e2.metric(
        t["metric_40"],
        "∞" if not np.isfinite(t40_theory) else f"{t40_theory:.1f} h",
    )
    e3.metric(
        t["metric_60"],
        "∞" if not np.isfinite(t60_theory) else f"{t60_theory:.1f} h",
    )
    e4.metric(
        t["metric_75"],
        "∞" if not np.isfinite(t75_theory) else f"{t75_theory:.1f} h",
    )

    st.caption(t["theory_times"])
