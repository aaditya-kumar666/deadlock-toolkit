# Academic Project Report Guide: Deadlock Prevention and Recovery Toolkit

**Course:** CSE316 Operating Systems  
**Faculty / Department:** School of Computer Science and Engineering  
**Institution:** Lovely Professional University (LPU)  
**Project Title:** Deadlock Prevention and Recovery Toolkit  

---

## 1. Project Overview
* **Objective:** To build an interactive, academically rigorous laboratory toolkit that demonstrates operating system resource management, deadlock avoidance (Banker's Algorithm), deadlock detection (multi-instance and single-instance RAG), deadlock prevention (Havender's linear ordering and Hold-and-Wait protocols), and deadlock recovery (victim selection by priority, cost, and heuristics).
* **Scope & Educational Safety:** The project is an educational simulator operating entirely on an in-memory mathematical model. It does not terminate actual host OS processes or alter real system resources.
* **Target Audience:** Undergraduate computer science students and instructors in operating systems courses.

---

## 2. Module-Wise Breakdown
The architecture is structured into exactly three main modules:
* **Module 1: Deadlock Analysis Engine**
  * `core/models.py`: Structural data models (`SystemState`, `StepTrace`, `SafetyResult`, `DetectionResult`).
  * `core/validation.py`: Matrix dimension checks, non-negative constraints, claim bounds, and resource conservation law verification.
  * `core/bankers.py`: Need matrix computation ($N = M - C$), safe-state checking, safe sequence generation (single and all sequences), and tentative resource request simulation with rollback.
  * `core/detection.py`: Multi-instance matrix reduction detection and NetworkX-based single-instance RAG cycle detection.
* **Module 2: Prevention and Recovery Engine**
  * `core/prevention.py`: Static enforcement of Havender's linear resource ordering $F: R \to \mathbb{N}$ to prevent Circular Wait; Hold-and-Wait Protocol A (all-at-once allocation) and Protocol B (release-before-request).
  * `core/recovery.py`: Simulated victim termination, resource reclamation ($\text{Available} \mathrel{+}= \text{Allocation}[\text{victim}]$), policy selection (Lowest Priority, Lowest Cost, Max Resources Reclaimed, Manual), and multi-step iterative recovery loop.
  * `core/scenarios.py`: 5 internally consistent, academically sound presets.
* **Module 3: Interactive Simulation and Visualization**
  * `visualization/resource_graph.py`: NetworkX bipartite RAG and interactive Plotly visualization with cycle highlighting.
  * `visualization/charts.py`: Resource utilization stacked bar charts, recovery audit charts, and simulator benchmark curves.
  * `ui/`: Modern Streamlit dashboard, custom scenario builder, analysis stepper, prevention sandbox, recovery workbench, What-If analyzer, and performance benchmark views.

---

## 3. Functionalities
1. **Interactive Dashboard:** Live OS status cards, dynamic RAG visualization, and quick matrix glance.
2. **Custom Scenario Builder:** Interactive matrix editor for allocation, max, request, priority, and cost with automatic Need calculation, conservation validation, and JSON/CSV import/export.
3. **Step-by-Step Algorithm Stepper:** Stepper allowing students to advance through each step of Banker's Algorithm and view Work, Need, and released allocations.
4. **Tentative Request Simulator:** Interactive resource request evaluation that tentatively modifies state, checks safety, and executes rollback if unsafe.
5. **Multi-Instance Deadlock Detection:** Matrix reduction algorithm evaluating actual outstanding requests $Q$ independently of Banker's Avoidance.
6. **Cycle vs Deadlock Demonstration:** Clarification that in single-instance systems, a cycle is necessary and sufficient; in multi-instance systems, a cycle is necessary but not sufficient.
7. **Prevention Sandbox:** Interactive tester verifying Havender's rule and Hold-and-Wait protocols with formal proof against circular wait.
8. **Automated & Manual Recovery Workbench:** Policy-driven victim selection and automatic iterative resolution with audit logs.
9. **What-If Analysis:** Side-by-side comparative analyzer for parameter perturbations.
10. **Simulator Performance Benchmarks:** Scalability curves testing execution time over process counts ($n=5$ to $100$) with explicit simulation disclaimers.

---

## 4. Technology Used
* **Programming Language:** Python 3 (Tested on Python 3.13)
* **Web Framework:** Streamlit (>= 1.30.0)
* **Graph Theory & Modeling:** NetworkX (>= 3.0)
* **Interactive Visualizations:** Plotly (>= 5.18.0)
* **Tabular Data & Numerical Processing:** Pandas (>= 2.0.0), NumPy (>= 1.24.0)
* **Automated Testing:** Pytest (>= 7.4.0)
* **Version Control:** Git (>= 2.40.0)
* **Operating System Target:** Local Windows environment (no external cloud services or paid APIs required).

---

## 5. Flow Diagram
*(Refer to `docs/flow_diagram.md` for complete high-resolution Mermaid diagrams)*:
1. Banker's Safety Algorithm Flowchart.
2. Resource-Request Simulation with Rollback Flowchart.
3. Multi-Instance Deadlock Detection Flowchart.
4. Deadlock Recovery Loop Flowchart.
5. Havender's Resource Ordering Rule Verification Flowchart.

---

## 6. Revision Tracking on GitHub
The project was developed following Git best practices with atomic commits:
* `723bd39`: `init: project scaffolding, requirements, and package architecture`
* `0834384`: `feat(core): data models and validation engine with non-negative checks and conservation laws`
* `4d952df`: `feat(core): Banker's algorithm with safe sequence generation and request rollback simulation`
* `eeecafb`: `feat(core): single and multi-instance deadlock detection with RAG cycle analysis`
* `a2935e9`: `feat(core): deadlock prevention engine with Havender's ordering and Hold-and-Wait protocols`
* `a1603df`: `feat(core): recovery engine with priority, cost, and heuristic victim selection`
* `78c7fde`: `feat(core): 5 validated scenario presets covering safe, unsafe, circular wait, multi-instance, and recovery`
* `2ac376f`: `feat(vis): NetworkX RAG generator, Plotly bipartite layout, and benchmark charts`
* `c9844d6`: `feat(ui): complete Streamlit dashboard, scenario builder, analysis, prevention, recovery, what-if, and benchmarks`

*(Note: Push instructions to GitHub remote are provided in Section 10 of README.md).*

---

## 7. Conclusion and Future Scope
* **Conclusion:** The toolkit successfully meets all academic requirements for the CSE316 Operating Systems course. It delivers a comprehensive platform for understanding the nuances of deadlock avoidance vs prevention vs detection, accompanied by interactive visualizations and automated tests.
* **Future Scope:**
  * Integration of real-time multi-threaded simulated process threads using Python's `threading` and `queue` primitives.
  * Dynamic priority aging to prevent starvation during repeated victim selection.
  * Support for distributed deadlock detection algorithms (e.g., Chandy-Misra-Haas edge-chasing).

---

## 8. References
1. Silberschatz, A., Galvin, P. B., & Gagne, G. *Operating System Concepts* (10th ed.). John Wiley & Sons, 2018. (Chapter 8: Deadlocks).
2. Dijkstra, E. W. *Cooperating Sequential Processes*. Technological University Eindhoven, 1965.
3. Havender, J. W. "Avoiding Deadlock in Multitasking Systems." *IBM Systems Journal*, 7(2), 74-84, 1968.
4. Coffman, E. G., Elphick, M., & Shoshani, A. "System Deadlocks." *ACM Computing Surveys*, 3(2), 67-78, 1971.

---

## Appendix A: AI-Guided Project Breakdown
* Explains the structured decomposition of requirements into three modules.
* Highlights the verification workflow: Research $\to$ Plan $\to$ Test-Driven Core $\to$ Visualization $\to$ Streamlit UI $\to$ Verification.

---

## Appendix B: Original Problem Statement
* Complete CSE316 problem statement requiring deadlock detection, avoidance (Banker's Algorithm), prevention, recovery, resource allocation graph visualization, and user-defined deadlock scenarios.

---

## Appendix C: Complete Source Code
* Index and reference to all repository source files:
  * `core/models.py`, `core/validation.py`, `core/bankers.py`, `core/detection.py`, `core/prevention.py`, `core/recovery.py`, `core/scenarios.py`
  * `visualization/resource_graph.py`, `visualization/charts.py`
  * `ui/state_manager.py`, `ui/dashboard.py`, `ui/scenario_builder.py`, `ui/analysis_page.py`, `ui/prevention_page.py`, `ui/recovery_page.py`, `ui/what_if_page.py`, `ui/benchmark_page.py`
  * `app.py`, `requirements.txt`, `tests/`
