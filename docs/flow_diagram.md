# Algorithmic Flow Diagrams: Deadlock Toolkit

This document provides visual flowcharts using Mermaid diagrams for the core algorithms implemented in the toolkit.

---

## 1. Banker's Safety Algorithm (Avoidance)

```mermaid
flowchart TD
    Start([Start Safety Algorithm]) --> Init[Initialize Work = Available<br/>Finish[i] = False for all active processes]
    Init --> CheckCandidate{Find Process P_i where<br/>Finish[i] == False AND<br/>Need[i] <= Work?}
    
    CheckCandidate -- "Found P_i" --> FinishProcess[Work = Work + Allocation[i]<br/>Finish[i] = True<br/>Append P_i to Safe Sequence]
    FinishProcess --> RecordTrace[Record Step Trace in Log]
    RecordTrace --> CheckCandidate
    
    CheckCandidate -- "No such process found" --> CheckAllFinished{Are all active processes<br/>Finish[i] == True?}
    
    CheckAllFinished -- "Yes" --> SafeState([SAFE STATE<br/>Return Safe Sequence])
    CheckAllFinished -- "No" --> UnsafeState([UNSAFE STATE<br/>Identify Unresolved Processes])
```

---

## 2. Banker's Resource-Request Simulation with Rollback

```mermaid
flowchart TD
    ReqStart([Process P_i Requests Vector Q]) --> CheckClaim{Is Request[j] <= Need[i][j]<br/>for all resources j?}
    
    CheckClaim -- "No" --> ErrorClaim[Raise Claim Error:<br/>Process exceeded declared maximum]
    ErrorClaim --> Denied([Request Denied])
    
    CheckClaim -- "Yes" --> CheckAvail{Is Request[j] <= Available[j]<br/>for all resources j?}
    
    CheckAvail -- "No" --> WaitStatus[Process Must Wait:<br/>Resources currently unavailable]
    WaitStatus --> Denied
    
    CheckAvail -- "Yes" --> TentativeAlloc[Tentative Allocation:<br/>Available = Available - Request<br/>Allocation[i] = Allocation[i] + Request<br/>Need[i] = Need[i] - Request]
    
    TentativeAlloc --> RunSafety[Execute Banker's Safety Algorithm<br/>on Tentative State]
    
    RunSafety --> IsSafe{Is Tentative State Safe?}
    
    IsSafe -- "Yes" --> CommitState([COMMIT ALLOCATION<br/>Request Granted Safely])
    IsSafe -- "No" --> RollbackState[ROLLBACK ALLOCATION:<br/>Restore original Available & Allocation<br/>Process P_i Must Wait]
    RollbackState --> UnsafeDenied([Request Rejected to Prevent Deadlock])
```

---

## 3. Multiple-Instance Deadlock Detection Algorithm

```mermaid
flowchart TD
    StartDet([Start Deadlock Detection]) --> InitDet[Work = Available<br/>For each process i:<br/>If Allocation[i] != 0: Finish[i] = False<br/>Else: Finish[i] = True]
    
    InitDet --> FindRunnable{Find Process P_i where<br/>Finish[i] == False AND<br/>Request[i] <= Work?}
    
    FindRunnable -- "Found P_i" --> FreeAlloc[Work = Work + Allocation[i]<br/>Finish[i] = True<br/>Record Step in Trace]
    FreeAlloc --> FindRunnable
    
    FindRunnable -- "None Found" --> CheckDeadlock{Are any processes<br/>Finish[i] == False?}
    
    CheckDeadlock -- "Yes" --> Deadlocked([DEADLOCK DETECTED!<br/>List deadlocked processes])
    CheckDeadlock -- "No" --> NoDeadlock([NO DEADLOCK<br/>System is progressing])
```

---

## 4. Deadlock Recovery Loop

```mermaid
flowchart TD
    RecStart([Deadlock Recovery Triggered]) --> RunDet[Run Deadlock Detection]
    RunDet --> IsDeadlocked{Is System Deadlocked?}
    
    IsDeadlocked -- "No" --> Done([System is Deadlock-Free!])
    
    IsDeadlocked -- "Yes" --> PolicyEval{Victim Selection Policy}
    
    PolicyEval -- "Lowest Priority" --> PickPri[Select deadlocked process with lowest priority number]
    PolicyEval -- "Lowest Cost" --> PickCost[Select deadlocked process with lowest restart cost]
    PolicyEval -- "Max Resources" --> PickMax[Select process holding the largest sum of allocated units]
    PolicyEval -- "Manual" --> PickManual[Select user-specified process]
    
    PickPri --> TerminateVictim
    PickCost --> TerminateVictim
    PickMax --> TerminateVictim
    PickManual --> TerminateVictim
    
    TerminateVictim[Terminate Victim Process:<br/>1. Available = Available + Allocation[victim]<br/>2. Allocation[victim] = 0<br/>3. Request[victim] = 0<br/>4. Mark victim as TERMINATED]
    
    TerminateVictim --> LogAction[Record Recovery Action & Reclaimed Resources in Audit Log]
    LogAction --> RunDet
```

---

## 5. Havender's Resource Ordering (Circular Wait Prevention)

```mermaid
flowchart TD
    ReqOrder([Process P Requests Resource R_j]) --> LookupHeld[Identify all resources R_i currently held by P]
    LookupHeld --> CheckHeldEmpty{Does P hold any resources?}
    
    CheckHeldEmpty -- "No" --> Allow[Request Permitted]
    CheckHeldEmpty -- "Yes" --> CompOrder{Is F(R_j) > max(F(R_i)) for all held R_i?}
    
    CompOrder -- "Yes" --> Allow
    CompOrder -- "No" --> Violate[VIOLATION DETECTED:<br/>F(requested) <= F(held)<br/>Static rejection prevents Circular Wait]
    
    Allow --> OrderGranted([Request Allowed by Prevention Rule])
    Violate --> OrderRejected([Request Denied])
```
