"""
UI State Manager for Streamlit session persistence.
Maintains the active SystemState, recovery audit trails, and preset synchronization.
"""

import streamlit as st
import json
import pandas as pd
from typing import Optional, List, Dict, Any
from core.models import SystemState, RecoveryAction
from core.scenarios import get_preset_safe_system, PRESETS


def initialize_session_state():
    """Initializes default session variables if not already present."""
    if "current_state" not in st.session_state:
        st.session_state["current_state"] = get_preset_safe_system()

    if "current_preset_name" not in st.session_state:
        st.session_state["current_preset_name"] = "1. Safe System (Classic Banker's)"

    if "recovery_history" not in st.session_state:
        st.session_state["recovery_history"] = []

    if "simulation_log" not in st.session_state:
        st.session_state["simulation_log"] = []

    if "banker_step_idx" not in st.session_state:
        st.session_state["banker_step_idx"] = 0


def get_current_state() -> SystemState:
    """Returns the active SystemState from session."""
    return st.session_state["current_state"]


def set_current_state(state: SystemState, log_message: Optional[str] = None):
    """Updates the active SystemState and logs the event."""
    st.session_state["current_state"] = state
    if log_message:
        st.session_state["simulation_log"].append(log_message)


def reset_to_preset(preset_name: str):
    """Resets the active simulation state to a selected predefined preset."""
    if preset_name in PRESETS:
        new_state = PRESETS[preset_name]["generator"]()
        st.session_state["current_state"] = new_state
        st.session_state["current_preset_name"] = preset_name
        st.session_state["recovery_history"] = []
        st.session_state["banker_step_idx"] = 0
        st.session_state["simulation_log"].append(f"Loaded scenario preset: '{preset_name}'.")


def export_state_json(state: SystemState) -> str:
    """Exports state to JSON formatted string."""
    return json.dumps(state.to_dict(), indent=2)


def import_state_json(json_str: str) -> SystemState:
    """Imports state from JSON string."""
    data = json.loads(json_str)
    return SystemState.from_dict(data)
