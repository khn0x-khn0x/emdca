# Pattern 04: Execution (Active Capability)

## The Principle
We reject the separation of "Decision" and "Action." A Domain Model that cannot act is broken.
In EMDCA, Domain Models are **Active**. They hold the **Capabilities** (Tools) necessary to affect the world.

## The Mechanism
1.  **Capability:** A Pydantic Model that wraps an Infrastructure Client (e.g. `SmtpClient`).
2.  **Injection:** The Capability is passed to the Domain Model at construction.
3.  **Execution:** The Domain Model calls methods on the Capability to perform work.

---

## ❌ Anti-Pattern: Anemic Domain / Service Layer
Separating the logic into a "Service" leaves the Domain Model as a dumb data bag.

```python
# ❌ Service does the work
class UserService:
    def signup(self, user):
        email_client.send(user.email, ...)
```

---

## ✅ Pattern: Active Domain Model
The User owns the action. Note the use of **Smart Enums** for the result.

```python
class SignupResultKind(StrEnum):
    SENT = "sent"
    FAILED = "failed"

class EmailCapability(BaseModel):
    """Wrapper for the infrastructure tool."""
    model_config = {"frozen": True, "arbitrary_types_allowed": True}
    client: Any 

    def send(self, to: Email, content: str) -> EmailResult:
        return self.client.send(to, content)

class User(BaseModel):
    """Active Model. Owns Data AND Capability."""
    model_config = {"frozen": True}
    
    email: Email
    emailer: EmailCapability  # Injected Tool

    def signup(self) -> SignupResult:
        # The User performs the action using its tool.
        result = self.emailer.send(self.email, "Welcome!")
        
        if result.is_success:
            return SignupResult(kind=SignupResultKind.SENT)
        return SignupResult(kind=SignupResultKind.FAILED)
```

---

## Cognitive Checks
- [ ] **No Service Classes:** Did I remove `UserService` / `EmailExecutor`?
- [ ] **Injected Capability:** Does the Model hold the `Capability` as a field?
- [ ] **Co-located Logic:** Is the `signup` logic inside the `User` model?
- [ ] **Smart Enums:** Am I using `SignupResultKind`?
- [ ] **Real Types:** Am I using `Email`, `UserId`?
