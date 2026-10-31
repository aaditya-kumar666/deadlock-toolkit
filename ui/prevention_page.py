"""
UI Module: Deadlock Prevention Sandbox & Academic Analysis.
Demonstrates Havender's linear resource ordering, Hold-and-Wait protocols,
and comprehensive trade-off comparisons.
"""

import streamlit as st
import pandas as pd
from ui.state_manager import get_current_state
from core.prevention import (
    verify_resource_ordering,
    verify_hold_and_wait_protocol_a,
    verify_hold_and_wait_protocol_b,
    get_default_resource_ordering,
    get_prevention_tradeoffs_matrix,
)


def render_prevention_page():
    """Renders the prevention analysis and interactive protocol testers."""
    state = get_current_state()

    st.markdown("## 🛡️ Deadlock Prevention Sandbox")
    st.markdown(
        "*Deadlock Prevention restrains how requests can be made by invalidating at least one of Coffman's four necessary conditions.*"
    )

    with st.expander("📖 The Four Necessary Coffman Conditions (OS Theory)", expanded=False):
        st.markdown("""
        For a deadlock to occur, all four conditions must hold simultaneously:
        1. **Mutual Exclusion:** At least one resource must be held in a non-shareable mode.
        2. **Hold and Wait:** A process must currently hold at least one resource and be waiting to acquire additional resources held by other processes.
        3. **No Preemption:** Resources cannot be forcibly preempted from a process; they can only be released voluntarily after completion.
        4. **Circular Wait:** A closed chain of processes exists: $P_0$ waits for $P_1$, $P_1$ waits for $P_2$, ..., and $P_k$ waits for $P_0$.
        """)

    tab_order, tab_hw, tab_tradeoffs = st.tabs([
        "🔢 Havender's Resource Ordering (Circular Wait)",
        "⏳ Hold-and-Wait Prevention Protocols",
        "⚖️ Architectural Trade-off Matrix",
    ])

    # -------------------------------------------------------------
    # TAB 1: Resource Ordering
    # -------------------------------------------------------------
    with tab_order:
        st.markdown("### Havender's Scheme: Total Linear Ordering")
        st.caption(
            "Mathematical Invalidation of Circular Wait: Define a one-to-one function F: R -> N. "
            "A process may request R_j only if F(R_j) > F(R_i) for all resources R_i currently held."
        )

        st.info("""
        **Proof of Correctness:**
        Assume a circular wait exists: $P_0 \\to R_1 \\to P_1 \\to R_2 \\dots \\to P_k \\to R_0 \\to P_0$.
        Under Havender's rule, this requires:
        $F(R_0) < F(R_1) < F(R_2) < \\dots < F(R_k) < F(R_0)$.
        This implies $F(R_0) < F(R_0)$, which is impossible! Hence, Circular Wait cannot exist.
        """)

        st.markdown("#### Interactive Ordering Rule Tester")
        col_ord1, col_ord2 = st.columns(2)

        # Configurable linear order
        with col_ord1:
            st.markdown("**1. Configure Resource Ordering Function F(R):**")
            default_ordering = get_default_resource_ordering(state.resource_ids)
            order_inputs = {}
            for rid in state.resource_ids:
                val = st.number_input(
                    f"Order F({rid})",
                    min_value=1,
                    max_value=100,
                    value=default_ordering.get(rid, 1),
                    key=f"ord_{rid}",
                )
                order_inputs[rid] = int(val)

        with col_ord2:
            st.markdown("**2. Simulate Process Request Against Order:**")
            active_pids = [p for p in state.process_ids if not state.terminated.get(p, False)]
            test_pid = st.selectbox("Select Process:", options=active_pids, key="prev_ord_pid")
            p_idx = state.process_ids.index(test_pid)

            # Resources currently held with count > 0
            held_rids = [
                state.resource_ids[j] 
                for j in range(state.num_resources) 
                if state.allocation[p_idx][j] > 0
            ]
            st.markdown(f"**Currently Held by `{test_pid}`:** `{held_rids}` (Allocation: `{state.allocation[p_idx]}`)")

            test_rid = st.selectbox("Resource to Request:", options=state.resource_ids, key="prev_ord_rid")

            if st.button("🧪 Check Ordering Compliance", type="primary"):
                compliant, explanation = verify_resource_ordering(held_rids, test_rid, order_inputs)
                if compliant:
                    st.success(f"✅ {explanation}")
                else:
                    st.error(f"❌ {explanation}")

    # -------------------------------------------------------------
    # TAB 2: Hold-and-Wait Protocols
    # -------------------------------------------------------------
    with tab_hw:
        st.markdown("### Hold-and-Wait Prevention Protocols")
        st.caption(
            "To prevent the Hold-and-Wait condition, the OS must guarantee that when a process requests resources, "
            "it does not hold any other resources."
        )

        col_p_a, col_p_b = st.columns(2)

        with col_p_a:
            st.markdown("#### Protocol A: Conservative (All-at-Once)")
            st.markdown(
                "A process must request and receive **all** required resources before execution begins. "
                "Incremental acquisition is rejected."
            )
            p_a_held = st.number_input("Currently held resources by process", min_value=0, max_value=10, value=0, key="hw_a_held")
            p_a_is_initial = st.checkbox("Is this the initial startup batch?", value=True, key="hw_a_init")

            if st.button("Test Protocol A", key="btn_test_hw_a"):
                ok, msg = verify_hold_and_wait_protocol_a(p_a_held, p_a_is_initial)
                if ok:
                    st.success(f"✅ {msg}")
                else:
                    st.error(f"❌ {msg}")

        with col_p_b:
            st.markdown("#### Protocol B: Release-Before-Request")
            st.markdown(
                "A process may request resources only when it currently holds **zero** resources. "
                "It must release all held resources before asking for new ones."
            )
            p_b_held = st.number_input("Currently held resources by process", min_value=0, max_value=10, value=1, key="hw_b_held")
            p_b_req = st.number_input("New requested amount", min_value=1, max_value=10, value=1, key="hw_b_req")

            if st.button("Test Protocol B", key="btn_test_hw_b"):
                ok, msg = verify_hold_and_wait_protocol_b(p_b_held, p_b_req)
                if ok:
                    st.success(f"✅ {msg}")
                else:
                    st.error(f"❌ {msg}")

    # -------------------------------------------------------------
    # TAB 3: Trade-off Comparison
    # -------------------------------------------------------------
    with tab_tradeoffs:
        st.markdown("### Architectural Trade-Off Analysis")
        st.markdown(
            "*Comparing Prevention, Avoidance, and Detection across overhead, resource utilization, and operational constraints.*"
        )
        tradeoffs = get_prevention_tradeoffs_matrix()
        st.dataframe(pd.DataFrame(tradeoffs), use_container_width=True, hide_index=True)
