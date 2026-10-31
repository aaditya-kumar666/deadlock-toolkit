"""
DEADLOCK PREVENTION AND RECOVERY TOOLKIT
CSE316 Operating Systems Academic Project — Lovely Professional University
Main Streamlit Application Entrypoint.
"""

import streamlit as st

# Set Streamlit page configuration (must be first Streamlit command)
st.set_page_config(
    page_title="Deadlock Prevention & Recovery Toolkit",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom styling for polished, modern academic dashboard
st.markdown("""
<style>
    /* Dark neutral styling enhancements */
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2.5rem;
    }
    div[data-testid="metric-container"] {
        background-color: #1E293B;
        border: 1px solid #334155;
        padding: 0.8rem 1.2rem;
        border-radius: 8px;
    }
    div[data-testid="metric-container"] label {
        color: #94A3B8 !important;
        font-weight: 500;
    }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        color: #F8FAFC !important;
        font-size: 1.5rem;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)

from ui.state_manager import initialize_session_state, get_current_state, reset_to_preset
from ui.dashboard import render_dashboard
from ui.scenario_builder import render_scenario_builder
from ui.analysis_page import render_analysis_page
from ui.prevention_page import render_prevention_page
from ui.recovery_page import render_recovery_page
from ui.what_if_page import render_what_if_page
from ui.benchmark_page import render_benchmark_page
from core.scenarios import PRESETS


def main():
    initialize_session_state()
    state = get_current_state()

    # Sidebar Header & Metadata
    with st.sidebar:
        st.markdown("### 🔒 Deadlock Toolkit")
        st.caption("CSE316 Operating Systems | LPU")
        st.markdown("---")

        # Navigation
        pages = [
            "📊 Dashboard & RAG",
            "🛠️ Scenario Builder",
            "🔬 Avoidance & Detection",
            "🛡️ Deadlock Prevention",
            "🚨 Deadlock Recovery",
            "🔮 What-If Analysis",
            "⚡ Performance Benchmarks",
        ]
        selected_page = st.radio("Navigation Menu:", options=pages, index=0)

        st.markdown("---")
        st.markdown("#### 📂 Quick Preset Loader")
        active_preset = st.session_state.get("current_preset_name", "Custom")
        st.markdown(f"**Active:** `{active_preset}`")

        preset_choice = st.selectbox(
            "Change Preset:",
            options=list(PRESETS.keys()),
            key="quick_preset_select",
        )
        if st.button("Load Selected Preset", use_container_width=True):
            reset_to_preset(preset_choice)
            st.toast(f"Loaded '{preset_choice}'!", icon="🚀")
            st.rerun()

        st.markdown("---")
        st.markdown("#### ⚙️ Scenario Glance")
        st.markdown(f"• **Processes (n):** `{state.num_processes}`")
        st.markdown(f"• **Resource Types (m):** `{state.num_resources}`")
        st.markdown(f"• **Total Units:** `{sum(state.total)}`")
        st.markdown(f"• **Available Units:** `{sum(state.available)}`")

        st.markdown("---")
        st.caption("Educational Laboratory Simulator\nStrictly In-Memory Non-Destructive Model.")

    # Page Routing
    if selected_page == "📊 Dashboard & RAG":
        render_dashboard()
    elif selected_page == "🛠️ Scenario Builder":
        render_scenario_builder()
    elif selected_page == "🔬 Avoidance & Detection":
        render_analysis_page()
    elif selected_page == "🛡️ Deadlock Prevention":
        render_prevention_page()
    elif selected_page == "🚨 Deadlock Recovery":
        render_recovery_page()
    elif selected_page == "🔮 What-If Analysis":
        render_what_if_page()
    elif selected_page == "⚡ Performance Benchmarks":
        render_benchmark_page()


if __name__ == "__main__":
    main()
