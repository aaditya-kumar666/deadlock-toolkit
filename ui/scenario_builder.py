"""
UI Module: Custom Scenario Builder.
Provides interactive matrix editing, automatic Need matrix computation,
rigorous validation error reporting, preset loading, and JSON/CSV export/import.
"""

import streamlit as st
import pandas as pd
import json
from ui.state_manager import get_current_state, set_current_state, reset_to_preset, export_state_json, import_state_json
from core.models import SystemState
from core.validation import validate_system_state
from core.scenarios import PRESETS


def render_scenario_builder():
    """Renders the scenario editor and configuration workbench."""
    state = get_current_state()

    st.markdown("## 🛠️ Scenario Builder & Matrix Editor")
    st.markdown(
        "*Configure custom process and resource parameters, edit allocation matrices, and validate consistency laws.*"
    )

    # Preset Selection Bar
    with st.expander("📂 Load Predefined Scenario Preset", expanded=True):
        col_p1, col_p2 = st.columns([3, 1])
        with col_p1:
            preset_options = list(PRESETS.keys())
            selected_preset = st.selectbox(
                "Select Academic Scenario Preset:",
                options=preset_options,
                index=0,
                help="Select one of the 5 academically verified presets.",
            )
            st.caption(PRESETS[selected_preset]["description"])
        with col_p2:
            st.write("")
            st.write("")
            if st.button("🚀 Load Preset", use_container_width=True):
                reset_to_preset(selected_preset)
                st.success(f"Loaded '{selected_preset}' successfully!")
                st.rerun()

    st.markdown("---")

    # Dimensions & Vector Editor
    st.markdown("### 1. Resource & Process Configuration")
    col_d1, col_d2, col_d3 = st.columns([1, 1, 2])

    with col_d1:
        num_p = st.number_input("Number of Processes (n)", min_value=1, max_value=20, value=state.num_processes)
    with col_d2:
        num_r = st.number_input("Number of Resource Types (m)", min_value=1, max_value=10, value=state.num_resources)

    # Adjust process IDs and resource IDs if dimensions changed
    process_ids = [f"P{i}" for i in range(num_p)]
    resource_ids = [chr(65 + j) if j < 26 else f"R{j}" for j in range(num_r)]

    st.markdown("#### Total & Available Resource Vectors")
    c_tot, c_avail = st.columns(2)

    with c_tot:
        st.markdown("**Total Resource Capacity (Vector E):**")
        df_tot = pd.DataFrame([state.total[:num_r] + [5] * max(0, num_r - len(state.total))], columns=resource_ids)
        edited_tot = st.data_editor(df_tot, use_container_width=True, key="edit_tot")
        new_total = [int(v) for v in edited_tot.iloc[0].tolist()]

    with c_avail:
        st.markdown("**Available Resources (Vector A):**")
        df_avail = pd.DataFrame([state.available[:num_r] + [2] * max(0, num_r - len(state.available))], columns=resource_ids)
        edited_avail = st.data_editor(df_avail, use_container_width=True, key="edit_avail")
        new_available = [int(v) for v in edited_avail.iloc[0].tolist()]

    st.markdown("---")

    # Matrix Editors
    st.markdown("### 2. State Matrices")
    m_col1, m_col2 = st.columns(2)

    # Pad or slice existing matrices to match new dimensions
    def resize_matrix(mat, rows, cols, default_val=0):
        new_mat = []
        for i in range(rows):
            row = []
            for j in range(cols):
                if i < len(mat) and j < len(mat[i]):
                    row.append(mat[i][j])
                else:
                    row.append(default_val)
            new_mat.append(row)
        return new_mat

    curr_alloc = resize_matrix(state.allocation, num_p, num_r, 0)
    curr_max = resize_matrix(state.maximum, num_p, num_r, 2)
    curr_req = resize_matrix(state.request, num_p, num_r, 0)

    with m_col1:
        st.markdown("**Current Allocation Matrix (C):**")
        df_alloc = pd.DataFrame(curr_alloc, index=process_ids, columns=resource_ids)
        edited_alloc = st.data_editor(df_alloc, use_container_width=True, key="edit_alloc")
        new_alloc = [[int(v) for v in row] for row in edited_alloc.values.tolist()]

        st.markdown("**Outstanding Request Matrix (Q) - For Detection:**")
        df_req = pd.DataFrame(curr_req, index=process_ids, columns=resource_ids)
        edited_req = st.data_editor(df_req, use_container_width=True, key="edit_req")
        new_req = [[int(v) for v in row] for row in edited_req.values.tolist()]

    with m_col2:
        st.markdown("**Maximum Claim Matrix (M) - For Banker's:**")
        df_max = pd.DataFrame(curr_max, index=process_ids, columns=resource_ids)
        edited_max = st.data_editor(df_max, use_container_width=True, key="edit_max")
        new_max = [[int(v) for v in row] for row in edited_max.values.tolist()]

        st.markdown("**Automatically Computed Need Matrix (N = M - C):**")
        need_calc = []
        for i in range(num_p):
            row = [new_max[i][j] - new_alloc[i][j] for j in range(num_r)]
            need_calc.append(row)
        df_need = pd.DataFrame(need_calc, index=process_ids, columns=resource_ids)
        st.dataframe(df_need, use_container_width=True)

    st.markdown("---")

    # Priorities & Costs
    st.markdown("### 3. Process Priorities & Recovery Costs")
    col_pri, col_cost = st.columns(2)

    with col_pri:
        st.markdown("**Process Priorities (Lower number = lower importance / first victim):**")
        pri_dict = {p: state.priorities.get(p, 1) for p in process_ids}
        df_pri = pd.DataFrame([pri_dict], index=["Priority"])
        edited_pri = st.data_editor(df_pri, use_container_width=True, key="edit_pri")
        new_priorities = {p: int(edited_pri.iloc[0][p]) for p in process_ids}

    with col_cost:
        st.markdown("**Termination / Restart Costs:**")
        cost_dict = {p: state.costs.get(p, 10.0) for p in process_ids}
        df_cost = pd.DataFrame([cost_dict], index=["Cost ($)"])
        edited_cost = st.data_editor(df_cost, use_container_width=True, key="edit_cost")
        new_costs = {p: float(edited_cost.iloc[0][p]) for p in process_ids}

    st.markdown("---")

    # Construct candidate state
    candidate_state = SystemState(
        process_ids=process_ids,
        resource_ids=resource_ids,
        total=new_total,
        available=new_available,
        allocation=new_alloc,
        maximum=new_max,
        request=new_req,
        priorities=new_priorities,
        costs=new_costs,
        terminated={p: state.terminated.get(p, False) for p in process_ids},
    )

    # Live Validation Status
    is_valid, errors = validate_system_state(candidate_state)

    st.markdown("### 4. Validation & Commit")
    if is_valid:
        st.success("✅ **Scenario is structurally and mathematically consistent!** (No conservation violations).")
        col_act1, col_act2, col_act3 = st.columns([1, 1, 2])
        with col_act1:
            if st.button("💾 Apply & Update Scenario", type="primary", use_container_width=True):
                set_current_state(candidate_state, log_message="Custom scenario parameters updated.")
                st.toast("Scenario updated successfully!", icon="✅")
                st.rerun()
    else:
        st.error(f"❌ **Validation Errors Found ({len(errors)}):**")
        for err in errors:
            st.warning(f"• {err}")
        st.caption("Fix the highlighted errors above to commit the state.")

    # Export / Import Expandable
    with st.expander("📥 Export / Import Scenario Data (JSON & CSV)"):
        ex_col1, ex_col2 = st.columns(2)
        with ex_col1:
            st.markdown("#### Export Current Scenario")
            json_data = export_state_json(state)
            st.download_button(
                label="⬇️ Download Scenario JSON",
                data=json_data,
                file_name="deadlock_scenario.json",
                mime="application/json",
                use_container_width=True,
            )
            # CSV export
            csv_alloc = df_alloc.to_csv()
            st.download_button(
                label="⬇️ Download Allocation Matrix CSV",
                data=csv_alloc,
                file_name="allocation_matrix.csv",
                mime="text/csv",
                use_container_width=True,
            )

        with ex_col2:
            st.markdown("#### Import Scenario from JSON")
            uploaded_file = st.file_uploader("Upload JSON Scenario File", type=["json"])
            if uploaded_file is not None:
                try:
                    content = uploaded_file.read().decode("utf-8")
                    imported_state = import_state_json(content)
                    valid_imp, imp_errs = validate_system_state(imported_state)
                    if valid_imp:
                        set_current_state(imported_state, log_message="Imported custom scenario from JSON file.")
                        st.success("Successfully imported and loaded scenario!")
                        st.rerun()
                    else:
                        st.error(f"Uploaded scenario failed validation: {imp_errs}")
                except Exception as e:
                    st.error(f"Failed to parse JSON file: {e}")
