# 🔒 DEADLOCK PREVENTION AND RECOVERY TOOLKIT

> **Academic Operating Systems Laboratory Project**  
> **Course:** CSE316 Operating Systems  
> **Institution:** Lovely Professional University (LPU)  
> **Author:** Aaditya Kumar | Aryan Singh
> **Environment:** Python 3 | Windows Compatible | Streamlit Dashboard  

---

## 📖 1. Project Overview

The **Deadlock Prevention and Recovery Toolkit** is an interactive, educational laboratory simulator built to demonstrate fundamental Operating Systems principles:
1. **Deadlock Avoidance:** Dijkstra's Banker's Algorithm with safe-sequence generation, interactive step-by-step traces, and resource request evaluation with automatic rollback.
2. **Deadlock Detection:** Multi-instance matrix reduction algorithm and NetworkX/Plotly directed Resource Allocation Graph (RAG) cycle analysis.
3. **Deadlock Prevention:** Static elimination of Coffman conditions using Havender's linear resource ordering and Hold-and-Wait protocols.
4. **Deadlock Recovery:** Simulated process termination with priority, cost, and reclaimed resource heuristic policies, safe resource release, and iterative detection cycles.

> 🛡️ **Educational Safety Notice:**  
> This application operates strictly on an in-memory simulated mathematical model. It does **not** inspect, terminate, or alter real operating system processes, kernel memory, or host resources.

---

## ✨ 2. Key Features

* **3-Module Decoupled Architecture:** Core algorithms are completely isolated from UI code for testing and academic clarity.
* **Interactive Resource Allocation Graph (RAG):**
  * Directed bipartite layout with process nodes (circles) and resource nodes (squares).
  * Real directed arrows for allocation edges ($R_j \to P_i$) and request edges ($P_i \to R_j$).
  * Dynamic highlighting of circular wait cycles in bright red.
* **Banker's Algorithm & Stepper:**
  * Computes Need matrix ($N = M - C$) automatically.
  * Evaluates safe states and finds all valid safe sequences via backtracking.
  * Interactive step-by-step stepper showing Work vectors, process Need, released allocations, and updated Work.
* **Resource Request Simulator with Rollback:**
  * Tentatively grants requests, tests system safety, commits if safe, and triggers immediate rollback if unsafe.
* **Deadlock Detection (Single & Multi-Instance):**
  * Demonstrates why a cycle is **necessary and sufficient** in single-instance systems, but **necessary and NOT sufficient** in multiple-instance systems.
* **Prevention Sandbox:**
  * Havender's linear resource ordering rule validator with mathematical proof.
  * Hold-and-Wait Protocol A (all-at-once) and Protocol B (release-before-request) testers.
* **Automated & Manual Recovery:**
  * Policies: Lowest Priority, Lowest Termination Cost, Max Reclaimed Resources, and Manual.
  * Iterative recovery loop terminating victims and re-evaluating until deadlock-free.
  * Full recovery audit trail with Plotly charts.
* **5 Academic Scenario Presets:**
  1. Safe System (Classic 5-process, 3-resource safe state).
  2. Unsafe System Without Proven Deadlock (Unsafe $\neq$ Deadlocked demonstration).
  3. Circular-Wait Deadlock (Single-instance 2-process knot).
  4. Multiple-Instance Cycle (Cycle exists, but NO deadlock exists).
  5. Recoverable Deadlock (Multi-process knot resolved through victim termination).
* **What-If Analysis:** Real-time side-by-side comparative analyzer for parameter perturbations.
* **Simulator Performance Benchmarks:** Scalability curves ($n=5$ to $100$) with explicit simulation disclaimers.
* **Data Export & Import:** Export scenario states to JSON or CSV; import custom JSON files.

---

## 🛠️ 3. Technology Stack

* **Language:** Python 3 (Python 3.13 tested)
* **Frontend UI:** Streamlit (`>= 1.30.0`)
* **Graph Modeling:** NetworkX (`>= 3.0`)
* **Visualization:** Plotly (`>= 5.18.0`)
* **Data Processing:** Pandas (`>= 2.0.0`), NumPy (`>= 1.24.0`)
* **Automated Testing:** Pytest (`>= 7.4.0`)
* **Version Control:** Git

---

## 📂 4. Project Folder Structure

```text
deadlock-toolkit/
├── app.py                          # Streamlit application entry point
├── requirements.txt                # Python package dependencies
├── README.md                       # Comprehensive project documentation
├── .gitignore                      # Git ignore rules for Python/Streamlit
│
├── core/                           # MODULE 1 & 2: Core Algorithmic Engines
│   ├── __init__.py
│   ├── models.py                   # SystemState, StepTrace, RecoveryAction dataclasses
│   ├── validation.py               # Conservation law, claim bounds, dimension checks
│   ├── bankers.py                  # Banker's safety check, safe sequences, request simulation
│   ├── detection.py                # Multi-instance detection, RAG cycle analysis
│   ├── prevention.py               # Havender's ordering, Hold-and-Wait protocols
│   ├── recovery.py                 # Victim selection policies, resource reclamation loop
│   └── scenarios.py                # 5 verified academic scenario presets
│
├── visualization/                  # VISUALIZATION ENGINE
│   ├── __init__.py
│   ├── resource_graph.py           # NetworkX RAG builder & Plotly interactive visualizer
│   └── charts.py                   # Utilization bars, recovery audit, runtime benchmark plots
│
├── ui/                             # MODULE 3: Streamlit User Interface
│   ├── __init__.py
│   ├── state_manager.py            # Streamlit session state & export/import
│   ├── dashboard.py                # Executive overview, metric cards, live RAG snapshot
│   ├── scenario_builder.py         # Dynamic matrix editor, Need computation, live errors
│   ├── analysis_page.py            # Banker's stepper, request simulator, detection trace
│   ├── prevention_page.py          # Prevention sandbox & trade-offs comparison
│   ├── recovery_page.py            # Recovery workbench, victim policies, audit trail
│   ├── what_if_page.py             # Side-by-side parameter perturbation comparison
│   └── benchmark_page.py           # Algorithmic time complexity benchmarks
│
├── tests/                          # AUTOMATED TEST SUITE (34 deterministic tests)
│   ├── __init__.py
│   ├── test_validation.py          # Matrix dimensions, negative counts, conservation laws
│   ├── test_bankers.py             # Safe states, unsafe states, request rollback
│   ├── test_detection.py           # Single-instance cycles, multi-instance detection
│   ├── test_prevention.py          # Havender's ordering violations, hold-and-wait checks
│   ├── test_recovery.py            # Priority, cost, heuristic recovery, multi-victim loop
│   └── test_scenarios.py           # Verification of all 5 academic presets
│
└── docs/                           # ACADEMIC DOCUMENTATION & VIVA PREPARATION
    ├── architecture.md             # 3-module architectural breakdown and sequence diagram
    ├── flow_diagram.md             # Mermaid flowcharts for all core algorithms
    ├── report_outline.md           # 11-section formal project report guide
    └── viva_questions.md           # High-yield OS viva questions and answers
```

---

## 💻 5. Installation & Windows Setup Instructions

### Prerequisites
* Windows 10 or 11
* Python 3.10+ installed and added to system `PATH` (Verify via `python --version`)
* Git installed (Verify via `git --version`)

### Step-by-Step Setup
1. **Clone or Open the Repository:**
   ```powershell
   cd c:\Users\adity\deadlock-toolkit
   ```

2. **(Optional) Create and Activate a Virtual Environment:**
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. **Install Dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

---

## 🚀 6. How to Run the Application

Launch the Streamlit web dashboard locally:

```powershell
streamlit run app.py
```

The application will automatically open in your default browser at:
`http://localhost:8501`

---

## 🧪 7. Running Automated Tests

To run the complete Pytest suite (34 deterministic tests covering all algorithms, presets, and validation edge cases):

```powershell
pytest -v
```

Expected result:
```text
============================= 34 passed in 0.54s ==============================
```

---

## 📚 8. Example Scenarios & How to Demonstrate

1. **Demonstrating Banker's Avoidance (Preset 1):**
   * Load **1. Safe System (Classic Banker's)** from the sidebar.
   * Navigate to **🔬 Avoidance & Detection**.
   * Use the **Interactive Stepper** to advance through steps ($P_1 \to P_3 \to P_4 \to P_0 \to P_2$).
   * Switch to the **Resource Request Simulator** tab. Request $[1, 0, 2]$ for $P_1$ to show a safe grant. Then request $[3, 3, 0]$ for $P_4$ to show an automatic rollback due to unsafe state.

2. **Demonstrating Unsafe State $\neq$ Deadlock (Preset 2):**
   * Load **2. Unsafe System (Not Deadlocked)**.
   * Notice that Banker's Algorithm reports **UNSAFE STATE** (cannot guarantee completion under maximum claims), but Deadlock Detection reports **DEADLOCK FREE** (current actual requests are runnable).

3. **Demonstrating Single-Instance Cycle = Deadlock (Preset 3):**
   * Load **3. Circular-Wait Deadlock (Single-Instance)**.
   * View the **Resource Allocation Graph**: A red cycle $P_0 \to R_1 \to P_1 \to R_0 \to P_0$ is highlighted.
   * Both processes are deadlocked.

4. **Demonstrating Multi-Instance Cycle $\neq$ Deadlock (Preset 4):**
   * Load **4. Multi-Instance Cycle (No Deadlock)**.
   * View the RAG: A cycle exists between $P_0$ and $P_1$.
   * Deadlock detection reports **DEADLOCK FREE** because unblocked processes $P_2$ and $P_3$ hold instances of the cycled resources and will finish, releasing capacity!

5. **Demonstrating Deadlock Recovery (Preset 5):**
   * Load **5. Recoverable Deadlock**.
   * Navigate to **🚨 Deadlock Recovery**.
   * Select **Lowest Termination Cost** and click **⚡ Execute Single Step**. Observe $P_3$ terminated, resources reclaimed, and system restored to progress.

---

## ⚠️ 9. Limitations & Academic Assumptions

* **Static Process Sets:** The simulation models a fixed set of $n$ processes and $m$ resource types per scenario run.
* **Advance Claim Knowledge:** Banker's Algorithm assumes each process can declare its maximum resource requirement upfront.
* **Simulator Timings:** Benchmarks in the toolkit measure in-memory Python algorithmic execution times and do not reflect hardware-level OS kernel context switches.
* **Single Thread Execution:** The simulation evaluates state deterministically on a single thread.

---

## 📤 10. Manual Git Push Instructions

All commits have been recorded locally in the repository. To publish your repository to your remote GitHub account:

```powershell
# 1. Add your GitHub remote repository URL
git remote add origin https://github.com/<your-username>/deadlock-toolkit.git

# 2. Rename branch to main if desired
git branch -M main

# 3. Push all commits to GitHub
git push -u origin main
```
