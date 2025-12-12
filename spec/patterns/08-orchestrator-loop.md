# Pattern 08: Coordination (The Orchestrator)

## The Principle
A system needs a "driver" that does no thinking, only moving. It coordinates the flow of data between Repository, Factory, and Execution shell.

## The Mechanism
The **Application Service** runs a "dumb" procedural loop: Fetch → Translate → Decide → Act → Persist. It contains no business rules, only flow control.

---

## 1. The Fat Service (Anti-Pattern)
Putting business logic ("Thinking") inside the orchestration layer ("Moving") makes the system rigid and hard to test.

### ❌ Anti-Pattern: Logic in the Loop
```python
def process_payment(payment_id: str, repo: Repo):
    payment = repo.get(payment_id)
    
    # ❌ BUSINESS LOGIC LEAK!
    # This rule belongs in the Domain, not the Service.
    if payment.amount > 10000 and not payment.is_verified:
        raise ValueError("Large payments need verification")
        
    payment.status = "processed"
    repo.save(payment)
```

---

## 2. The Dumb Loop (The Standard Cycle)
The Orchestrator is a pipeline. It connects the components but does not modify the data stream.

### ✅ Pattern: Fetch -> Decide -> Act -> Persist
```python
def process_payment(payment_id: str, repo: Repo):
    # 1. Fetch (Infrastructure)
    payment = repo.get(payment_id)
    if not payment:
        return

    # 2. Decide (Pure Domain)
    # The Service asks the Domain: "What should happen?"
    # It does NOT ask "Is this valid?"
    result_intent = decide_payment_action(payment)

    # 3. Act (Infrastructure)
    match result_intent:
        case ProcessPaymentIntent(new_state=s):
            gateway.charge(s.amount)
            repo.save(s)
            
        case RequireVerificationIntent(reason=r):
            email_service.send_alert(r)
            # No save needed, state didn't change
            
        case RejectPaymentIntent(new_state=rejected_payment):
            # ✅ The Service just saves what it was given.
            # It does NOT call methods like .mark_rejected().
            repo.save(rejected_payment)
```

---

## 3. Transaction Boundaries
The Orchestrator is responsible for the **Unit of Work**. It ensures that the "Act" and "Persist" steps happen atomically.

### ✅ Pattern: Explicit Transactions
```python
def safe_process(payment_id: str, repo: Repo, uow: UnitOfWork):
    with uow.begin():
        payment = repo.get(payment_id)
        
        # ... logic ...
        
        repo.save(payment)
        # Commit happens here automatically
```

---

## 4. Cognitive Checks
*   [ ] **No If Statements:** Does the service contain `if payment.amount > X`? (Move to Domain).
*   [ ] **No Object Creation:** Does the service call `Payment(...)`? (Use a Factory).
*   [ ] **Dumb Piping:** Does the service just pass variable `A` from function `get_A()` to function `process_A()`?
