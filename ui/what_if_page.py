"""
UI Module: What-If Comparative Analyzer.
Enables side-by-side comparative analysis of state perturbations (Available vector changes,
allocation adjustments) and dynamic recalculation of Banker's and detection algorithms.
"""

import streamlit as st
import pandas as pd
from ui.state_manager import get_current_state, set_current_state
from core.bankers import is_safe_state
from core.detection import detect_deadlock_multiple_instances
from core.validation import validate_system_state


def render_what_if_page():
    """Renders the What-If analysis comparison workbench."""
    base_state = get_current_state()

    st.markdown("## 🔮 Dynamic What-If Analysis")
    st.markdown(
        "*Perturb available resources or allocations to observe real-time algorithmic transitions between Safe, Unsafe, and Deadlocked states.*"
    )

    st.markdown("### 1. Perturb System Parameters")
    st.caption("Adjust available resource quantities to simulate dynamic resource addition/subtraction:")

    mod_available = []
    avail_cols = st.columns(base_state.num_resources)

    for j, rid in enumerate(base_state.resource_ids):
        with avail_cols[j]:
            base_val = base_state.available[j]
            new_val = st.number_input(
                f"Available {rid}",
                min_value=0,
                max_value=base_state.total[j] + 20,
                value=base_val,
                key=f"whatif_avail_{rid}",
                help=f"Baseline: {base_val} units",
            )
            mod_available.append(int(new_val))

    # Construct candidate perturbed state
    # Adjust total to preserve Total = Available + sum(Allocation)
    n = base_state.num_processes
    mod_total = []
    for j in range(base_state.num_resources):
        alloc_sum = sum(base_state.allocation[i][j] for i in range(n))
        mod_total.append(mod_available[j] + alloc_sum)

    perturbed_state = base_state.clone()
    perturbed_state.available = mod_available
    perturbed_state.total = mod_total

    # Validate perturbed state
    is_valid, errors = validate_system_state(perturbed_state)
    if not is_valid:
        st.error(f"Invalid perturbation: {errors}")
        return

    st.markdown("---")
    st.markdown("### 2. Side-by-Side Comparative Verdict")

    # Run evaluations on both
    safety_before = is_safe_state(base_state, find_all=False)
    safety_after = is_safe_state(perturbed_state, find_all=False)

    det_before = detect_deadlock_multiple_instances(base_state)
    det_after = detect_deadlock_multiple_instances(perturbed_state)

    col_before, col_after = st.columns(2)

    with col_before:
        st.markdown("#### 🏛️ Baseline Scenario")
        st.markdown(f"**Available Vector:** `{base_state.available}`")

        # Safety
        if safety_before.is_safe:
            st.success("Banker's: **SAFE STATE**")
            st.caption(f"Safe Sequence: `{' ➔ '.join(safety_before.safe_sequence)}`")
        else:
            st.error("Banker's: **UNSAFE STATE**")
            st.caption(f"Unresolved: `{safety_before.unresolved_processes}`")

        # Detection
        if det_before.is_deadlocked:
            st.error(f"Detection: **DEADLOCKED** ({len(det_before.deadlocked_processes)} processes)")
            st.caption(f"Deadlocked: `{det_before.deadlocked_processes}`")
        else:
            st.success("Detection: **DEADLOCK FREE**")

    with col_after:
        st.markdown("#### ⚡ Perturbed (What-If) Scenario")
        st.markdown(f"**Available Vector:** `{perturbed_state.available}`")

        # Safety
        if safety_after.is_safe:
            st.success("Banker's: **SAFE STATE**")
            st.caption(f"Safe Sequence: `{' ➔ '.join(safety_after.safe_sequence)}`")
        else:
            st.error("Banker's: **UNSAFE STATE**")
            st.caption(f"Unresolved: `{safety_after.unresolved_processes}`")

        # Detection
        if det_after.is_deadlocked:
            st.error(f"Detection: **DEADLOCKED** ({len(det_after.deadlocked_processes)} processes)")
            st.caption(f"Deadlocked: `{det_after.deadlocked_processes}`")
        else:
            st.success("Detection: **DEADLOCK FREE**")

    st.markdown("---")

    # Comparison summary table
    st.markdown("#### 📊 Metric Delta Summary")
    delta_rows = [
        {
            "Metric": "Total Available Units",
            "Baseline": sum(base_state.available),
            "What-If": sum(perturbed_state.available),
            "Difference": f"{sum(perturbed_state.available) - sum(base_state.available):+d}",
        },
        {
            "Metric": "Avoidance State",
            "Baseline": "SAFE" if safety_before.is_safe else "UNSAFE",
            "What-If": "SAFE" if safety_after.is_safe else "UNSAFE",
            "Difference": "Improved" if (not safety_before.is_safe and safety_after.is_safe) else ("Degraded" if (safety_before.is_safe and not safety_after.is_safe) else "Unchanged"),
        },
        {
            "Metric": "Deadlocked Processes",
            "Baseline": len(det_before.deadlocked_processes),
            "What-If": len(det_after.deadlocked_processes),
            "Difference": f"{len(det_after.deadlocked_processes) - len(det_before.deadlocked_processes):+d}",
        },
    ]
    st.dataframe(pd.DataFrame(delta_rows), use_container_width=True, hide_index=True)

    col_apply, _ = st.columns([1, 2])
    with col_apply:
        if st.button("🚀 Apply What-If Parameters as Active Scenario", type="primary"):
            set_current_state(perturbed_state, log_message="Applied What-If parameters to active scenario.")
            st.toast("Active scenario updated with What-If settings!", icon="✅")
            st.rerun()
