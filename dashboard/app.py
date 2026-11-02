import numpy as np
import sys
from pathlib import Path

import streamlit as st
import pandas as pd
import plotly.express as px

# ============================================================
# PROJECT SETUP
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

DATA_PATH = PROJECT_ROOT / "data" / "chronos_x_events.csv"
PARADOX_DATA_PATH = (
    PROJECT_ROOT / "data" / "paradox_protocol" / "cx006_events.csv"
)

try:
    from backend.pipeline import run_pipeline
except Exception as e:
    run_pipeline = None
    PIPELINE_ERROR = str(e)
else:
    PIPELINE_ERROR = None


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="CHRONOS-X Command Center",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# DARK INDUSTRIAL THEME
# ============================================================

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #07111f, #0c1b2c);
    color: #e6f1fa;
}

section[data-testid="stSidebar"] {
    background: #091525;
    border-right: 1px solid #263d55;
}

h1, h2, h3 {
    color: #eaf6ff !important;
}

p, label, span {
    color: #c4d4e5;
}

div[data-testid="stMetric"] {
    background: #12263b;
    border: 1px solid #294761;
    padding: 17px;
    border-radius: 12px;
}

div[data-testid="stMetricValue"] {
    color: #36d9f5;
}

.stButton button {
    background: #087f9c;
    color: white;
    border: 1px solid #18b6d2;
    border-radius: 9px;
    font-weight: bold;
    min-height: 42px;
}

.stButton button:hover {
    background: #079fbd;
    color: white;
}

div[data-testid="stExpander"] {
    background: #102238;
    border: 1px solid #294761;
    border-radius: 10px;
}

hr {
    border-color: #294761;
}

.module-heading {
    background: linear-gradient(90deg, #102b43, #0b1b2c);
    border-left: 5px solid #22c9e8;
    border-radius: 8px;
    padding: 18px;
    margin-bottom: 20px;
}

.module-heading h2 {
    margin: 0;
    color: #42dafa;
}

.module-heading p {
    margin: 5px 0 0 0;
    color: #a9bfd2;
}

.small-note {
    color: #8da7bd;
    font-size: 13px;
}

.agent-card {
    background: #102238;
    border: 1px solid #294761;
    border-radius: 10px;
    padding: 14px;
    margin-bottom: 12px;
}

.agent-key {
    color: #43d8f2;
    font-weight: 700;
}
</style>
""", unsafe_allow_html=True)


# ============================================================
# DATA LOADING - ORIGINAL + PARADOX DATASET
# ============================================================

@st.cache_data
def load_dataset():

    if not DATA_PATH.exists():
        return pd.DataFrame()

    data = pd.read_csv(DATA_PATH)

    if PARADOX_DATA_PATH.exists():
        paradox_data = pd.read_csv(PARADOX_DATA_PATH)

        data = pd.concat(
            [data, paradox_data],
            ignore_index=True
        )

    for column in ["event_time", "arrival_time"]:
        if column in data.columns:
            data[column] = pd.to_datetime(
                data[column],
                errors="coerce"
            )

    return data


df = load_dataset()

if df.empty:
    st.error("Dataset not found. Check data/chronos_x_events.csv")
    st.stop()

scenario_ids = sorted(
    df["scenario_id"].dropna().astype(str).unique().tolist()
)


# ============================================================
# SESSION STATE
# ============================================================

PAGES = [
    "Overview",
    "Scenario Comparison",
    "M1 - Temporal Reconstruction",
    "M2 - Causal Investigation",
    "M3 - Counterfactual Simulation",
    "M4 - Multi-Agent System",
    "M5 - Risk Optimization",
    "M6 - Adversarial Detection",
    "M7 - Safety Verification",
    "M8 - Time Travel Command Center"
]

if "module_navigation" not in st.session_state:
    st.session_state.module_navigation = PAGES[0]

if "pipeline_result" not in st.session_state:
    st.session_state.pipeline_result = None

if "analysed_scenario" not in st.session_state:
    st.session_state.analysed_scenario = None

if "comparison_results" not in st.session_state:
    st.session_state.comparison_results = None


# ============================================================
# NAVIGATION CALLBACKS
# ============================================================

def go_previous():

    current = PAGES.index(
        st.session_state.module_navigation
    )

    if current > 0:
        st.session_state.module_navigation = PAGES[current - 1]


def go_next():

    current = PAGES.index(
        st.session_state.module_navigation
    )

    if current < len(PAGES) - 1:
        st.session_state.module_navigation = PAGES[current + 1]


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.markdown("# ⚙️ CHRONOS-X")
st.sidebar.caption("INDUSTRIAL COMMAND CENTER")
st.sidebar.divider()

selected_scenario = st.sidebar.selectbox(
    "SELECT SCENARIO",
    scenario_ids,
    key="scenario_selector"
)

if st.session_state.analysed_scenario != selected_scenario:
    st.session_state.pipeline_result = None

st.sidebar.divider()
st.sidebar.markdown("### NAVIGATION")

st.sidebar.radio(
    "Choose Module",
    PAGES,
    key="module_navigation"
)

page = PAGES.index(
    st.session_state.module_navigation
)


# ============================================================
# RUN FULL ANALYSIS
# ============================================================

st.sidebar.divider()

if st.sidebar.button(
    "RUN FULL ANALYSIS — M1 TO M7",
    key="run_full_analysis",
    use_container_width=True
):

    if run_pipeline is None:
        st.sidebar.error("Pipeline import failed.")
        st.sidebar.code(PIPELINE_ERROR)

    else:

        with st.spinner(
            f"Running CHRONOS-X analysis for {selected_scenario}..."
        ):

            try:

                st.session_state.pipeline_result = run_pipeline(
                    selected_scenario
                )

                st.session_state.analysed_scenario = selected_scenario

                st.sidebar.success(
                    "Analysis completed successfully!"
                )

            except Exception as e:
                st.sidebar.error(f"Analysis failed: {e}")


# ============================================================
# SYSTEM MODULES
# ============================================================

st.sidebar.divider()
st.sidebar.markdown("### SYSTEM MODULES")

st.sidebar.markdown("""
🕒 M1 — Temporal

🔍 M2 — Causal

🔮 M3 — Simulation

🤖 M4 — Agents

📊 M5 — Optimization

🛡️ M6 — Security

✅ M7 — Safety
""")

st.sidebar.caption("CHRONOS-X | Prototype v1.0")


# ============================================================
# COMMON HEADER
# ============================================================

st.markdown("# ⚙️ CHRONOS-X")

st.caption(
    "INDUSTRIAL RISK INTELLIGENCE & DECISION SUPPORT SYSTEM"
)

st.markdown(
    f"**ACTIVE SCENARIO:** `{selected_scenario}`"
)

st.divider()

scenario_df = df[
    df["scenario_id"].astype(str) == selected_scenario
].copy()

result = st.session_state.pipeline_result

if st.session_state.analysed_scenario != selected_scenario:
    result = None


# ============================================================
# COMMON HELPER FUNCTIONS
# ============================================================

def module_header(title, description):

    st.markdown(
        f"""
        <div class="module-heading">
            <h2>{title}</h2>
            <p>{description}</p>
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# RISK SCORE CLASSIFICATION
# ============================================================

def get_risk_category(score):

    try:
        score = float(score)
    except (TypeError, ValueError):
        return "UNKNOWN", "Risk score unavailable"

    if pd.isna(score):
        return "UNKNOWN", "Risk score unavailable"

    score = max(0, min(100, score))

    if score <= 30:
        return "LOW", "🟢"

    elif score <= 60:
        return "MEDIUM", "🟡"

    elif score <= 80:
        return "HIGH", "🟠"

    else:
        return "CRITICAL", "🔴"


def display_risk_metric(label, score):

    category, indicator = get_risk_category(score)

    if category == "UNKNOWN":
        st.metric(label, "N/A", "Risk score unavailable")
    else:
        st.metric(
            label,
            f"{float(score):.2f} / 100",
            f"{indicator} {category}"
        )


def show_table(data):

    if isinstance(data, pd.DataFrame) and not data.empty:

        st.dataframe(
            data,
            use_container_width=True,
            hide_index=True
        )

    elif isinstance(data, list) and data:

        st.dataframe(
            pd.DataFrame(data),
            use_container_width=True,
            hide_index=True
        )

    else:
        st.info("No records available.")


def show_text_list(items):

    if isinstance(items, list):
        for item in items:
            st.write("•", item)

    elif items:
        st.write(items)

    else:
        st.write("No details available.")


def render_agent_value(value, depth=0):

    if depth > 5:
        st.caption("Further nested details omitted.")
        return

    if value is None:
        st.write("Not available")

    elif isinstance(value, pd.DataFrame):

        if not value.empty:
            show_table(value)
        else:
            st.write("No records")

    elif isinstance(value, dict):

        if not value:
            st.write("No details available.")
            return

        for subkey, subvalue in value.items():

            label = (
                str(subkey)
                .replace("_", " ")
                .replace("-", " ")
                .title()
            )

            st.markdown(f"**{label}**")
            render_agent_value(subvalue, depth + 1)

    elif isinstance(value, (list, tuple)):

        if not value:
            st.write("No items available.")

        elif all(isinstance(item, dict) for item in value):

            try:
                show_table(pd.DataFrame(value))
            except Exception:
                for item in value:
                    render_agent_value(item, depth + 1)

        else:

            for item in value:

                if isinstance(item, (dict, list, tuple)):

                    with st.container(border=True):
                        render_agent_value(item, depth + 1)

                else:
                    st.markdown(f"- {item}")

    elif isinstance(value, bool):
        st.write("Yes" if value else "No")

    else:
        st.write(value)


def require_analysis():

    if result is None:
        st.warning(
            "Run the full analysis first using the button in the sidebar."
        )
        return False

    return True


def navigation():

    current = PAGES.index(
        st.session_state.module_navigation
    )

    st.divider()

    left, middle, right = st.columns([1, 2, 1])

    with left:
        st.button(
            "← PREVIOUS",
            disabled=(current == 0),
            use_container_width=True,
            on_click=go_previous
        )

    with middle:
        st.markdown(
            f"<p style='text-align:center'>PAGE {current + 1} OF {len(PAGES)}</p>",
            unsafe_allow_html=True
        )

    with right:
        st.button(
            "NEXT →",
            disabled=(current == len(PAGES) - 1),
            use_container_width=True,
            on_click=go_next
        )


# ============================================================
# PAGE 0 - OVERVIEW
# ============================================================

if page == 0:

    module_header(
        "COMMAND CENTER OVERVIEW",
        "Monitor industrial scenarios and launch the complete analysis pipeline."
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Scenario", selected_scenario)
    c2.metric("Total Events", len(scenario_df))
    c3.metric("Event Types", scenario_df["event_type"].nunique())
    c4.metric("Data Sources", scenario_df["source"].nunique())

    st.subheader("SCENARIO MONITORING")

    left, right = st.columns(2)

    with left:

        event_counts = (
            scenario_df["event_type"]
            .value_counts()
            .reset_index()
        )

        event_counts.columns = ["Event Type", "Count"]

        fig = px.bar(
            event_counts,
            x="Event Type",
            y="Count",
            title="Events by Type",
            template="plotly_dark"
        )

        st.plotly_chart(fig, use_container_width=True)

    with right:

        source_counts = (
            scenario_df["source"]
            .value_counts()
            .reset_index()
        )

        source_counts.columns = ["Source", "Count"]

        fig = px.pie(
            source_counts,
            names="Source",
            values="Count",
            title="Event Source Distribution",
            template="plotly_dark"
        )

        st.plotly_chart(fig, use_container_width=True)

    st.subheader("SCENARIO EVENT RECORDS")
    show_table(scenario_df)

    if result is not None:
        st.success("Analysis is ready. Navigate through M1 to M7.")
    else:
        st.info(
            "Select a scenario and click RUN FULL ANALYSIS in the sidebar."
        )


# ============================================================
# PAGE 1 - SCENARIO COMPARISON
# ============================================================

elif page == 1:

    module_header(
        "SCENARIO COMPARISON",
        "Compare event patterns, security alerts and safety verification across all scenarios."
    )

    st.info(
        "This page runs the complete M1–M7 pipeline separately for every scenario."
    )

    st.warning(
        "The comparison may take some time because each scenario is analysed independently."
    )

    if st.button(
        "RUN ALL SCENARIO COMPARISONS",
        key="run_scenario_comparison",
        use_container_width=True
    ):

        if run_pipeline is None:

            st.error("Pipeline import failed.")
            st.code(PIPELINE_ERROR)

        else:

            comparison_rows = []

            progress = st.progress(0)
            status_text = st.empty()

            try:

                for index, scenario_id in enumerate(scenario_ids):

                    status_text.write(
                        f"Analysing {scenario_id}..."
                    )

                    scenario_result = run_pipeline(scenario_id)

                    scenario_events = df[
                        df["scenario_id"].astype(str) == str(scenario_id)
                    ]

                    m6_data = scenario_result.get(
                        "m6",
                        pd.DataFrame()
                    )

                    if isinstance(m6_data, pd.DataFrame):

                        if "detection_status" in m6_data.columns:

                            flagged = m6_data[
                                m6_data["detection_status"] == "REVIEW_REQUIRED"
                            ]

                        else:
                            flagged = pd.DataFrame()

                        if "review_priority" in flagged.columns:

                            high_priority = flagged[
                                flagged["review_priority"] == "HIGH"
                            ]

                        else:
                            high_priority = pd.DataFrame()

                    else:

                        flagged = pd.DataFrame()
                        high_priority = pd.DataFrame()

                    m7 = scenario_result.get("m7", {})

                    comparison_rows.append({

                        "Scenario": scenario_id,

                        "Total Events": len(scenario_events),

                        "M6 Flagged Events": len(flagged),

                        "High Priority Alerts": len(high_priority),

                        "M7 Safety Status": m7.get(
                            "status",
                            "UNKNOWN"
                        )

                    })

                    progress.progress(
                        (index + 1) / len(scenario_ids)
                    )

                st.session_state.comparison_results = pd.DataFrame(
                    comparison_rows
                )

                status_text.success(
                    "All scenario comparisons completed successfully!"
                )

            except Exception as e:

                st.error(f"Comparison failed: {e}")

    comparison_df = st.session_state.comparison_results

    if comparison_df is not None and not comparison_df.empty:

        st.divider()

        st.subheader("SCENARIO PERFORMANCE SUMMARY")

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "Scenarios Analysed",
            len(comparison_df)
        )

        c2.metric(
            "Total Events",
            int(comparison_df["Total Events"].sum())
        )

        c3.metric(
            "Flagged Events",
            int(comparison_df["M6 Flagged Events"].sum())
        )

        c4.metric(
            "High Priority Alerts",
            int(comparison_df["High Priority Alerts"].sum())
        )

        st.divider()

        st.subheader("COMPLETE SCENARIO COMPARISON")
        show_table(comparison_df)

        st.divider()

        st.subheader("EVENT COUNT COMPARISON")

        fig = px.bar(
            comparison_df,
            x="Scenario",
            y="Total Events",
            title="Total Events Across Scenarios",
            text="Total Events",
            template="plotly_dark"
        )

        st.plotly_chart(fig, use_container_width=True)

        st.subheader("ADVERSARIAL ALERT COMPARISON")

        alert_chart = comparison_df.melt(
            id_vars="Scenario",
            value_vars=[
                "M6 Flagged Events",
                "High Priority Alerts"
            ],
            var_name="Alert Type",
            value_name="Count"
        )

        fig = px.bar(
            alert_chart,
            x="Scenario",
            y="Count",
            color="Alert Type",
            barmode="group",
            title="Security Alerts Across Scenarios",
            template="plotly_dark"
        )

        st.plotly_chart(fig, use_container_width=True)

        st.subheader("M7 SAFETY STATUS DISTRIBUTION")

        safety_counts = (
            comparison_df["M7 Safety Status"]
            .value_counts()
            .reset_index()
        )

        safety_counts.columns = [
            "Safety Status",
            "Scenario Count"
        ]

        fig = px.pie(
            safety_counts,
            names="Safety Status",
            values="Scenario Count",
            title="Safety Verification Results",
            template="plotly_dark"
        )

        st.plotly_chart(fig, use_container_width=True)

        st.caption(
            "PASS means implemented prototype checks passed. "
            "UNKNOWN means further evidence verification is required. "
            "These results do not certify real-world industrial safety."
        )

        csv_data = comparison_df.to_csv(index=False).encode("utf-8")

        st.download_button(
            "DOWNLOAD COMPARISON REPORT",
            data=csv_data,
            file_name="chronos_x_scenario_comparison.csv",
            mime="text/csv"
        )

    else:

        st.info(
            "Click RUN ALL SCENARIO COMPARISONS to generate the comparison report."
        )


# ============================================================
# M1 - TEMPORAL RECONSTRUCTION
# ============================================================

elif page == 2:

    module_header(
        "M1 — TEMPORAL RECONSTRUCTION",
        "Reconstruct event-time and arrival-time histories."
    )

    if require_analysis():

        m1 = result.get("m1", {})

        a, b, c = st.columns(3)

        a.metric("Event-Time Records", len(m1.get("event_history", [])))
        b.metric("Arrival-Time Records", len(m1.get("arrival_history", [])))
        c.metric("Duplicate Events", m1.get("duplicates", 0))

        st.subheader("Event-Time History")
        show_table(m1.get("event_history"))

        st.subheader("Arrival-Time History")
        show_table(m1.get("arrival_history"))


# ============================================================
# M2 - CAUSAL INVESTIGATION
# ============================================================

elif page == 3:

    module_header(
        "M2 — CAUSAL INVESTIGATION",
        "Identify possible root causes and supporting evidence."
    )

    if require_analysis():

        m2 = result.get("m2", {})

        st.metric(
            "Primary Root-Cause Hypothesis",
            m2.get("root_cause", "Not available")
        )

        a, b = st.columns(2)

        a.metric("Graph Nodes", m2.get("graph_nodes", 0))
        b.metric("Graph Edges", m2.get("graph_edges", 0))

        st.subheader("Root-Cause Hypotheses")

        for i, h in enumerate(m2.get("hypotheses", []), 1):

            with st.container(border=True):

                st.markdown(f"### Hypothesis {i}")

                st.markdown(
                    f"**Possible Cause:** {h.get('cause', 'Unknown')}"
                )

                st.metric(
                    "Evidence Score",
                    h.get("score", "N/A")
                )

                st.markdown("**Supporting Evidence**")
                show_text_list(h.get("evidence", []))

                st.caption(
                    "Assumptions: " +
                    str(h.get("assumptions", "Not available"))
                )

        st.caption(
            "Scores are heuristic evidence scores, not probabilities or confirmed causes."
        )


# ============================================================
# M3 - COUNTERFACTUAL SIMULATION
# ============================================================

# ============================================================
# M3 - COUNTERFACTUAL SIMULATION
# ============================================================

elif page == 4:

    module_header(
        "M3 — COUNTERFACTUAL SIMULATION",
        "Compare possible interventions and view simulated risk outcomes."
    )

    if require_analysis():

        m3 = result.get("m3", {})

        features = m3.get("features", {})
        simulations = m3.get("results", [])

        # ----------------------------------------------------
        # INITIAL RISK
        # ----------------------------------------------------

        st.subheader("INITIAL SCENARIO RISK")

        initial_risk = features.get("initial_risk")

        display_risk_metric(
            "Initial Risk Score",
            initial_risk
        )

        st.caption(
            "Initial risk is an illustrative index calculated from "
            "observed scenario indicators. It is not a real-world "
            "failure probability."
        )

        # ----------------------------------------------------
        # RISK CLASSIFICATION GUIDE
        # ----------------------------------------------------

        st.subheader("RISK CLASSIFICATION")

        risk_columns = st.columns(4)

        risk_columns[0].markdown(
            "**🟢 LOW**\n\n0–30"
        )

        risk_columns[1].markdown(
            "**🟡 MEDIUM**\n\n31–60"
        )

        risk_columns[2].markdown(
            "**🟠 HIGH**\n\n61–80"
        )

        risk_columns[3].markdown(
            "**🔴 CRITICAL**\n\n81–100"
        )

        # ----------------------------------------------------
        # SCENARIO INDICATORS
        # ----------------------------------------------------

        st.divider()

        st.subheader("SCENARIO INDICATORS")

        if isinstance(features, dict):

            indicator_features = {
                key: value
                for key, value in features.items()
                if key != "initial_risk"
            }

            cols = st.columns(3)

            for i, (key, value) in enumerate(
                indicator_features.items()
            ):

                with cols[i % 3]:

                    st.metric(
                        key.replace("_", " ").title(),
                        (
                            round(float(value), 2)
                            if isinstance(
                                value,
                                (int, float, np.number)
                            )
                            else value
                        )
                    )

        # ----------------------------------------------------
        # SIMULATION RESULTS
        # ----------------------------------------------------

        st.divider()

        st.subheader("INTERVENTION COMPARISON")

        if simulations:

            sim_df = pd.DataFrame(simulations)

            if not sim_df.empty:

                # Add risk categories to every action.
                if "average_peak" in sim_df.columns:

                    sim_df["Peak Risk Category"] = (
                        sim_df["average_peak"].apply(
                            lambda x: get_risk_category(x)[0]
                        )
                    )

                if "average_final" in sim_df.columns:

                    sim_df["Final Risk Category"] = (
                        sim_df["average_final"].apply(
                            lambda x: get_risk_category(x)[0]
                        )
                    )

                if "percentile_95" in sim_df.columns:

                    sim_df["95th Percentile Category"] = (
                        sim_df["percentile_95"].apply(
                            lambda x: get_risk_category(x)[0]
                        )
                    )

                # ------------------------------------------------
                # SIMULATED RISK OUTCOMES
                # ------------------------------------------------

                st.subheader("SIMULATED RISK OUTCOMES")

                if "average_peak" in sim_df.columns:

                    best_peak = pd.to_numeric(
                        sim_df["average_peak"],
                        errors="coerce"
                    ).min()

                    display_risk_metric(
                        "Lowest Average Peak Risk",
                        best_peak
                    )

                if "average_final" in sim_df.columns:

                    best_final = pd.to_numeric(
                        sim_df["average_final"],
                        errors="coerce"
                    ).min()

                    display_risk_metric(
                        "Lowest Average Final Risk",
                        best_final
                    )

                if "percentile_95" in sim_df.columns:

                    best_p95 = pd.to_numeric(
                        sim_df["percentile_95"],
                        errors="coerce"
                    ).min()

                    display_risk_metric(
                        "Lowest 95th Percentile Risk",
                        best_p95
                    )

                # ------------------------------------------------
                # ACTION RISK COMPARISON CHART
                # ------------------------------------------------

                st.divider()

                st.subheader("RISK SCORE BY INTERVENTION")

                risk_columns = [
                    col for col in [
                        "average_peak",
                        "average_final",
                        "percentile_95"
                    ]
                    if col in sim_df.columns
                ]

                if risk_columns:

                    chart_df = sim_df[
                        ["action"] + risk_columns
                    ].copy()

                    chart_df = chart_df.rename(
                        columns={
                            "action": "Intervention",
                            "average_peak": "Average Peak Risk",
                            "average_final": "Average Final Risk",
                            "percentile_95": "95th Percentile Risk"
                        }
                    )

                    chart_df = chart_df.melt(
                        id_vars="Intervention",
                        var_name="Risk Metric",
                        value_name="Risk Score"
                    )

                    chart_df["Risk Score"] = pd.to_numeric(
                        chart_df["Risk Score"],
                        errors="coerce"
                    )

                    chart_df = chart_df.dropna(
                        subset=["Risk Score"]
                    )

                    fig = px.bar(
                        chart_df,
                        x="Intervention",
                        y="Risk Score",
                        color="Risk Metric",
                        barmode="group",
                        title="Simulated Risk Comparison",
                        template="plotly_dark",
                        hover_data=["Risk Score"]
                    )

                    fig.update_layout(
                        yaxis_title="Risk Score (0–100)",
                        xaxis_title="Intervention"
                    )

                    fig.update_yaxes(range=[0, 100])

                    st.plotly_chart(
                        fig,
                        use_container_width=True
                    )

                # ------------------------------------------------
                # RISK CATEGORY PER ACTION
                # ------------------------------------------------

                st.divider()

                st.subheader("ACTION-WISE RISK CLASSIFICATION")

                for _, row in sim_df.iterrows():

                    action = str(row.get("action", "Unknown"))

                    peak = row.get("average_peak")
                    final = row.get("average_final")
                    p95 = row.get("percentile_95")

                    peak_category, peak_icon = (
                        get_risk_category(peak)
                    )

                    with st.container(border=True):

                        st.markdown(
                            f"### {action.replace('_', ' ')}"
                        )

                        c1, c2, c3 = st.columns(3)

                        with c1:
                            display_risk_metric(
                                "Average Peak Risk",
                                peak
                            )

                        with c2:
                            display_risk_metric(
                                "Average Final Risk",
                                final
                            )

                        with c3:
                            display_risk_metric(
                                "95th Percentile Risk",
                                p95
                            )

                        st.write(
                            f"**Peak Risk Category:** "
                            f"{peak_icon} {peak_category}"
                        )

                # ------------------------------------------------
                # COMPLETE SIMULATION TABLE
                # ------------------------------------------------

                st.divider()

                st.subheader("COMPLETE SIMULATION RESULTS")

                show_table(sim_df)

                # ------------------------------------------------
                # HIGH RISK FREQUENCY
                # ------------------------------------------------

                if "high_risk_frequency" in sim_df.columns:

                    st.divider()

                    st.subheader(
                        "HIGH-RISK FREQUENCY ACROSS SIMULATIONS"
                    )

                    fig = px.bar(
                        sim_df,
                        x="action",
                        y="high_risk_frequency",
                        title="Percentage of Rollouts Reaching Risk 80 or Higher",
                        labels={
                            "action": "Intervention",
                            "high_risk_frequency": "Rollout Frequency (%)"
                        },
                        template="plotly_dark"
                    )

                    fig.update_yaxes(
                        range=[0, 100]
                    )

                    st.plotly_chart(
                        fig,
                        use_container_width=True
                    )

        else:

            st.info(
                "No simulation results available. "
                "Check the M3 pipeline output."
            )

        # ----------------------------------------------------
        # DISCLAIMER
        # ----------------------------------------------------

        st.divider()

        st.caption(
            "CHRONOS-X uses 200 Monte Carlo rollouts and 10 simulation "
            "steps per action. Risk categories are illustrative display "
            "bands applied to the existing 0–100 risk index. They are "
            "not calibrated failure probabilities or certified "
            "industrial safety thresholds."
        )


# ============================================================
# M4 - MULTI-AGENT SYSTEM
# ============================================================

elif page == 5:

    module_header(
        "M4 — MULTI-AGENT SYSTEM",
        "View the investigator, predictor, optimizer, safety and red-team agents."
    )

    if require_analysis():

        m4 = result.get("m4", {})

        if not isinstance(m4, dict) or not m4:

            st.warning(
                "M4 agent results are missing or have an unexpected format."
            )

        else:

            st.metric(
                "Agent System Status",
                m4.get("final_status", "Not available")
            )

            agent_labels = {
                "investigation": "🔍 INVESTIGATOR AGENT",
                "prediction": "🔮 PREDICTOR AGENT",
                "optimization": "📊 OPTIMIZER AGENT",
                "safety": "🛡️ SAFETY AGENT",
                "red_team": "⚔️ RED-TEAM AGENT"
            }

            found_agents = 0

            for key, label in agent_labels.items():

                if key in m4:

                    found_agents += 1

                    with st.container(border=True):

                        st.markdown(f"### {label}")
                        render_agent_value(m4[key])

            if found_agents == 0:

                st.warning(
                    "No recognized agent sections were found."
                )

                st.write(
                    ", ".join(str(k) for k in m4.keys())
                )

            st.caption(
                "These are rule-based prototype agents. Their outputs require independent validation."
            )


# ============================================================
# M5 - RISK-AWARE OPTIMIZATION
# ============================================================

# ============================================================
# M5 - RISK-AWARE OPTIMIZATION
# ============================================================

elif page == 6:

    module_header(
        "M5 — RISK-AWARE OPTIMIZATION",
        "View risk classification and compare optimized intervention plans."
    )

    if require_analysis():

        m5 = result.get("m5", {})
        m3 = result.get("m3", {})

        if not isinstance(m5, dict) or not m5:

            st.warning("M5 optimization results are not available.")

        else:

            # ------------------------------------------------
            # INITIAL RISK CLASSIFICATION
            # ------------------------------------------------

            st.subheader("SCENARIO RISK ASSESSMENT")

            initial_risk = m5.get(
                "initial_risk",
                m3.get("features", {}).get("initial_risk")
            )

            display_risk_metric(
                "Initial Scenario Risk",
                initial_risk
            )

            st.caption(
                "Risk categories are illustrative classifications "
                "of the prototype's 0–100 risk index."
            )

            # ------------------------------------------------
            # RISK CLASSIFICATION GUIDE
            # ------------------------------------------------

            st.subheader("RISK CLASSIFICATION")

            c1, c2, c3, c4 = st.columns(4)

            c1.markdown("**🟢 LOW**\n\n0–30")
            c2.markdown("**🟡 MEDIUM**\n\n31–60")
            c3.markdown("**🟠 HIGH**\n\n61–80")
            c4.markdown("**🔴 CRITICAL**\n\n81–100")

            st.divider()

            # ------------------------------------------------
            # OPTIMIZATION METRICS
            # ------------------------------------------------

            st.subheader("OPTIMIZATION CONSTRAINTS")

            a, b, c = st.columns(3)

            a.metric(
                "Resources Used",
                f"{m5.get('resources_used', 0)} / "
                f"{m5.get('resource_budget', 0)}"
            )

            b.metric(
                "Time Required",
                f"{m5.get('time_required', 0)} / "
                f"{m5.get('time_deadline', 0)}"
            )

            c.metric(
                "Plan Feasible",
                "YES" if m5.get("feasible") else "NO"
            )

            st.divider()

            # ------------------------------------------------
            # OPTIMIZED PLAN
            # ------------------------------------------------

            optimized = m5.get("optimized", {})

            st.subheader("🏆 OPTIMIZED ACTION PLAN")

            actions = (
                optimized.get("plan", [])
                if isinstance(optimized, dict)
                else []
            )

            if isinstance(actions, list) and actions:

                if actions == ["NO_ACTION"]:

                    st.info("The optimizer selected the NO ACTION plan.")

                else:

                    for i, action in enumerate(actions, 1):

                        st.markdown(
                            f"**{i}.** {str(action).replace('_', ' ')}"
                        )

            else:
                st.info("No intervention action selected.")

            # ------------------------------------------------
            # STRATEGY COMPARISON
            # ------------------------------------------------

            st.divider()

            st.subheader("STRATEGY COMPARISON")

            strategy_rows = []

            for name in ["no_action", "greedy", "optimized"]:

                strategy = m5.get(name, {})

                if isinstance(strategy, dict):

                    plan = strategy.get("plan", [])

                    plan_text = (
                        ", ".join(
                            str(action).replace("_", " ")
                            for action in plan
                        )
                        if isinstance(plan, list)
                        else str(plan)
                    )

                    strategy_rows.append({

                        "Strategy": name.replace("_", " ").title(),

                        "Action Plan": plan_text,

                        "Objective Score": strategy.get(
                            "objective_score", "N/A"
                        ),

                        "Feasible": strategy.get(
                            "feasible", "N/A"
                        )

                    })

            if strategy_rows:

                comparison_df = pd.DataFrame(strategy_rows)

                show_table(comparison_df)

                chart_df = comparison_df.copy()

                chart_df["Objective Score"] = pd.to_numeric(
                    chart_df["Objective Score"],
                    errors="coerce"
                )

                chart_df = chart_df.dropna(
                    subset=["Objective Score"]
                )

                if not chart_df.empty:

                    st.subheader("OPTIMIZATION OBJECTIVE COMPARISON")

                    fig = px.bar(
                        chart_df,
                        x="Strategy",
                        y="Objective Score",
                        color="Strategy",
                        title="Objective Score by Strategy",
                        template="plotly_dark"
                    )

                    st.plotly_chart(
                        fig,
                        use_container_width=True
                    )

            else:

                st.info("Strategy comparison data is unavailable.")

            # ------------------------------------------------
            # RESOURCE AND TIME VALIDATION
            # ------------------------------------------------

            st.divider()

            st.subheader("RESOURCE AND DEADLINE VALIDATION")

            resource_used = m5.get("resources_used", 0)
            resource_budget = m5.get("resource_budget", 0)

            time_used = m5.get("time_required", 0)
            time_deadline = m5.get("time_deadline", 0)

            st.write(
                f"**Resource Budget:** {resource_used} used "
                f"out of {resource_budget}"
            )

            st.progress(
                min(
                    max(
                        float(resource_used) /
                        max(float(resource_budget), 1),
                        0.0
                    ),
                    1.0
                )
            )

            st.write(
                f"**Time Deadline:** {time_used} required "
                f"out of {time_deadline}"
            )

            st.progress(
                min(
                    max(
                        float(time_used) /
                        max(float(time_deadline), 1),
                        0.0
                    ),
                    1.0
                )
            )

            # ------------------------------------------------
            # DISCLAIMER
            # ------------------------------------------------

            st.divider()

            st.caption(
                "The risk category displays the initial simulated risk index. "
                "Optimization objective scores are separate from risk scores "
                "and must not be interpreted as risk percentages. "
                "All outputs use illustrative simulation assumptions."
            )


# ============================================================
# M6 - ADVERSARIAL DETECTION
# ============================================================

elif page == 7:

    module_header(
        "M6 — ADVERSARIAL DETECTION",
        "Identify suspicious events that require further investigation."
    )

    if require_analysis():

        m6 = result.get("m6", pd.DataFrame())

        if isinstance(m6, pd.DataFrame) and not m6.empty:

            if "detection_status" in m6.columns:

                flagged = m6[
                    m6["detection_status"] == "REVIEW_REQUIRED"
                ].copy()

            else:
                flagged = pd.DataFrame()

            a, b, c = st.columns(3)

            a.metric("Total Events", len(m6))
            b.metric("Flagged Events", len(flagged))

            high_count = (
                len(
                    flagged[
                        flagged["review_priority"] == "HIGH"
                    ]
                )
                if "review_priority" in flagged.columns
                else 0
            )

            c.metric("High Priority", high_count)

            st.subheader("Detection Summary")

            if not flagged.empty:

                if "review_priority" in flagged.columns:

                    priority_counts = (
                        flagged["review_priority"]
                        .value_counts()
                        .reset_index()
                    )

                    priority_counts.columns = ["Priority", "Count"]

                    fig = px.pie(
                        priority_counts,
                        names="Priority",
                        values="Count",
                        title="Review Priority Distribution",
                        template="plotly_dark"
                    )

                    st.plotly_chart(fig, use_container_width=True)

                st.subheader("Events Requiring Review")
                show_table(flagged)

            else:
                st.success(
                    "No events flagged for review in this scenario."
                )

            with st.expander("View all detection records"):
                show_table(m6)

        else:
            st.info("No M6 records available.")


# ============================================================
# M7 - SAFETY VERIFICATION
# ============================================================


elif page == 8:
    module_header(
        "M7 — SAFETY VERIFICATION",
        "Check whether the proposed intervention plan satisfies prototype safety rules."
    )

    if require_analysis():

        m7 = result.get("m7", {})
        status = str(m7.get("status", "UNKNOWN")).upper()

        # Safety status
        st.subheader("Safety Verification Status")

        if status == "PASS":
            st.success("SAFETY VERIFICATION: PASS")
        elif status == "FAIL":
            st.error("SAFETY VERIFICATION: FAIL")
        else:
            st.warning(f"SAFETY VERIFICATION: {status}")

        # Verification metrics
        st.subheader("Verification Details")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Resources Used",
                f"{m7.get('resources', 'N/A')} / 10"
            )

        with col2:
            st.metric(
                "Time Required",
                f"{m7.get('time', 'N/A')} / 20"
            )

        with col3:
            st.metric(
                "High-Priority Events",
                m7.get("high_priority_events", 0)
            )

        # Proposed actions
        st.subheader("Proposed Actions")

        actions = m7.get("actions", [])

        if actions:
            for action in actions:
                st.write(f"• {action}")
        else:
            st.info("No intervention actions proposed.")

        # Verification reasons
        st.subheader("Verification Reasons")

        reasons = m7.get("reasons", [])

        if reasons:
            for reason in reasons:
                if status == "PASS":
                    st.success(reason)
                elif status == "FAIL":
                    st.error(reason)
                else:
                    st.warning(reason)
        else:
            st.info("No verification reasons available.")

        # Scenario information
        st.subheader("Scenario Information")

        st.write(
            "**Scenario ID:**",
            m7.get("scenario_id", selected_scenario)
        )

        st.caption(
            "Resource budget: 10 units | "
            "Virtual deadline: 20 time units"
        )

        st.caption(
            "A PASS indicates that implemented prototype checks passed; "
            "it is not real-world industrial safety certification. "
            "UNKNOWN requires independent evidence verification."
        )



# ============================================================
# M8 - TIME-TRAVEL COMMAND CENTER
# ============================================================

elif page == 9:

    module_header(
        "M8 — TIME-TRAVEL COMMAND CENTER",
        "Explore historical event states and reconstruct scenario timelines."
    )

    st.info(
        "Select a timestamp to inspect the scenario as it appeared at that point in time."
    )

    time_column = st.radio(
        "TIMELINE MODE",
        ["Event Time", "Arrival Time"],
        horizontal=True
    )

    time_field = (
        "event_time"
        if time_column == "Event Time"
        else "arrival_time"
    )

    if time_field not in scenario_df.columns:

        st.error(f"{time_field} is missing from the dataset.")

    else:

        timeline_data = scenario_df.dropna(
            subset=[time_field]
        ).copy()

        timeline_data = timeline_data.sort_values(time_field)

        if timeline_data.empty:

            st.warning("No timestamp records available.")

        else:

            min_time = timeline_data[time_field].min()
            max_time = timeline_data[time_field].max()

            selected_time = st.slider(
                "TRAVEL THROUGH TIME",
                min_value=min_time.to_pydatetime(),
                max_value=max_time.to_pydatetime(),
                value=max_time.to_pydatetime(),
                format="YYYY-MM-DD HH:mm:ss"
            )

            historical = timeline_data[
                timeline_data[time_field] <= pd.Timestamp(selected_time)
            ].copy()

            upcoming = timeline_data[
                timeline_data[time_field] > pd.Timestamp(selected_time)
            ].copy()

            st.divider()

            st.subheader("HISTORICAL SYSTEM SNAPSHOT")

            a, b, c = st.columns(3)

            a.metric(
                "Selected Timestamp",
                pd.Timestamp(selected_time).strftime("%H:%M:%S")
            )

            b.metric(
                "Events Recorded",
                len(historical)
            )

            c.metric(
                "Upcoming Events",
                len(upcoming)
            )

            st.divider()

            st.subheader("EVENT TIMELINE")

            if not historical.empty:

                fig = px.scatter(
                    historical,
                    x=time_field,
                    y="event_type",
                    color="source",
                    hover_data=[
                        col for col in [
                            "event_id",
                            "value",
                            "unit",
                            "trust_score",
                            "note"
                        ]
                        if col in historical.columns
                    ],
                    title="Historical Event Replay",
                    template="plotly_dark"
                )

                fig.update_layout(
                    xaxis_title=time_column,
                    yaxis_title="Event Type"
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

            else:

                st.info(
                    "No events had been recorded at this timestamp."
                )

            st.divider()

            st.subheader("HISTORICAL EVENT RECORDS")

            show_table(historical)

            st.divider()

            st.subheader("UPCOMING EVENTS")

            if not upcoming.empty:

                show_table(upcoming)

            else:

                st.success(
                    "You have reached the end of the available timeline."
                )

            st.divider()

            st.subheader("TIMELINE INTERPRETATION")

            st.write(
                f"At the selected timestamp, "
                f"{len(historical)} of {len(timeline_data)} "
                f"events had been recorded using {time_column.lower()}."
            )

            st.caption(
                "This is a historical data replay based on recorded timestamps. "
                "It does not reconstruct unrecorded physical equipment states."
            )



# ============================================================
# PAGE NAVIGATION
# ============================================================

navigation()

st.divider()

st.markdown(
    """
    <p class='small-note'>
        CHRONOS-X | Synthetic industrial demonstration |
        Decision support only — no real equipment control.
    </p>
    """,
    unsafe_allow_html=True
)
