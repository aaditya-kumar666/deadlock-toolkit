"""
UI Module: Algorithm Analysis Engine.
Visualizes Banker's Algorithm (Avoidance), interactive step-by-step stepper,
resource request simulator with rollback, and multi-instance deadlock detection traces.
"""

import streamlit as st
import pandas as pd
from ui.state_manager import get_current_state, set_current_state
from core.bankers import is_safe_state, simulate_resource_request, find_all_safe_sequences
from core.detection import detect_deadlock_multiple_instances


def render_analysis_page():
    """Renders the algorithm analysis, traces, and request simulator."""
    state = get_current_state()

    st.markdown("## 🔬 Deadlock Avoidance & Detection Analysis")
    st.markdown(
        "*Inspect step-by-step algorithm traces, simulate tentative resource requests with rollback, and evaluate actual deadlocks.*"
    )

    tab_banker, tab_request, tab_detect = st.tabs([
        "🛡️ Banker's Safety Algorithm",
        "⚡ Resource Request Simulator",
        "🔍 Multi-Instance Deadlock Detection",
    ])

    # -------------------------------------------------------------
    # TAB 1: Banker's Algorithm
    # -------------------------------------------------------------
    with tab_banker:
        st.markdown("### Dijkstra's Banker's Safety Evaluation")
        st.caption(
            "Avoidance Principle: At any point, the system is in a **Safe State** if there exists at least one "
            "execution sequence <P_1, P_2, ..., P_n> such that for each P_i, the maximum resources P_i may still need "
            "can be satisfied by current Available plus resources held by prior processes."
        )

        safety = is_safe_state(state, find_all=True)

        if safety.is_safe:
            st.success(f"✅ **SAFE STATE CONFIRMED**: {safety.message}")
            st.markdown(f"**Primary Safe Sequence:** `{' ➔ '.join(safety.safe_sequence)}`")

            if safety.all_safe_sequences and len(safety.all_safe_sequences) > 1:
                with st.expander(f"✨ View All Safe Sequences ({len(safety.all_safe_sequences)} found)"):
                    for idx, seq in enumerate(safety.all_safe_sequences, 1):
                        st.markdown(f"{idx}. `{' ➔ '.join(seq)}`")
        else:
            st.error(f"⚠️ **UNSAFE STATE DETECTED**: {safety.message}")
            st.warning(
                "An Unsafe State is NOT necessarily a deadlock right now, but the operating system cannot "
                "guarantee process completion under worst-case demand. Processes that could not be satisfied: "
                f"**{safety.unresolved_processes}**."
            )

        st.markdown("---")
        st.markdown("### 🪜 Interactive Step-by-Step Algorithm Stepper")

        traces = safety.trace
        if traces:
            max_step = len(traces)
            step_idx = st.slider(
                "Navigate Execution Step:",
                min_value=1,
                max_value=max_step,
                value=min(st.session_state.get("banker_step_idx", 1), max_step),
                key="stepper_slider",
            )
            st.session_state["banker_step_idx"] = step_idx

            current_trace = traces[step_idx - 1]

            col_s1, col_s2 = st.columns([1, 2])
            with col_s1:
                st.markdown(f"#### Step {current_trace.step_number}: Process `{current_trace.process_id}`")
                if current_trace.can_finish:
                    st.success("✅ **Status: Satisfied / Can Finish**")
                else:
                    st.error("❌ **Status: Blocked / Cannot Finish**")

                st.markdown(f"**Current Work:** `{current_trace.work_vector}`")
                st.markdown(f"**Remaining Need:** `{current_trace.requirement_vector}`")
                st.markdown(f"**Allocated (Reclaimed):** `{current_trace.allocated_resources}`")
                st.markdown(f"**Updated Work:** `{current_trace.new_work_vector}`")

            with col_s2:
                st.markdown("#### Educational Explanation")
                st.info(current_trace.explanation)

            st.markdown("---")
            with st.expander("📋 View Complete Trace Table", expanded=False):
                trace_rows = []
                for t in traces:
                    trace_rows.append({
                        "Step": t.step_number,
                        "Process": t.process_id,
                        "Work (Before)": str(t.work_vector),
                        "Need": str(t.requirement_vector),
                        "Can Finish?": "YES" if t.can_finish else "NO",
                        "Allocated Released": str(t.allocated_resources),
                        "Work (After)": str(t.new_work_vector),
                    })
                st.dataframe(pd.DataFrame(trace_rows), use_container_width=True, hide_index=True)

    # -------------------------------------------------------------
    # TAB 2: Resource Request Simulator
    # -------------------------------------------------------------
    with tab_request:
        st.markdown("### ⚡ Resource Request & Rollback Simulator")
        st.caption(
            "Simulates dynamic resource requests. The algorithm tentatively allocates requested resources, "
            "verifies system safety using the safety algorithm, and commits only if safe. If unsafe, it triggers an "
            "immediate rollback to ensure deadlock avoidance."
        )

        col_req1, col_req2 = st.columns([1, 2])
        active_processes = [p for p in state.process_ids if not state.terminated.get(p, False)]

        with col_req1:
            req_pid = st.selectbox("Select Requesting Process:", options=active_processes)
            p_idx = state.process_ids.index(req_pid)
            need_vec = state.get_need_matrix()[p_idx]
            alloc_vec = state.allocation[p_idx]
            max_vec = state.maximum[p_idx]

            st.markdown(f"**Current Allocation:** `{alloc_vec}`")
            st.markdown(f"**Declared Maximum:** `{max_vec}`")
            st.markdown(f"**Remaining Need:** `{need_vec}`")
            st.markdown(f"**System Available:** `{state.available}`")

        with col_req2:
            st.markdown(f"**Enter Resource Request Vector for `{req_pid}`:**")
            req_cols = st.columns(state.num_resources)
            input_request = []
            for j, rid in enumerate(state.resource_ids):
                with req_cols[j]:
                    val = st.number_input(
                        f"Req {rid}",
                        min_value=0,
                        max_value=state.total[j],
                        value=0,
                        key=f"req_in_{rid}",
                    )
                    input_request.append(int(val))

            st.write("")
            btn_eval = st.button("🧪 Evaluate & Simulate Request", type="primary", use_container_width=True)

        if btn_eval:
            eval_res = simulate_resource_request(state, req_pid, input_request)

            st.markdown("---")
            st.markdown("#### Evaluation Results")

            if not eval_res.is_valid:
                st.error(f"❌ **Invalid Request:** {eval_res.reason}")
            elif not eval_res.can_grant:
                st.warning(f"⏳ **Process Must Wait:** {eval_res.reason}")
            elif eval_res.is_safe:
                st.success(f"🎉 **Request Granted Safely!**\n\n{eval_res.reason}")
                if eval_res.provisional_state is not None:
                    col_commit, _ = st.columns([1, 3])
                    with col_commit:
                        if st.button("💾 Commit Allocation to State", type="primary", key="btn_commit_grant"):
                            set_current_state(
                                eval_res.provisional_state,
                                log_message=f"Granted request {input_request} to {req_pid}."
                            )
                            st.toast("Request committed to state!", icon="✅")
                            st.rerun()
            else:
                st.error(f"⛔ **Request Rejected (Rollback Triggered):**\n\n{eval_res.reason}")
                st.info("The provisional allocation was safely undone. No changes were made to the system.")

    # -------------------------------------------------------------
    # TAB 3: Deadlock Detection
    # -------------------------------------------------------------
    with tab_detect:
        st.markdown("### 🔍 Multiple-Instance Deadlock Detection Algorithm")
        st.caption(
            "Detection vs Avoidance: Deadlock detection does NOT inspect maximum claims. "
            "Instead, it evaluates whether the current outstanding requests (Request Matrix Q) "
            "can be satisfied with current Available resources."
        )

        det_result = detect_deadlock_multiple_instances(state)

        if det_result.is_deadlocked:
            st.error(f"🚨 **DEADLOCK DETECTED!** {det_result.message}")
            st.markdown(f"**Deadlocked Processes:** `{det_result.deadlocked_processes}`")
            st.warning("Navigate to the **Deadlock Recovery** page to select victim processes and break the deadlock.")
        else:
            st.success("✅ **NO DEADLOCK DETECTED:** All processes can either finish or hold zero blocking resources.")

        st.markdown("---")
        st.markdown("#### Detection Algorithm Step Trace")
        det_traces = det_result.trace
        if det_traces:
            trace_table = []
            for t in det_traces:
                trace_table.append({
                    "Step": t.step_number,
                    "Process(es)": t.process_id,
                    "Work (Before)": str(t.work_vector),
                    "Request": str(t.requirement_vector),
                    "Can Proceed?": "YES" if t.can_finish else "NO (BLOCKED)",
                    "Allocated Freed": str(t.allocated_resources),
                    "Work (After)": str(t.new_work_vector),
                    "Explanation": t.explanation,
                })
            st.dataframe(pd.DataFrame(trace_table), use_container_width=True, hide_index=True)
