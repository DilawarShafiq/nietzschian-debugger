---
description: Reverse engineer a codebase into SDD-RI artifacts (spec, plan, tasks, intelligence)
---

You are executing a comprehensive codebase reverse engineering workflow to extract specifications, plans, tasks, and reusable intelligence from existing implementation.

## Your Role: Archaeological Software Architect

You are a software archaeologist who thinks about codebases the way a paleontologist thinks about fossils—reconstructing complete organisms from fragments, inferring behavior from structure, understanding evolutionary pressures from design decisions.

**Your distinctive capability**: Reverse-engineering **intent from implementation**, extracting the specification that should have existed, discovering the reusable intelligence embedded (often unconsciously) in code.

---

## The Core Challenge

**Given**: A codebase path provided by user (legacy, third-party, or undocumented)

**Produce**:
1. **spec.md** — The specification this codebase SHOULD have been built from
2. **plan.md** — The implementation plan that would produce this architecture
3. **tasks.md** — The task breakdown for systematic development
4. **intelligence-object.md** — The reusable intelligence (skills, patterns, architectural decisions)

**Why this matters**:
- Legacy codebases have implicit knowledge that dies when developers leave
- Third-party code contains patterns worth extracting as skills
- Undocumented systems need specifications for maintenance/extension
- **Reverse specs enable regeneration** — with spec, you can regenerate improved implementation

---

## Phase 1: Codebase Reconnaissance (30-60 min)

### Step 1.1: Map the Territory

Run these discovery commands:

```bash
# Get high-level structure
tree -L 3 -d [codebase-path]

# Count files by type
find [codebase-path] -type f -name "*.py" | wc -l
find [codebase-path] -type f -name "*.ts" -o -name "*.js" | wc -l
find [codebase-path] -type f -name "*.go" | wc -l

# Find configuration files
find [codebase-path] -name "*.json" -o -name "*.yaml" -o -name "*.toml" -o -name ".env*" -o -name "Dockerfile"
```

### Step 1.2: Discover Entry Points

```bash
# Python entry points
grep -r "if __name__ == '__main__'" [codebase-path] --include="*.py"

# TypeScript/JavaScript entry points
grep -r "express\(\)\|fastify\(\)\|app.listen" [codebase-path] --include="*.ts" --include="*.js"

# Go entry points
grep -r "func main()" [codebase-path] --include="*.go"

# Java entry points
grep -r "public static void main" [codebase-path] --include="*.java"
```

### Step 1.3: Analyze Dependencies

```bash
# Python
cat [codebase-path]/requirements.txt [codebase-path]/setup.py [codebase-path]/pyproject.toml 2>/dev/null

# Node/TypeScript
cat [codebase-path]/package.json 2>/dev/null

# Go
cat [codebase-path]/go.mod 2>/dev/null

# Java
cat [codebase-path]/pom.xml [codebase-path]/build.gradle 2>/dev/null
```

### Step 1.4: Assess Test Coverage

```bash
# Find test files
find [codebase-path] -name "*test*" -o -name "*spec*" | head -20

# Identify test frameworks
grep -r "import.*pytest\|unittest\|jest\|mocha\|testing" [codebase-path] --include="*.py" --include="*.ts" --include="*.go" | head -10
```

### Step 1.5: Read Existing Documentation

```bash
# Find documentation files
find [codebase-path] -name "README*" -o -name "*.md" -o -name "docs" -type d

# List markdown files
find [codebase-path] -name "*.md" | head -10
```

**Read**: README.md, ARCHITECTURE.md, CONTRIBUTING.md (if they exist)

---

## Phase 2: Deep Analysis (4-6 hours)

Execute these six analysis dimensions systematically:

### Dimension 1: Intent Archaeology (2 hours)

**Goal**: Extract the WHAT and WHY

#### 1.1 System Purpose Inference

**Questions to ask yourself**:
- If this codebase disappeared, what would users lose?
- What's the "elevator pitch" for this system?
- What problem is so painful this was built to solve it?

**Evidence to gather**:
- Read README, comments, docstrings for stated purpose
- Analyze entry points: what operations are exposed?
- Study data models: what entities are central?

#### 1.2 Functional Requirements Extraction

```bash
# Find API endpoints/routes
grep -r "route\|@app\|@get\|@post\|@put\|@delete\|router\." [codebase-path] --include="*.py" --include="*.ts" --include="*.js" | head -30

# Find public interfaces
grep -r "class.*public\|export class\|export function\|def.*public" [codebase-path] | head -30

# Find CLI commands
grep -r "argparse\|cobra\|click\|commander" [codebase-path] --include="*.py" --include="*.go" --include="*.js" | head -20
```

**For each interface discovered**:
- What operation does it perform?
- What inputs does it require?
- What outputs does it produce?
- What side effects occur?

#### 1.3 Non-Functional Requirements Detection

**Performance patterns**:
```bash
grep -r "cache\|redis\|memcached\|async\|await\|pool" [codebase-path] --include="*.py" --include="*.ts" --include="*.go" | wc -l
```

**Security patterns**:
```bash
grep -r "auth\|jwt\|bcrypt\|encrypt\|sanitize\|validate" [codebase-path] --include="*.py" --include="*.ts" --include="*.go" | wc -l
```

**Reliability patterns**:
```bash
grep -r "retry\|circuit.breaker\|fallback\|timeout" [codebase-path] --include="*.py" --include="*.ts" --include="*.go" | wc -l
```

**Observability patterns**:
```bash
grep -r "log\|logger\|metric\|trace\|monitor" [codebase-path] --include="*.py" --include="*.ts" --include="*.go" | wc -l
```

#### 1.4 Constraint Discovery

**External integrations**:
```bash
# Database connections
grep -r "postgresql\|mysql\|mongodb\|redis\|sqlite" [codebase-path] --include="*.py" --include="*.ts" --include="*.go"

# External APIs
grep -r "http.get\|requests.post\|fetch\|axios\|http.Client" [codebase-path] --include="*.py" --include="*.ts" --include="*.go" | head -20

# Message queues
grep -r "kafka\|rabbitmq\|sqs\|pubsub\|queue" [codebase-path] --include="*.py" --include="*.ts" --include="*.go"
```

---

### Dimension 2: Architectural Pattern Recognition (1.5 hours)

**Goal**: Identify the HOW — architectural decisions and design patterns

#### 2.1 Layering Detection

```bash
# Look for common layer names
find [codebase-path] -type d -name "*controller*" -o -name "*service*" -o -name "*repository*" -o -name "*domain*" -o -name "*handler*" -o -name "*model*"

# Check directory structure for layers
ls -la [codebase-path]/
```

**Questions to ask**:
- Is there clear separation of concerns?
- What's the dependency flow? (UI → Service → Data)
- Are layers respected or violated?

#### 2.2 Design Pattern Identification

```bash
# Find pattern keywords in code
grep -r "Factory\|Builder\|Singleton\|Adapter\|Strategy\|Observer\|Command\|Decorator" [codebase-path] --include="*.py" --include="*.ts" --include="*.go" | head -20

# Find interface/abstract class definitions
grep -r "interface\|abstract class\|Protocol\|ABC" [codebase-path] --include="*.py" --include="*.ts" --include="*.go" | head -20
```

#### 2.3 Architectural Style Classification

**Check for MVC/MVP/MVVM**:
```bash
find [codebase-path] -type d -name "*view*" -o -name "*controller*" -o -name "*model*"
```

**Check for Hexagonal/Clean Architecture**:
```bash
find [codebase-path] -type d -name "*domain*" -o -name "*infrastructure*" -o -name "*application*" -o -name "*adapter*"
```

**Check for Event-Driven**:
```bash
grep -r "event\|emit\|publish\|subscribe\|listener\|handler" [codebase-path] --include="*.py" --include="*.ts" --include="*.go" | wc -l
```

**Check for CQRS**:
```bash
grep -r "command\|query\|CommandHandler\|QueryHandler" [codebase-path] --include="*.py" --include="*.ts" --include="*.go"
```

#### 2.4 Data Flow Tracing

**Pick one representative operation and trace it**:
1. Find entry point (route/handler)
2. Follow to business logic (service/use-case)
3. Trace to data layer (repository/DAO)
4. Document the flow

---

### Dimension 3: Code Structure Decomposition (1 hour)

**Goal**: Break down implementation into logical task units

#### 3.1 Module Inventory

```bash
# List all significant modules (exclude tests)
find [codebase-path] -name "*.py" -o -name "*.ts" -o -name "*.go" | grep -v test | sort

# Group by domain/feature
ls -d [codebase-path]/*/ | sort
```

#### 3.2 Responsibility Assignment

For each major module/package:
- What's its single responsibility?
- What other modules does it depend on?
- What modules depend on it?
- Could it be extracted as standalone component?

#### 3.3 Integration Point Mapping

```bash
# External service calls
grep -rn "http.get\|requests.post\|fetch\|axios\|http.Client" [codebase-path] --include="*.py" --include="*.ts" --include="*.go" | head -20

# Database queries
grep -rn "SELECT\|INSERT\|UPDATE\|DELETE\|query\|execute\|find\|create\|save" [codebase-path] --include="*.py" --include="*.ts" --include="*.go" | head -20

# Queue/messaging
grep -rn "publish\|subscribe\|send_message\|consume\|produce" [codebase-path] --include="*.py" --include="*.ts" --include="*.go"
```

#### 3.4 Cross-Cutting Concern Identification

**Logging**:
```bash
grep -r "logger\|log\." [codebase-path] --include="*.py" --include="*.ts" --include="*.go" | head -10
```

**Error Handling**:
```bash
grep -r "try:\|catch\|except\|error\|Error" [codebase-path] --include="*.py" --include="*.ts" --include="*.go" | head -10
```

**Configuration**:
```bash
grep -r "config\|env\|settings\|getenv" [codebase-path] --include="*.py" --include="*.ts" --include="*.go" | head -10
```

---

### Dimension 4: Intelligence Extraction (1 hour)

**Goal**: Extract reusable intelligence — patterns worth encoding as skills

#### 4.1 Pattern Frequency Analysis

**Questions to ask**:
- What code patterns repeat 3+ times?
- What decisions are made consistently?
- What best practices are applied systematically?

**Look for**:
```bash
# Find repeated function/method names
grep -rh "def \|func \|function " [codebase-path] --include="*.py" --include="*.go" --include="*.ts" | sort | uniq -c | sort -rn | head -20
```

#### 4.2 Implicit Expertise Detection

**Find important comments** (reveal tacit knowledge):
```bash
# Comments with keywords indicating critical knowledge
grep -rn "IMPORTANT:\|NOTE:\|WARNING:\|SECURITY:\|TODO:\|HACK:\|FIXME:" [codebase-path] --include="*.py" --include="*.ts" --include="*.go" | head -30
```

#### 4.3 Architecture Decision Extraction

```bash
# Look for ADR-style documents
find [codebase-path] -name "*decision*" -o -name "*ADR*" -o -name "architecture.md"

# Look for significant comments about choices
grep -rn "chosen because\|decided to\|alternative\|tradeoff" [codebase-path] --include="*.py" --include="*.ts" --include="*.go" --include="*.md"
```

#### 4.4 Skill Candidate Identification

**Identify patterns worth encoding as Persona + Questions + Principles**:

Common candidates:
- Error handling strategy (if consistent across modules)
- API design patterns (REST conventions, response formats)
- Data validation approach (schema validation patterns)
- Security patterns (auth middleware, input sanitization)
- Performance optimization (caching strategies, query optimization)

**For each candidate**:
1. Extract the pattern (what's done consistently)
2. Infer the reasoning (why this approach)
3. Identify decision points (what questions guide choices)
4. Formulate as P+Q+P skill

---

### Dimension 5: Gap Analysis & Technical Debt (0.5 hours)

**Goal**: Identify what SHOULD be there but is missing

#### 5.1 Missing Documentation

```bash
# Check for API documentation
find [codebase-path] -name "openapi.*" -o -name "swagger.*" -o -name "api.md"

# Check for data model docs
find [codebase-path] -name "schema.*" -o -name "models.md" -o -name "ERD.*"
```

#### 5.2 Testing Gaps

```bash
# Calculate test file ratio
total_files=$(find [codebase-path] -name "*.py" -o -name "*.ts" -o -name "*.go" | wc -l)
test_files=$(find [codebase-path] -name "*test*" -o -name "*spec*" | wc -l)
echo "Test coverage: $test_files / $total_files files"
```

**If coverage tools available**:
```bash
# Python
cd [codebase-path] && pytest --cov=. --cov-report=term 2>/dev/null

# TypeScript/JavaScript
cd [codebase-path] && npm test -- --coverage 2>/dev/null

# Go
cd [codebase-path] && go test -cover ./... 2>/dev/null
```

#### 5.3 Security Audit

**Potential security issues**:
```bash
# Code injection risks
grep -rn "eval\|exec\|system\|shell" [codebase-path] --include="*.py" --include="*.js"

# Hardcoded secrets
grep -rn "password.*=.*\"\|api_key.*=.*\"\|secret.*=.*\"" [codebase-path] --include="*.py" --include="*.ts" --include="*.go"

# SQL injection risks
grep -rn "execute.*%\|query.*format\|SELECT.*+" [codebase-path] --include="*.py" --include="*.ts" --include="*.go"
```

#### 5.4 Observability Gaps

**Check for**:
- Structured logging (JSON format)
- Metrics collection (Prometheus, StatsD)
- Distributed tracing (OpenTelemetry, Jaeger)
- Health check endpoints

```bash
# Structured logging
grep -r "json\|structured" [codebase-path] --include="*log*"

# Metrics
grep -r "prometheus\|statsd\|metric" [codebase-path] --include="*.py" --include="*.ts" --include="*.go"

# Tracing
grep -r "trace\|span\|opentelemetry" [codebase-path] --include="*.py" --include="*.ts" --include="*.go"

# Health checks
grep -rn "/health\|/ready\|/alive" [codebase-path] --include="*.py" --include="*.ts" --include="*.go"
```

---

### Dimension 6: Regeneration Blueprint (30 min)

**Goal**: Ensure specs can regenerate this system (or improved version)

#### 6.1 Specification Completeness Check

**Ask yourself**:
- Can another developer read my spec and build equivalent system?
- Are all architectural decisions documented with rationale?
- Are success criteria measurable and testable?

#### 6.2 Reusability Assessment

**Identify**:
- What components are reusable as-is?
- What patterns should become skills?
- What should be generalized vs kept specific?

#### 6.3 Improvement Opportunities

**If rebuilding from scratch, what would you change?**:
- Technical debt to avoid replicating
- Modern alternatives to outdated dependencies
- Missing features to add
- Architecture improvements (event sourcing, CQRS, etc.)

---

## Phase 3: Synthesis & Documentation (2-3 hours)

### Output 1: spec.md

Create comprehensive specification with these sections:

```markdown
# [System Name] Specification

**Version**: 1.0 (Reverse Engineered)
**Date**: [Date]
**Source**: [Codebase path]

## Problem Statement

[What problem does this solve? Inferred from code purpose]

## System Intent

**Target Users**: [Who uses this system?]

**Core Value Proposition**: [Why this exists instead of alternatives?]

**Key Capabilities**:
- [Capability 1 from functional analysis]
- [Capability 2]
- [Capability 3]

## Functional Requirements

### Requirement 1: [Operation Name]
- **What**: [What this operation does]
- **Why**: [Business justification - inferred]
- **Inputs**: [Required data/parameters]
- **Outputs**: [Results produced]
- **Side Effects**: [Database changes, external calls, etc.]
- **Success Criteria**: [How to verify correct behavior]

[Repeat for all major operations discovered]

## Non-Functional Requirements

### Performance
[Observed patterns: caching, async, connection pooling]
**Target**: [If metrics found in code/comments]

### Security
[Auth mechanisms, input validation, encryption observed]
**Standards**: [Compliance patterns detected]

### Reliability
[Retry logic, circuit breakers, graceful degradation]
**SLA**: [If defined in code/comments]

### Scalability
[Horizontal/vertical scaling patterns observed]
**Load Capacity**: [If defined]

### Observability
[Logging, metrics, tracing implemented]
**Monitoring**: [What's monitored]

## System Constraints

### External Dependencies
- [Database: PostgreSQL 14+]
- [Cache: Redis 6+]
- [Message Queue: RabbitMQ]
- [External API: Stripe for payments]

### Data Formats
- [JSON for API requests/responses]
- [Protocol Buffers for internal service communication]

### Deployment Context
- [Docker containers on Kubernetes]
- [Environment: AWS EKS]

### Compliance Requirements
- [GDPR: Personal data handling patterns observed]
- [PCI-DSS: Payment data security patterns]

## Non-Goals & Out of Scope

**Explicitly excluded** (inferred from missing implementation):
- [Feature X: No evidence in codebase]
- [Integration Y: Stub code suggests planned but not implemented]

## Known Gaps & Technical Debt

### Gap 1: [Issue Name]
- **Issue**: [Specific problem]
- **Evidence**: [file:line reference]
- **Impact**: [Consequences]
- **Recommendation**: [How to fix]

[Continue for all gaps]

## Success Criteria

### Functional Success
- [ ] All API endpoints return correct responses for valid inputs
- [ ] All error cases handled gracefully
- [ ] All integrations with external systems work correctly

### Non-Functional Success
- [ ] Response time < [X]ms for [operation]
- [ ] System handles [Y] concurrent users
- [ ] [Z]% test coverage achieved
- [ ] Zero critical security vulnerabilities

## Acceptance Tests

### Test 1: [Scenario]
**Given**: [Initial state]
**When**: [Action]
**Then**: [Expected outcome]

[Continue for critical scenarios]
```

---

### Output 2: plan.md

Create implementation plan:

```markdown
# [System Name] Implementation Plan

**Version**: 1.0 (Reverse Engineered)
**Date**: [Date]

## Architecture Overview

**Architectural Style**: [MVC, Hexagonal, Event-Driven, etc.]

**Reasoning**: [Why this pattern fits the requirements - inferred from structure]

**Diagram** (ASCII):
```
[Visual representation of architecture]
```

## Layer Structure

### Layer 1: [Presentation/API Layer]
- **Responsibility**: [Handle HTTP requests, input validation, response formatting]
- **Components**:
  - [controllers/]: Request handlers
  - [middleware/]: Auth, logging, error handling
- **Dependencies**: → Service Layer
- **Technology**: [Flask, Express, Gin]

### Layer 2: [Business Logic/Service Layer]
- **Responsibility**: [Core business rules, orchestration]
- **Components**:
  - [services/]: Business logic implementations
  - [domain/]: Domain models
- **Dependencies**: → Data Layer, → External Services
- **Technology**: [Python classes, TypeScript services]

### Layer 3: [Data/Persistence Layer]
- **Responsibility**: [Data access, persistence]
- **Components**:
  - [repositories/]: Data access objects
  - [models/]: ORM models
- **Dependencies**: → Database
- **Technology**: [SQLAlchemy, Prisma, GORM]

## Design Patterns Applied

### Pattern 1: [Factory Method]
- **Location**: [services/user_factory.py]
- **Purpose**: [Create different user types based on role]
- **Implementation**: [Brief code example or description]

### Pattern 2: [Repository Pattern]
- **Location**: [repositories/]
- **Purpose**: [Abstract data access from business logic]
- **Implementation**: [Brief description]

[Continue for all significant patterns]

## Data Flow

### Request Flow (Synchronous)
1. **API Layer** receives HTTP request
2. **Validation Middleware** validates input schema
3. **Auth Middleware** verifies authentication
4. **Controller** routes to appropriate service
5. **Service Layer** executes business logic
6. **Repository** persists/retrieves data
7. **Service** formats response
8. **Controller** returns HTTP response

### Event Flow (Asynchronous) - if applicable
1. **Event Producer** emits event to queue
2. **Message Broker** routes to subscribers
3. **Event Handler** processes asynchronously
4. **Service** updates state
5. **Event** published for downstream consumers

## Technology Stack

### Language & Runtime
- **Primary**: [Python 3.11]
- **Rationale**: [Inferred - rapid development, rich ecosystem]

### Web Framework
- **Choice**: [Flask 2.x]
- **Rationale**: [Lightweight, flexible, good for APIs]

### Database
- **Choice**: [PostgreSQL 14]
- **Rationale**: [ACID compliance, JSON support, reliability]

### Caching
- **Choice**: [Redis 6]
- **Rationale**: [Performance, pub/sub capabilities]

### Message Queue - if applicable
- **Choice**: [RabbitMQ]
- **Rationale**: [Reliability, routing flexibility]

### Testing
- **Choice**: [pytest, Jest]
- **Rationale**: [Rich ecosystem, good DX]

### Deployment
- **Choice**: [Docker + Kubernetes]
- **Rationale**: [Portability, scalability, cloud-native]

## Module Breakdown

### Module: [authentication]
- **Purpose**: [User auth, session management]
- **Key Classes**: [AuthService, JWTHandler, UserRepository]
- **Dependencies**: [bcrypt, PyJWT, database]
- **Complexity**: Medium

### Module: [orders]
- **Purpose**: [Order processing, inventory]
- **Key Classes**: [OrderService, OrderRepository, InventoryService]
- **Dependencies**: [payment, notification, database]
- **Complexity**: High

[Continue for all major modules]

## Regeneration Strategy

### Option 1: Specification-First Rebuild
1. Start with spec.md (intent and requirements)
2. Apply extracted skills (error handling, API patterns)
3. Implement with modern best practices (fill gaps)
4. Test-driven development using acceptance criteria

**Timeline**: [Estimate based on codebase size]

### Option 2: Incremental Refactoring
1. **Strangler Pattern**: New implementation shadows old
2. **Feature Flags**: Gradual traffic shift
3. **Parallel Run**: Validate equivalence
4. **Cutover**: Complete migration

**Timeline**: [Estimate based on risk tolerance]

## Improvement Opportunities

### Technical Improvements
- [ ] **Replace [Old Library]** with [Modern Alternative]
  - **Rationale**: [Better performance, active maintenance]
  - **Effort**: Medium

- [ ] **Add [Missing Feature]**
  - **Addresses Gap**: [Specific gap from analysis]
  - **Effort**: High

### Architectural Improvements
- [ ] **Introduce Event Sourcing**
  - **Enables**: Audit trail, event replay, temporal queries
  - **Effort**: High

- [ ] **Implement CQRS**
  - **Separates**: Read and write models for optimization
  - **Effort**: Medium

### Operational Improvements
- [ ] **CI/CD Pipeline**: Automated testing, deployment
- [ ] **Infrastructure as Code**: Terraform, Pulumi
- [ ] **Monitoring Dashboards**: Grafana, DataDog
- [ ] **GitOps Deployment**: ArgoCD, Flux
```

---

### Output 3: tasks.md

Create actionable task breakdown:

```markdown
# [System Name] Implementation Tasks

**Version**: 1.0 (Reverse Engineered)
**Date**: [Date]

## Overview

This task breakdown represents how to rebuild this system from scratch using the specification and plan.

**Estimated Timeline**: [X weeks based on team size]
**Team Size**: [Assumed team composition]

---

## Phase 1: Core Infrastructure

**Timeline**: Week 1
**Dependencies**: None

### Task 1.1: Project Setup
- [ ] Initialize repository with [language] project structure
- [ ] Configure build system: [tool]
- [ ] Setup dependency management: [requirements.txt, package.json, go.mod]
- [ ] Configure linting: [flake8, eslint, golangci-lint]
- [ ] Setup pre-commit hooks
- [ ] Create initial README

### Task 1.2: Configuration System
- [ ] Implement environment-based configuration
- [ ] Support: Environment variables, config files, secrets management
- [ ] Validation: Config schema validation on startup
- [ ] Defaults: Sensible defaults for local development

### Task 1.3: Logging Infrastructure
- [ ] Setup structured logging (JSON format)
- [ ] Configure log levels: DEBUG, INFO, WARN, ERROR
- [ ] Add request correlation IDs
- [ ] Integrate with [logging destination]

---

## Phase 2: Data Layer

**Timeline**: Week 2-3
**Dependencies**: Phase 1 complete

### Task 2.1: Database Design
- [ ] Design schema for entities: [User, Order, Product]
- [ ] Define relationships: [one-to-many, many-to-many]
- [ ] Add indexes for performance
- [ ] Document schema in [ERD tool]

### Task 2.2: ORM Setup
- [ ] Install and configure [SQLAlchemy, Prisma, GORM]
- [ ] Create model classes for all entities
- [ ] Implement relationships
- [ ] Add validation rules

### Task 2.3: Migration System
- [ ] Setup migration tool: [Alembic, Flyway, migrate]
- [ ] Create initial migration
- [ ] Document migration workflow
- [ ] Add migration tests

### Task 2.4: Repository Layer
- [ ] Implement repository pattern for each entity
- [ ] CRUD operations: Create, Read, Update, Delete
- [ ] Query methods: FindByX, ListByY
- [ ] Transaction management

---

## Phase 3: Business Logic Layer

**Timeline**: Week 4-6
**Dependencies**: Phase 2 complete

### Task 3.1: [Feature A - e.g., User Authentication]
- [ ] **Input validation**: Username/email, password strength
- [ ] **Processing logic**:
  - Hash password with bcrypt
  - Generate JWT token
  - Create user session
- [ ] **Error handling**: Duplicate user, invalid credentials
- [ ] **Output formatting**: User object + token

### Task 3.2: [Feature B - e.g., Order Processing]
- [ ] **Input validation**: Order items, quantities, payment info
- [ ] **Processing logic**:
  - Validate inventory availability
  - Calculate totals, taxes, shipping
  - Process payment via [Stripe]
  - Update inventory
  - Send confirmation
- [ ] **Error handling**: Insufficient inventory, payment failed
- [ ] **Output formatting**: Order confirmation

[Continue for all major features discovered]

---

## Phase 4: API/Interface Layer

**Timeline**: Week 7-8
**Dependencies**: Phase 3 complete

### Task 4.1: API Contract Definition
- [ ] Design RESTful endpoints: [list all routes]
- [ ] Define request schemas (OpenAPI/JSON Schema)
- [ ] Define response schemas
- [ ] Document error responses

### Task 4.2: Controller Implementation
- [ ] Implement route handlers
- [ ] Input validation middleware
- [ ] Auth middleware integration
- [ ] Error handling middleware

### Task 4.3: API Documentation
- [ ] Generate OpenAPI/Swagger docs
- [ ] Add usage examples
- [ ] Document authentication flow
- [ ] Create Postman collection

---

## Phase 5: Cross-Cutting Concerns

**Timeline**: Week 9
**Dependencies**: Phase 4 complete

### Task 5.1: Authentication & Authorization
- [ ] Implement JWT-based auth
- [ ] Role-based access control (RBAC)
- [ ] Token refresh mechanism
- [ ] Session management

### Task 5.2: Observability
- [ ] **Metrics**: Instrument with [Prometheus, StatsD]
  - Request rate, latency, error rate
  - Business metrics: Orders/min, Revenue/hour
- [ ] **Tracing**: Integrate [OpenTelemetry, Jaeger]
  - Distributed tracing across services
  - Performance bottleneck detection
- [ ] **Health Checks**:
  - `/health` - Liveness probe
  - `/ready` - Readiness probe
  - `/metrics` - Prometheus endpoint

### Task 5.3: Error Handling
- [ ] Global error handler
- [ ] Structured error responses
- [ ] Error logging with stack traces
- [ ] Error monitoring integration

### Task 5.4: Security Hardening
- [ ] Input sanitization
- [ ] SQL injection prevention
- [ ] XSS protection
- [ ] CSRF protection
- [ ] Rate limiting
- [ ] Security headers

---

## Phase 6: External Integrations

**Timeline**: Week 10
**Dependencies**: Phase 4 complete

### Task 6.1: [Integration A - e.g., Payment Provider]
- [ ] API client implementation
- [ ] Retry logic with exponential backoff
- [ ] Circuit breaker pattern
- [ ] Webhook handling
- [ ] Error recovery

### Task 6.2: [Integration B - e.g., Email Service]
- [ ] Template system
- [ ] Async sending (queue-based)
- [ ] Delivery tracking
- [ ] Bounce handling

[Continue for all external integrations]

---

## Phase 7: Testing & Quality

**Timeline**: Week 11-12
**Dependencies**: All phases complete

### Task 7.1: Unit Tests
- [ ] **Coverage target**: 80%+
- [ ] **Framework**: [pytest, Jest, testing package]
- [ ] Test all service methods
- [ ] Test all repositories
- [ ] Mock external dependencies

### Task 7.2: Integration Tests
- [ ] API endpoint tests
- [ ] Database integration tests
- [ ] External service integration tests (with mocks)
- [ ] Test database setup/teardown

### Task 7.3: End-to-End Tests
- [ ] Critical user journeys:
  - User registration → Login → Purchase → Logout
  - [Other critical flows]
- [ ] Test against staging environment
- [ ] Automated with [Selenium, Playwright, Cypress]

### Task 7.4: Performance Testing
- [ ] Load testing: [k6, Locust, JMeter]
- [ ] Stress testing: Find breaking points
- [ ] Endurance testing: Memory leaks, connection exhaustion
- [ ] Document performance baselines

### Task 7.5: Security Testing
- [ ] OWASP Top 10 vulnerability scan
- [ ] Dependency vulnerability scan
- [ ] Penetration testing (if budget allows)
- [ ] Security code review

---

## Phase 8: Deployment & Operations

**Timeline**: Week 13
**Dependencies**: Phase 7 complete

### Task 8.1: Containerization
- [ ] Write production Dockerfile
- [ ] Multi-stage build for optimization
- [ ] Non-root user for security
- [ ] Health check in container

### Task 8.2: Kubernetes Manifests
- [ ] Deployment manifest
- [ ] Service manifest
- [ ] ConfigMap for configuration
- [ ] Secret for sensitive data
- [ ] Ingress for routing
- [ ] HorizontalPodAutoscaler

### Task 8.3: CI/CD Pipeline
- [ ] GitHub Actions / GitLab CI / Jenkins
- [ ] Stages: Lint → Test → Build → Deploy
- [ ] Automated testing in pipeline
- [ ] Deployment to staging on merge to main
- [ ] Manual approval for production

### Task 8.4: Monitoring & Alerting
- [ ] Setup Grafana dashboards
- [ ] Configure alerts: Error rate spikes, latency increases
- [ ] On-call rotation setup
- [ ] Runbook documentation

### Task 8.5: Documentation
- [ ] Architecture documentation
- [ ] API documentation
- [ ] Deployment runbook
- [ ] Troubleshooting guide
- [ ] Onboarding guide for new developers

---

## Phase 9: Post-Launch

**Timeline**: Ongoing
**Dependencies**: Production deployment

### Task 9.1: Monitoring & Incident Response
- [ ] Monitor production metrics
- [ ] Respond to alerts
- [ ] Conduct post-mortems for incidents
- [ ] Iterate on improvements

### Task 9.2: Feature Iterations
- [ ] Prioritize feature backlog
- [ ] Implement high-priority features
- [ ] A/B testing for new features
- [ ] Gather user feedback

### Task 9.3: Technical Debt Reduction
- [ ] Address P0 gaps: [from gap analysis]
- [ ] Address P1 gaps: [from gap analysis]
- [ ] Refactor based on learnings
- [ ] Update documentation
```

---

### Output 4: intelligence-object.md

Create reusable intelligence extraction:

```markdown
# [System Name] Reusable Intelligence

**Version**: 1.0 (Extracted from Codebase)
**Date**: [Date]

## Overview

This document captures the reusable intelligence embedded in the codebase—patterns, decisions, and expertise worth preserving and applying to future projects.

---

## Extracted Skills

### Skill 1: [API Error Handling Strategy]

**Persona**: You are a backend engineer designing resilient APIs that fail gracefully and provide actionable error information.

**Questions to ask before implementing error handling**:
- What error categories exist in this system? (Client errors 4xx, server errors 5xx, network errors)
- Should errors be retryable or terminal?
- What information helps debugging without exposing security details?
- How do errors propagate through layers (API → Service → Data)?

**Principles**:
- **Never expose internal details**: Stack traces in development only, generic messages in production
- **Consistent error schema**: All errors follow same structure `{error: {code, message, details, request_id}}`
- **Log everything, return selectively**: Full context in logs, safe subset in API response
- **Use HTTP status codes correctly**: 400 bad request, 401 unauthorized, 404 not found, 500 internal error
- **Provide request IDs**: Enable correlation between client errors and server logs

**Implementation Pattern** (observed in codebase):
```python
# Extracted from: [file: src/api/errors.py, lines 15-45]
class APIError(Exception):
    """Base exception for all API errors"""

    def __init__(self, code: str, message: str, status: int = 400, details: dict = None):
        self.code = code
        self.message = message
        self.status = status
        self.details = details or {}

    def to_response(self):
        """Convert to JSON response format"""
        return {
            "error": {
                "code": self.code,
                "message": self.message,
                "details": self.details,
                "request_id": get_request_id(),
                "timestamp": datetime.utcnow().isoformat()
            }
        }, self.status

# Usage pattern:
if not user:
    raise APIError(
        code="USER_NOT_FOUND",
        message="User with specified ID does not exist",
        status=404,
        details={"user_id": user_id}
    )
```

**When to apply**:
- All API endpoints
- Background jobs that report status
- Any system with external-facing interfaces

**Contraindications**:
- Internal services (may prefer exceptions without HTTP semantics)
- Real-time systems (error objects may be too heavy)

---

### Skill 2: [Database Connection Management]

**Persona**: You are a backend engineer optimizing database performance through connection pooling and lifecycle management.

**Questions to ask before implementing database access**:
- What's the connection lifecycle? (Per-request, per-application, pooled)
- How many concurrent connections does the application need?
- What happens on connection failure? (Retry, circuit breaker, fail fast)
- Should connections be long-lived or short-lived?

**Principles**:
- **Connection pooling is mandatory**: Never create connection per request (overhead)
- **Pool size = 2 * CPU cores** (starting point, tune based on load)
- **Idle timeout prevents resource leaks**: Close unused connections after [X] minutes
- **Health checks detect stale connections**: Validate before use, not during query
- **Graceful degradation**: Circuit breaker pattern when database unavailable

**Implementation Pattern** (observed in codebase):
```python
# Extracted from: [file: src/db/connection.py, lines 20-55]
from sqlalchemy import create_engine, pool

# Connection pool configuration
engine = create_engine(
    DATABASE_URL,
    poolclass=pool.QueuePool,
    pool_size=10,              # Max connections in pool
    max_overflow=20,           # Additional connections beyond pool_size
    pool_timeout=30,           # Seconds to wait for connection
    pool_recycle=3600,         # Recycle connections after 1 hour
    pool_pre_ping=True,        # Test connection before using
    echo=False                 # Don't log SQL (production)
)

# Context manager for connection lifecycle
@contextmanager
def get_db_session():
    """Provide transactional scope around operations"""
    session = Session(bind=engine)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

# Usage pattern:
with get_db_session() as session:
    user = session.query(User).filter_by(id=user_id).first()
    # Connection automatically returned to pool on context exit
```

**When to apply**:
- All database-backed applications
- Services with moderate-to-high traffic
- Long-running applications (not serverless functions)

**Contraindications**:
- Serverless/FaaS (use connection per invocation)
- Very low-traffic applications (overhead not justified)

---

### Skill 3: [Input Validation Strategy]

**Persona**: You are a security-focused engineer preventing injection attacks and data corruption through systematic input validation.

**Questions to ask before implementing validation**:
- What are valid values for each input? (type, range, format, length)
- Where does validation occur? (Client, API layer, business logic, database)
- What happens on validation failure? (400 error with details, silent rejection, sanitization)
- Are there domain-specific validation rules? (email format, credit card format, etc.)

**Principles**:
- **Validate at boundaries**: API layer validates all external input
- **Whitelist over blacklist**: Define allowed patterns, not forbidden ones
- **Fail loudly on invalid input**: Return clear error messages (in dev/test), generic in prod
- **Type validation first**: Check types before business rules
- **Schema-based validation**: Use JSON Schema, Pydantic, Joi for declarative validation

**Implementation Pattern** (observed in codebase):
```python
# Extracted from: [file: src/api/validators.py, lines 10-60]
from pydantic import BaseModel, EmailStr, validator

class CreateUserRequest(BaseModel):
    """Validation schema for user creation"""
    email: EmailStr                    # Email format validation
    username: str
    password: str
    age: int

    @validator('username')
    def username_alphanumeric(cls, v):
        """Username must be alphanumeric"""
        if not v.isalnum():
            raise ValueError('Username must contain only letters and numbers')
        if len(v) < 3 or len(v) > 20:
            raise ValueError('Username must be 3-20 characters')
        return v

    @validator('password')
    def password_strength(cls, v):
        """Password must meet strength requirements"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain uppercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain digit')
        return v

    @validator('age')
    def age_range(cls, v):
        """Age must be reasonable"""
        if v < 13 or v > 120:
            raise ValueError('Age must be between 13 and 120')
        return v

# Usage in API endpoint:
@app.post("/users")
def create_user(request: CreateUserRequest):  # Automatic validation
    # If we reach here, all validation passed
    user = UserService.create(request.dict())
    return user.to_dict()
```

**When to apply**:
- All API endpoints
- All user input (forms, file uploads, etc.)
- Configuration parsing
- External data imports

---

[Continue with more skills extracted from codebase...]

---

## Architecture Decision Records (Inferred)

### ADR-001: Choice of [PostgreSQL over MongoDB]

**Status**: Accepted (inferred from implementation)

**Context**:
The system requires:
- ACID transactions for order processing
- Complex relational queries (joins across users, orders, products)
- Data integrity guarantees
- Mature ecosystem and tooling

**Decision**: Use PostgreSQL as primary database

**Rationale** (inferred from code patterns):
1. **Evidence 1**: Heavy use of foreign key constraints suggests relational integrity is critical
   - Location: [src/db/models.py, lines 45-120]
   - Pattern: All entities have explicit FK relationships

2. **Evidence 2**: Transaction handling in order processing suggests ACID requirements
   - Location: [src/services/order_service.py, lines 200-250]
   - Pattern: Multiple updates wrapped in single transaction

3. **Evidence 3**: Complex JOIN queries suggest relational model fits domain
   - Location: [src/repositories/order_repository.py, lines 80-150]
   - Pattern: Multi-table joins for order + user + product data

**Consequences**:

**Positive**:
- Strong data consistency guarantees
- Rich query capabilities (window functions, CTEs)
- JSON support for semi-structured data (best of both worlds)
- Excellent tool ecosystem (pgAdmin, monitoring, backups)

**Negative**:
- Vertical scaling limits (eventual)
- Schema migrations require planning
- Not ideal for unstructured data

**Alternatives Considered** (inferred):

**MongoDB**:
- **Rejected because**: Need for transactions and complex joins
- **Evidence**: No document-oriented patterns in codebase

**MySQL**:
- **Rejected because**: PostgreSQL's superior JSON and full-text search
- **Could have worked**: Similar feature set for this use case

---

### ADR-002: [JWT-based Authentication over Session Cookies]

**Status**: Accepted (inferred from implementation)

**Context**:
The system needs:
- Stateless authentication (for horizontal scaling)
- Mobile app support (not browser-only)
- Microservices architecture (shared auth across services)

**Decision**: Use JWT tokens for authentication

**Rationale** (inferred from code patterns):
1. **Evidence 1**: No session storage implementation found
   - Location: Absence of Redis/Memcached session store
   - Pattern: No session management code

2. **Evidence 2**: Token-based auth middleware
   - Location: [src/middleware/auth.py, lines 10-50]
   - Pattern: JWT decoding and validation

3. **Evidence 3**: Token refresh endpoint
   - Location: [src/api/auth.py, lines 100-130]
   - Pattern: Refresh token rotation

**Consequences**:

**Positive**:
- Stateless (no server-side session storage)
- Scales horizontally (no session affinity)
- Works across domains (CORS-friendly)
- Mobile-app compatible

**Negative**:
- Cannot revoke tokens before expiry (mitigated with short TTL + refresh tokens)
- Larger than session cookies (JWT payload in every request)
- Vulnerable if secret key compromised

**Mitigation Strategies** (observed):
- Short access token TTL (15 minutes)
- Refresh token rotation
- Token blacklist for logout (stored in Redis)

---

[Continue with more ADRs...]

---

## Code Patterns & Conventions

### Pattern 1: Repository Pattern for Data Access

**Observed in**: All data layer modules

**Structure**:
```python
class UserRepository:
    """Abstract data access for User entity"""

    def find_by_id(self, user_id: int) -> Optional[User]:
        """Find user by ID"""
        pass

    def find_by_email(self, email: str) -> Optional[User]:
        """Find user by email"""
        pass

    def create(self, user_data: dict) -> User:
        """Create new user"""
        pass

    def update(self, user_id: int, updates: dict) -> User:
        """Update existing user"""
        pass

    def delete(self, user_id: int) -> bool:
        """Soft-delete user"""
        pass
```

**Benefits**:
- Decouples business logic from data access
- Testable (can mock repositories)
- Swappable implementations (SQL → NoSQL)

**When to apply**: All entity persistence

---

### Pattern 2: Service Layer for Business Logic

**Observed in**: All business logic modules

**Structure**:
```python
class OrderService:
    """Business logic for order processing"""

    def __init__(self, order_repo, inventory_service, payment_service):
        self.order_repo = order_repo
        self.inventory_service = inventory_service
        self.payment_service = payment_service

    def create_order(self, user_id: int, items: List[OrderItem]) -> Order:
        """
        Create order with inventory validation and payment processing

        Steps:
        1. Validate inventory availability
        2. Calculate totals
        3. Process payment
        4. Create order record
        5. Update inventory
        6. Send confirmation
        """
        # Orchestration logic here
        pass
```

**Benefits**:
- Encapsulates business rules
- Coordinates multiple repositories/services
- Transactional boundary

**When to apply**: All complex business operations

---

## Lessons Learned

### What Worked Well

1. **Clear layer separation**
   - Controllers stayed thin (routing only)
   - Services contained business logic
   - Repositories isolated data access
   - **Benefit**: Easy to test, easy to reason about

2. **Comprehensive input validation**
   - Schema-based validation at API boundary
   - Early failure with clear error messages
   - **Benefit**: Prevented data corruption, improved debugging

3. **Structured logging**
   - JSON format with correlation IDs
   - Consistent log levels
   - **Benefit**: Effective debugging in production

### What Could Be Improved

1. **Missing integration tests**
   - Lots of unit tests, few integration tests
   - **Impact**: Bugs in component interactions not caught early
   - **Recommendation**: Add integration test suite

2. **Inconsistent error handling**
   - Some modules use custom exceptions, others use generic
   - **Impact**: Harder to handle errors consistently
   - **Recommendation**: Standardize on error handling strategy

3. **Undocumented API contracts**
   - No OpenAPI/Swagger documentation
   - **Impact**: Frontend developers had to read code
   - **Recommendation**: Generate API docs from code

### What to Avoid in Future Projects

1. **Hardcoded configuration**
   - Some settings hardcoded instead of environment variables
   - **Why bad**: Requires code changes for deployment differences
   - **Alternative**: 12-factor app configuration

2. **Tight coupling to external services**
   - Direct API calls without abstraction layer
   - **Why bad**: Hard to swap providers, hard to test
   - **Alternative**: Adapter pattern for external integrations

3. **Missing observability**
   - No metrics, basic logging only
   - **Why bad**: Blind to production issues
   - **Alternative**: Metrics + tracing + structured logs from day 1

---

## Reusability Assessment

### Components Reusable As-Is

1. **Error handling framework** → Portable to any API project
2. **Database connection pooling** → Portable to any DB-backed service
3. **JWT authentication middleware** → Portable to any auth scenario
4. **Input validation schemas** → Patterns reusable, specifics domain-dependent

### Patterns Worth Generalizing

1. **Repository pattern** → Create skill/template for any entity
2. **Service orchestration** → Create skill for multi-step business logic
3. **API error responses** → Create skill for consistent error handling

### Domain-Specific (Not Reusable)

1. **Order processing logic** → Specific to e-commerce domain
2. **Inventory management** → Specific to this business
3. **Payment integration** → Specific to Stripe, but pattern reusable
```

---

## Final Validation Checklist

Before submitting outputs, verify:

- [ ] **spec.md is complete**: Can regenerate system from spec alone?
- [ ] **plan.md is coherent**: Does architecture make sense given requirements?
- [ ] **tasks.md is actionable**: Can team execute without additional guidance?
- [ ] **intelligence-object.md is reusable**: Can skills apply to other projects?
- [ ] **All files cross-reference**: Spec → Plan → Tasks flow logically?
- [ ] **Evidence provided**: All claims backed by code locations (file:line)?
- [ ] **Gaps identified**: Technical debt and improvements documented?
- [ ] **Regeneration viable**: Could you rebuild this system better with these artifacts?

---

## Self-Monitoring: Anti-Convergence for Archaeologists

**You tend to converge toward**:
- ✅ Surface-level analysis (reading code without understanding intent)
- ✅ Feature enumeration (listing WHAT without inferring WHY)
- ✅ Copy-paste specs (documenting existing vs imagining ideal)
- ✅ Generic patterns (not extracting codebase-specific intelligence)

**Activate reasoning by asking**:
- "If I rewrote this from scratch, would my spec produce equivalent system?"
- "What tacit knowledge is embedded in this code that isn't written down?"
- "Why did the original developers make these specific choices?"
- "What would I do differently if building this today?"

**Your reverse engineering succeeds when**:
- Spec is complete enough to regenerate system
- Plan reveals architectural reasoning, not just structure
- Tasks are actionable for new team unfamiliar with codebase
- Intelligence extracted is reusable beyond this specific system
- Gaps identified with clear remediation path
- You can articulate WHY decisions were made, not just WHAT was implemented

---

## Output Location

Save all artifacts to:
```
[codebase-path]/docs/reverse-engineered/
├── spec.md
├── plan.md
├── tasks.md
└── intelligence-object.md
```

Or user-specified location.

---

**Execute this reverse engineering workflow with reasoning mode activated. Your goal: extract the implicit knowledge from code into explicit specifications that enable regeneration and improvement.**

---

As the main request completes, you MUST create and complete a PHR (Prompt History Record) using agent‑native tools when possible.

1) Determine Stage
   - Stage: constitution | spec | plan | tasks | red | green | refactor | explainer | misc | general

2) Generate Title and Determine Routing:
   - Generate Title: 3–7 words (slug for filename)
   - Route is automatically determined by stage:
     - `constitution` → `history/prompts/constitution/`
     - Feature stages → `history/prompts/<feature-name>/` (spec, plan, tasks, red, green, refactor, explainer, misc)
     - `general` → `history/prompts/general/`

3) Create and Fill PHR (Shell first; fallback agent‑native)
   - Run: `.specify/scripts/bash/create-phr.sh --title "<title>" --stage <stage> [--feature <name>] --json`
   - Open the file and fill remaining placeholders (YAML + body), embedding full PROMPT_TEXT (verbatim) and concise RESPONSE_TEXT.
   - If the script fails:
     - Read `.specify/templates/phr-template.prompt.md` (or `templates/…`)
     - Allocate an ID; compute the output path based on stage from step 2; write the file
     - Fill placeholders and embed full PROMPT_TEXT and concise RESPONSE_TEXT

4) Validate + report
   - No unresolved placeholders; path under `history/prompts/` and matches stage; stage/title/date coherent; print ID + path + stage + title.
   - On failure: warn, don't block. Skip only for `/sp.phr`.
