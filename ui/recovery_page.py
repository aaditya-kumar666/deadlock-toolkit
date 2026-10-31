"""
UI Module: Deadlock Recovery Workbench.
Simulates victim selection, safe educational resource reclamation,
and iterative detection re-evaluation.
"""

import streamlit as st
import pandas as pd
from ui.state_manager import get_current_state, set_current_state
from core.models import RecoveryPolicy
from core.detection import detect_deadlock_multiple_instances
from core.recovery import execute_recovery_step, run_full_recovery_loop
from visualization.charts import create_recovery_audit_chart


def render_recovery_page():
    """Renders the interactive recovery interface and audit logs."""
    state = get_current_state()

    st.markdown("## 🚨 Deadlock Recovery Workbench")
    st.markdown(
        "*Break deadlocks through simulated process termination and resource reclamation using priority, cost, or heuristic policies.*"
    )

    st.info(
        "🛡️ **Educational Safety Notice:** Process termination and resource release operate strictly on the simulated "
        "in-memory data model. No real host operating system processes are affected."
    )

    det = detect_deadlock_multiple_instances(state)

    if not det.is_deadlocked:
        st.success("✅ **SYSTEM IS DEADLOCK-FREE**: No processes are deadlocked. Recovery actions are not required.")
    else:
        st.error(f"🚨 **ACTIVE DEADLOCK DETECTED**: {len(det.deadlocked_processes)} process(es) deadlocked: `{det.deadlocked_processes}`.")

        # Deadlocked process breakdown
        dead_rows = []
        for pid in det.deadlocked_processes:
            idx = state.process_ids.index(pid)
            dead_rows.append({
                "Process": pid,
                "Priority": state.priorities.get(pid, 1),
                "Cost ($)": state.costs.get(pid, 10.0),
                "Currently Allocated": str(state.allocation[idx]),
                "Outstanding Request": str(state.request[idx]),
            })
        st.dataframe(pd.DataFrame(dead_rows), use_container_width=True, hide_index=True)

        st.markdown("---")
        st.markdown("### Victim Selection & Termination Policies")

        c_pol1, c_pol2 = st.columns([2, 1])

        with c_pol1:
            policy_options = [
                RecoveryPolicy.LOWEST_PRIORITY.value,
                RecoveryPolicy.LOWEST_COST.value,
                RecoveryPolicy.MAX_RESOURCES.value,
                RecoveryPolicy.MANUAL.value,
            ]
            selected_policy_str = st.radio(
                "Select Victim Selection Policy:",
                options=policy_options,
                index=0,
                horizontal=True,
            )
            policy_enum = RecoveryPolicy(selected_policy_str)

        manual_victim = None
        if policy_enum == RecoveryPolicy.MANUAL:
            with c_pol2:
                manual_victim = st.selectbox(
                    "Select Process to Terminate Manually:",
                    options=det.deadlocked_processes,
                )

        st.markdown("---")
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])

        with col_btn1:
            if st.button("⚡ Execute Single Step", type="primary", use_container_width=True):
                step_idx = len(st.session_state["recovery_history"]) + 1
                new_state, action = execute_recovery_step(
                    state, policy_enum, step_number=step_idx, manual_choice=manual_victim
                )
                if action is not None:
                    set_current_state(new_state)
                    st.session_state["recovery_history"].append(action)
                    st.toast(f"Terminated {action.victim_process_id} and reclaimed {action.reclaimed_resources}!", icon="⚡")
                    st.rerun()

        with col_btn2:
            if st.button("🔁 Auto-Recover All", use_container_width=True):
                new_state, actions, is_free = run_full_recovery_loop(state, policy_enum)
                set_current_state(new_state)
                st.session_state["recovery_history"].extend(actions)
                if is_free:
                    st.success("System completely recovered from deadlock!")
                st.rerun()

    # Recovery History and Audit Section
    st.markdown("---")
    st.markdown("### 📜 Recovery Audit Trail & Metrics")

    history = st.session_state.get("recovery_history", [])

    if history:
        col_hist_chart, col_hist_table = st.columns([1, 1])

        with col_hist_chart:
            fig_hist = create_recovery_audit_chart(history)
            st.plotly_chart(fig_hist, use_container_width=True)

        with col_hist_table:
            hist_rows = []
            for a in history:
                hist_rows.append({
                    "Step": a.step,
                    "Victim": a.victim_process_id,
                    "Policy": a.policy_used,
                    "Cost": a.cost,
                    "Priority": a.priority,
                    "Reclaimed": str(a.reclaimed_resources),
                    "Deadlock After?": "YES" if a.is_deadlocked_after else "NO (FREE)",
                    "Rationale": a.rationale,
                })
            st.dataframe(pd.DataFrame(hist_rows), use_container_width=True, hide_index=True)

        if st.button("🧹 Clear Recovery Audit History"):
            st.session_state["recovery_history"] = []
            st.rerun()
    else:
        st.caption("No simulated terminations performed in this session yet.")
