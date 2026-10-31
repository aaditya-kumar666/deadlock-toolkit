# Operating Systems Viva Preparation Guide: Deadlocks

**Course:** CSE316 Operating Systems  
**Topic:** Deadlock Prevention, Avoidance, Detection, and Recovery  
**Toolkit:** Deadlock Prevention and Recovery Toolkit  

---

## 1. Fundamental Concepts & Necessary Conditions

### Q1: What is a Deadlock in an Operating System?
**Answer:** A deadlock is a situation where a set of processes are blocked because each process is holding a resource and waiting for another resource held by some other process in the same set. None of the processes can execute, release resources, or be awakened.

### Q2: What are the four Coffman Conditions for Deadlock?
**Answer:** E. G. Coffman identified four necessary conditions that must hold simultaneously for a deadlock to occur:
1. **Mutual Exclusion:** At least one resource must be held in a non-shareable mode (only one process can use it at a time).
2. **Hold and Wait:** A process must currently hold at least one resource and be actively waiting to acquire additional resources that are currently held by other processes.
3. **No Preemption:** Resources cannot be forcibly taken away from a process holding them; they can only be released voluntarily by the process after completing its task.
4. **Circular Wait:** A closed chain of processes $\{P_0, P_1, \dots, P_n\}$ exists such that $P_0$ is waiting for a resource held by $P_1$, $P_1$ is waiting for $P_2$, ..., and $P_n$ is waiting for $P_0$.

> **Viva Tip:** Emphasize that these four conditions are *necessary* for deadlock. If you eliminate even one condition, deadlock cannot occur!

---

## 2. Prevention vs Avoidance vs Detection vs Recovery

### Q3: What is the exact difference between Deadlock Prevention and Deadlock Avoidance?
**Answer:**
* **Deadlock Prevention:** Statically constrains the system design or how resource requests are made to ensure that at least one of the four Coffman conditions can never hold. It does **not** require knowing future maximum resource claims. Example: Havender's linear resource ordering eliminates Circular Wait.
* **Deadlock Avoidance:** Allows all four conditions to exist theoretically, but dynamically monitors the resource allocation state at runtime. It requires *a priori* knowledge of the maximum claim of each process (e.g., Banker's Algorithm). Requests are granted only if the resulting state is guaranteed to be **safe**.

> **Crucial Viva Clarification:** Never label Banker's Algorithm as "prevention". It is strictly an **avoidance** algorithm!

### Q4: What is the difference between an Unsafe State and a Deadlocked State?
**Answer:**
* **Safe State:** A state where there exists at least one sequence $\langle P_1, P_2, \dots, P_n \rangle$ such that every process can satisfy its declared maximum demand and run to completion with currently available resources plus resources freed by prior processes.
* **Unsafe State:** A state where no safe sequence exists under the worst-case assumption that all processes request their maximum declared claims simultaneously. **An unsafe state is NOT automatically a deadlock!** It merely means the OS can no longer prevent a deadlock if processes request their maximums.
* **Deadlocked State:** A state where two or more processes have active outstanding requests that can never be satisfied because each is waiting on a resource held by another.
* **Relationship:** All deadlocked states are unsafe states, but not all unsafe states are deadlocked states!

---

## 3. Dijkstra's Banker's Algorithm (Avoidance)

### Q5: How does the Banker's Algorithm work?
**Answer:**
1. **Data Structures:**
   * Available vector $A$ of length $m$.
   * Max matrix $M$ of size $n \times m$.
   * Allocation matrix $C$ of size $n \times m$.
   * Need matrix $N = M - C$ of size $n \times m$.
2. **Safety Algorithm:**
   * Initialize $\text{Work} = \text{Available}$ and $\text{Finish}[i] = \text{False}$ for all processes.
   * Search for an active process $P_i$ where $\text{Finish}[i] == \text{False}$ and $\text{Need}[i] \le \text{Work}$.
   * If found: $\text{Work} = \text{Work} + \text{Allocation}[i]$, $\text{Finish}[i] = \text{True}$. Repeat search.
   * If all processes finish, the state is **SAFE**; otherwise, it is **UNSAFE**.
3. **Resource-Request Algorithm:**
   * Validate: $\text{Request}_i \le \text{Need}_i$ (otherwise error: claim exceeded).
   * Check: $\text{Request}_i \le \text{Available}$ (otherwise $P_i$ must wait).
   * Tentatively grant: $\text{Available} \mathrel{-}= \text{Request}$, $\text{Allocation}_i \mathrel{+}= \text{Request}$, $\text{Need}_i \mathrel{-}= \text{Request}$.
   * Run Safety Algorithm: If safe $\to$ commit. If unsafe $\to$ rollback state and make $P_i$ wait!

### Q6: What is the Time and Space Complexity of Banker's Algorithm?
**Answer:**
* **Time Complexity:** $O(m \cdot n^2)$ where $n$ is the number of processes and $m$ is the number of resource types. In the worst case, searching for a runnable process inspects $n$ candidates against $m$ resource types, finding only 1 runnable process per pass, repeating $n$ times ($n \times n \times m = m \cdot n^2$).
* **Space Complexity:** $O(m \cdot n)$ to store the Allocation, Maximum, Need, and Request matrices.

### Q7: What are the practical limitations of Banker's Algorithm in real OS kernels?
**Answer:**
1. **Unknown Maximum Claims:** Real-world processes rarely know in advance the maximum number of file handles, sockets, or memory blocks they will need.
2. **Dynamic Process Count:** Real OS processes are spawned and destroyed dynamically; Banker's assumes a fixed set of $n$ processes and $m$ resources.
3. **High Overhead:** Evaluating $O(m \cdot n^2)$ on every system call requesting a resource introduces unacceptable latency.
4. **Conservation of Resources:** It assumes resources remain constant, which does not account for hardware failures or dynamic hot-plugging.

---

## 4. Resource Allocation Graphs (RAG) & Cycles

### Q8: What are the components of a Resource Allocation Graph?
**Answer:** A RAG is a directed bipartite graph $G = (V, E)$:
* **Vertices $V$:** Divided into two disjoint sets: Processes $P = \{P_1, \dots, P_n\}$ (circles) and Resources $R = \{R_1, \dots, R_m\}$ (squares).
* **Edges $E$:**
  * **Assignment Edge ($R_j \to P_i$):** An instance of resource $R_j$ is allocated to process $P_i$.
  * **Request Edge ($P_i \to R_j$):** Process $P_i$ has requested and is currently waiting for an instance of resource $R_j$.

### Q9: Does a cycle in a Resource Allocation Graph always mean a deadlock?
**Answer:** **No, not always!**
* **In Single-Instance Resource Systems:** A directed cycle is a **necessary and sufficient** condition for deadlock. A cycle guarantees deadlock.
* **In Multiple-Instance Resource Systems:** A directed cycle is **necessary but NOT sufficient**! If a cycle exists, the system *may* be deadlocked, but if another process holding an instance of the cycled resource can finish and release its instance, the cycle is broken and no deadlock occurs.

> **Demonstration Tip:** In the toolkit, load Preset 4 ("Multi-Instance Cycle Without Deadlock") to demonstrate a graph with a cycle where detection proves no deadlock exists!

---

## 5. Deadlock Detection & Recovery

### Q10: How does the Multi-Instance Deadlock Detection Algorithm differ from Banker's?
**Answer:**
* Banker's Algorithm checks whether the system can satisfy the **Need Matrix** ($N = M - C$, potential worst-case future claims).
* Deadlock Detection checks whether the system can satisfy the **Request Matrix** ($Q$, actual currently outstanding requests).
* In Deadlock Detection, any process holding **zero allocated resources** is immediately marked as finished, because a process holding no resources cannot block any other process.

### Q11: What strategies are used to select a victim during recovery?
**Answer:**
1. **Lowest Priority:** Terminate the process with the lowest importance to the user/system.
2. **Lowest Cost:** Terminate the process with the smallest accumulated CPU time, memory footprint, or restart penalty.
3. **Max Reclaimed Resources Heuristic:** Terminate the process holding the largest quantity of the bottleneck resource to free maximum capacity.
4. **Trade-off:** Starvation! If the policy always picks the lowest priority or lowest cost process, the same process may be repeatedly selected and never complete. A timestamp or aging mechanism must be introduced.

---

## 6. Project Architecture & Design Decisions

### Q12: Why did you separate the toolkit into three distinct modules?
**Answer:**
* **Modularity and Decoupling:** Module 1 (Analysis) contains pure algorithmic logic independent of any UI framework. This allows unit testing via Pytest without spinning up a browser.
* **Academic Clarity:** Keeps Prevention (static constraints) strictly separated from Avoidance (runtime state inspection) and Detection/Recovery.
* **Testability:** 100% of algorithmic assertions can be validated deterministically in automated suites.

### Q13: Why is this simulation safe to run in a classroom environment?
**Answer:** It executes strictly on an in-memory object model (`SystemState`). All allocations, releases, and terminations are simulated array and dictionary operations. It uses no system calls like `kill()`, `TerminateProcess()`, or kernel-level memory reallocations.
