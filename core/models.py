"""
Data models and structural representations for the Deadlock Toolkit.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional, Any
import copy


class ProcessStatus(str, Enum):
    """Lifecycle status of a process in the simulation."""
    RUNNABLE = "RUNNABLE"
    WAITING = "WAITING"
    DEADLOCKED = "DEADLOCKED"
    TERMINATED = "TERMINATED"


class RecoveryPolicy(str, Enum):
    """Supported automatic victim selection policies."""
    LOWEST_PRIORITY = "Lowest Priority"
    LOWEST_COST = "Lowest Termination Cost"
    MAX_RESOURCES = "Max Reclaimed Resources"
    MANUAL = "Manual Selection"


@dataclass
class StepTrace:
    """Detailed record of a single step in Banker's safety check or deadlock detection."""
    step_number: int
    process_id: str
    work_vector: List[int]
    requirement_vector: List[int]  # Need vector in Banker's, Request vector in Detection
    can_finish: bool
    allocated_resources: List[int]
    new_work_vector: List[int]
    explanation: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "step_number": self.step_number,
            "process_id": self.process_id,
            "work_vector": list(self.work_vector),
            "requirement_vector": list(self.requirement_vector),
            "can_finish": self.can_finish,
            "allocated_resources": list(self.allocated_resources),
            "new_work_vector": list(self.new_work_vector),
            "explanation": self.explanation,
        }


@dataclass
class SafetyResult:
    """Result of Banker's Algorithm safety evaluation."""
    is_safe: bool
    safe_sequence: List[str]
    all_safe_sequences: List[List[str]] = field(default_factory=list)
    trace: List[StepTrace] = field(default_factory=list)
    unresolved_processes: List[str] = field(default_factory=list)
    message: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_safe": self.is_safe,
            "safe_sequence": self.safe_sequence,
            "all_safe_sequences": self.all_safe_sequences,
            "trace": [t.to_dict() for t in self.trace],
            "unresolved_processes": self.unresolved_processes,
            "message": self.message,
        }


@dataclass
class RequestEvaluation:
    """Result of evaluating and tentatively simulating a resource request."""
    is_valid: bool
    can_grant: bool
    is_safe: bool
    reason: str
    safe_sequence: List[str] = field(default_factory=list)
    provisional_state: Optional[SystemState] = None
    trace: List[StepTrace] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "can_grant": self.can_grant,
            "is_safe": self.is_safe,
            "reason": self.reason,
            "safe_sequence": self.safe_sequence,
            "trace": [t.to_dict() for t in self.trace],
        }


@dataclass
class DetectionResult:
    """Result of deadlock detection."""
    is_deadlocked: bool
    deadlocked_processes: List[str]
    trace: List[StepTrace] = field(default_factory=list)
    cycles: List[List[str]] = field(default_factory=list)
    message: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_deadlocked": self.is_deadlocked,
            "deadlocked_processes": self.deadlocked_processes,
            "trace": [t.to_dict() for t in self.trace],
            "cycles": self.cycles,
            "message": self.message,
        }


@dataclass
class RecoveryAction:
    """Audit record of a recovery step terminating a process to break deadlock."""
    step: int
    victim_process_id: str
    policy_used: str
    cost: float
    priority: int
    reclaimed_resources: List[int]
    was_deadlocked_before: bool
    is_deadlocked_after: bool
    remaining_deadlocked: List[str]
    rationale: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "step": self.step,
            "victim_process_id": self.victim_process_id,
            "policy_used": self.policy_used,
            "cost": self.cost,
            "priority": self.priority,
            "reclaimed_resources": list(self.reclaimed_resources),
            "was_deadlocked_before": self.was_deadlocked_before,
            "is_deadlocked_after": self.is_deadlocked_after,
            "remaining_deadlocked": self.remaining_deadlocked,
            "rationale": self.rationale,
        }


@dataclass
class SystemState:
    """
    Complete state representation of the simulated operating system.
    
    Matrices and vectors:
    - total: Vector E of length m (Total capacity per resource type)
    - available: Vector A of length m (Unallocated instances available)
    - allocation: Matrix C of size n x m (Currently allocated instances)
    - maximum: Matrix M of size n x m (Maximum declared claim for Banker's)
    - request: Matrix Q of size n x m (Outstanding requests for Detection)
    """
    process_ids: List[str]
    resource_ids: List[str]
    total: List[int]
    available: List[int]
    allocation: List[List[int]]
    maximum: List[List[int]]
    request: List[List[int]]
    priorities: Dict[str, int] = field(default_factory=dict)
    costs: Dict[str, float] = field(default_factory=dict)
    terminated: Dict[str, bool] = field(default_factory=dict)

    def __post_init__(self):
        # Initialize default priorities (1 = lowest, higher is more important)
        for pid in self.process_ids:
            if pid not in self.priorities:
                self.priorities[pid] = 1
            if pid not in self.costs:
                self.costs[pid] = 10.0
            if pid not in self.terminated:
                self.terminated[pid] = False

    @property
    def num_processes(self) -> int:
        return len(self.process_ids)

    @property
    def num_resources(self) -> int:
        return len(self.resource_ids)

    def get_need_matrix(self) -> List[List[int]]:
        """
        Calculates Need matrix = Maximum - Allocation.
        For terminated processes, need is zero.
        """
        need = []
        for i, pid in enumerate(self.process_ids):
            if self.terminated.get(pid, False):
                need.append([0] * self.num_resources)
            else:
                row = [self.maximum[i][j] - self.allocation[i][j] for j in range(self.num_resources)]
                need.append(row)
        return need

    def clone(self) -> SystemState:
        """Deep copy of the current state."""
        return copy.deepcopy(self)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize state to standard dictionary."""
        return {
            "process_ids": list(self.process_ids),
            "resource_ids": list(self.resource_ids),
            "total": list(self.total),
            "available": list(self.available),
            "allocation": [list(r) for r in self.allocation],
            "maximum": [list(r) for r in self.maximum],
            "request": [list(r) for r in self.request],
            "priorities": dict(self.priorities),
            "costs": dict(self.costs),
            "terminated": dict(self.terminated),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> SystemState:
        """Reconstruct state from serialized dictionary."""
        return cls(
            process_ids=list(data["process_ids"]),
            resource_ids=list(data["resource_ids"]),
            total=list(data["total"]),
            available=list(data["available"]),
            allocation=[list(r) for r in data["allocation"]],
            maximum=[list(r) for r in data["maximum"]],
            request=[list(r) for r in data.get("request", [[0] * len(data["resource_ids"])] * len(data["process_ids"]))],
            priorities=dict(data.get("priorities", {})),
            costs=dict(data.get("costs", {})),
            terminated=dict(data.get("terminated", {})),
        )
