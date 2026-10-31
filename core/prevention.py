"""
Module 2: Deadlock Prevention Engine.
Demonstrates static prevention techniques:
1. Havender's Resource Ordering (eliminating Circular Wait)
2. Hold-and-Wait Prevention (Protocol A: All-at-Once, Protocol B: Release-Before-Request)
Documents architectural trade-offs between Prevention, Avoidance, and Detection.
"""

from typing import List, Dict, Tuple, Any
from core.models import SystemState


def get_default_resource_ordering(resource_ids: List[str]) -> Dict[str, int]:
    """Generates a default linear ordering F(R_j) = 1, 2, 3... for each resource type."""
    return {rid: idx + 1 for idx, rid in enumerate(resource_ids)}


def verify_resource_ordering(
    currently_held_resources: List[str], 
    requested_resource: str, 
    ordering: Dict[str, int]
) -> Tuple[bool, str]:
    """
    Havender's Scheme: Imposes a total linear order F: R -> N on all resource types.
    Rule: A process can only request resource R_j if F(R_j) > F(R_i) for all R_i currently held.
    
    This mathematically guarantees that no circular wait can ever form.
    """
    if requested_resource not in ordering:
        return False, f"Resource '{requested_resource}' not found in ordering map."

    req_order = ordering[requested_resource]

    for held in currently_held_resources:
        if held not in ordering:
            continue
        held_order = ordering[held]
        if held_order >= req_order:
            return False, (
                f"RESOURCE ORDERING VIOLATION: Process holds '{held}' (Order {held_order}) "
                f"and attempted to request '{requested_resource}' (Order {req_order}). "
                f"Rule: F(requested) > F(held) is violated ({req_order} <= {held_order}). "
                f"This request is statically rejected to prevent Circular Wait."
            )

    return True, (
        f"RESOURCE ORDERING COMPLIANT: Requested resource '{requested_resource}' (Order {req_order}) "
        f"is strictly higher than all currently held resources."
    )


def verify_hold_and_wait_protocol_a(
    currently_allocated_count: int, 
    is_initial_batch_request: bool
) -> Tuple[bool, str]:
    """
    Hold-and-Wait Protocol A (Conservative / All-at-Once Allocation):
    A process must request and receive ALL its required resources at once before beginning execution.
    Incremental requests during execution are strictly prohibited.
    """
    if currently_allocated_count > 0:
        return False, (
            "HOLD-AND-WAIT VIOLATION (Protocol A): Process already holds allocated resources. "
            "Incremental resource acquisition is prohibited. "
            "All resources must be requested simultaneously before execution begins."
        )

    if not is_initial_batch_request:
        return False, (
            "HOLD-AND-WAIT VIOLATION (Protocol A): Request was marked as incremental rather than "
            "the complete initial execution batch."
        )

    return True, "HOLD-AND-WAIT COMPLIANT (Protocol A): Initial batch request allocated before execution."


def verify_hold_and_wait_protocol_b(
    total_currently_allocated: int, 
    requested_amount: int
) -> Tuple[bool, str]:
    """
    Hold-and-Wait Protocol B (Release-Before-Request):
    A process may request resources only when it currently holds NO resources at all.
    If it requires additional resources, it must first release all held resources.
    """
    if total_currently_allocated > 0:
        return False, (
            f"HOLD-AND-WAIT VIOLATION (Protocol B): Process currently holds {total_currently_allocated} "
            f"resource instances. It must release all held resources before issuing new requests."
        )

    if requested_amount <= 0:
        return False, "Requested amount must be greater than zero."

    return True, "HOLD-AND-WAIT COMPLIANT (Protocol B): Process holds zero resources; request permitted."


def get_prevention_tradeoffs_matrix() -> List[Dict[str, str]]:
    """Returns academic trade-off comparison matrix between prevention, avoidance, and detection."""
    return [
        {
            "Strategy": "Resource Ordering (Havender)",
            "Condition Targeted": "Circular Wait",
            "Mechanism": "Assign linear ordering F(R); enforce monotonic ascending requests",
            "Resource Utilization": "Moderate (limits request flexibility)",
            "Overhead": "Low (checked at compile time or request dispatch)",
            "Drawbacks / Limitations": "Severe inflexibility if process needs resources out of order; potential starvation for processes needing low-order resources.",
        },
        {
            "Strategy": "Hold-and-Wait (Protocol A)",
            "Condition Targeted": "Hold and Wait",
            "Mechanism": "Allocate all required resources upfront before execution starts",
            "Resource Utilization": "Very Low (resources reserved for entire runtime even if used briefly)",
            "Overhead": "Low",
            "Drawbacks / Limitations": "Severe resource underutilization; starvation of large-demand processes.",
        },
        {
            "Strategy": "Hold-and-Wait (Protocol B)",
            "Condition Targeted": "Hold and Wait",
            "Mechanism": "Process must release all held resources before requesting new ones",
            "Resource Utilization": "Low to Moderate",
            "Overhead": "Moderate (re-acquisition costs)",
            "Drawbacks / Limitations": "Waste of completed work if preempted/released; frequent re-requests; starvation.",
        },
        {
            "Strategy": "Banker's Algorithm (Avoidance)",
            "Condition Targeted": "Dynamically ensures circular wait cannot occur",
            "Mechanism": "Runtime safety evaluation on every request (Need = Max - Alloc)",
            "Resource Utilization": "High (resources granted whenever a safe sequence exists)",
            "Overhead": "High: O(m * n^2) complexity on every request",
            "Drawbacks / Limitations": "Requires advance knowledge of maximum resource claims; processes cannot increase claims dynamically.",
        },
        {
            "Strategy": "Deadlock Detection & Recovery",
            "Condition Targeted": "None (allows deadlock, then resolves)",
            "Mechanism": "Periodically run detection O(m * n^2); terminate victims or preempt resources",
            "Resource Utilization": "Highest (optimistic granting)",
            "Overhead": "Periodic detection overhead; recovery cost (lost process work)",
            "Drawbacks / Limitations": "Process termination costs; risk of starvation if same victim chosen repeatedly.",
        },
    ]
