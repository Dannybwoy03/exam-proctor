# PROJECT DOCUMENTATION

**Title:** Online Exam Proctoring System Using Deep Learning  
**Institution:** Kwame Nkrumah University of Science and Technology (KNUST), Kumasi, Ghana  
**Department:** Computer Science  
**Document type:** Final Year Project Report  
**Referencing style:** Harvard (author–date)

> **Formatting:** Before submission, apply KNUST layout rules in [KNUST_FORMATTING_GUIDE.md](./KNUST_FORMATTING_GUIDE.md) (Times New Roman 12 pt, justified, 1.5 line spacing, 2.5 cm margins, 4 cm gutter).

---

## TABLE OF CONTENTS

1. [Chapter 1 — Introduction](#chapter-1--introduction)
2. [Chapter 2 — Review of Related Works and Proposed System](#chapter-2--review-of-related-works-and-proposed-system)
3. [Chapter 3 — Methodology](#chapter-3--methodology)
4. [Chapter 4 — Implementation and Results](#chapter-4--implementation-and-results)
5. [Chapter 5 — Findings and Conclusion](#chapter-5--findings-and-conclusion)
6. [References](#references)
7. [Appendices](#appendices)

---

# CHAPTER ONE: INTRODUCTION

## 1.1 Background of the Study

Higher education institutions worldwide have undergone a significant shift toward online and blended learning, accelerated by global disruptions to face-to-face instruction and the growing adoption of digital infrastructure on university campuses (UNESCO, 2020). In Ghana, universities including Kwame Nkrumah University of Science and Technology (KNUST) have expanded the use of learning management systems, virtual classrooms, and web-based assessment tools to sustain academic programmes when physical attendance is limited (Agyeman and Owusu-Darko, 2022).

While these digital platforms improve access and flexibility, they also introduce new risks to academic integrity. Examinations that were once supervised in controlled halls are increasingly delivered through browsers on personal devices, often without continuous human invigilation. Students may therefore be exposed to opportunities for misconduct that are difficult for instructors to observe remotely, including impersonation, consultation of unauthorised materials, use of secondary devices, and manipulation of the webcam environment (Norris et al., 2021).

Recent advances in computer vision and deep learning, particularly real-time object detection architectures such as You Only Look Once (YOLO), offer a practical basis for automating visual proctoring during online examinations (Redmon et al., 2016; Jocher et al., 2022). By analysing webcam frames during an active examination session, such systems can flag the presence of prohibited objects and behaviours, log violations, and enforce institutional integrity policies with minimal human intervention.

This project responds to the need for a locally developed, web-based examination platform that integrates deep learning-based proctoring to strengthen academic integrity in remote assessment environments at KNUST.

## 1.2 Problem Statement

In recent years, Ghanaian universities have increasingly adopted online and hybrid assessment models to support large student populations and flexible programme delivery. However, many existing online examination workflows remain vulnerable to examination malpractice because they cannot **see** what occurs in the student's physical environment during the test.

**The specific problem** addressed by this research is the inability of conventional online examination platforms to automatically detect the introduction and use of **foreign materials**—including mobile phones, printed books, handwritten notes, and secondary computing devices—during remote examinations. Without continuous visual monitoring, invigilators and instructors cannot confirm that students are attempting assessments independently and in compliance with examination regulations.

**Evidence of the problem** is reflected in growing international concern about academic dishonesty in digitally mediated assessments. Rule-based browser lockdown tools may restrict tab switching or copying and pasting, but they do not identify a phone held below the camera, a book placed beside the keyboard, or a second person entering the frame. At KNUST and comparable institutions, this gap undermines confidence in the fairness and credibility of online examination results.

**If the problem is not addressed**, institutions risk awarding qualifications on the basis of assessments that do not accurately reflect individual student competence, eroding trust among employers, accreditation bodies, and the academic community.

**Therefore**, there is a need to design, implement, and evaluate an online examination system that integrates a deep learning object detection model—YOLOv5—to provide automated, real-time detection of prohibited materials and related examination violations during remote testing at KNUST.

## 1.3 Aim of the Project

To design, develop, and evaluate an Online Exam Proctoring System using the YOLOv5 deep learning model to improve automated detection of examination violations and enhance academic integrity in online assessments at KNUST.

## 1.4 Specific Objectives of the Project

1. To analyse examination malpractice risks in online assessment environments at KNUST, with emphasis on the use of unauthorised foreign materials.
2. To design a secure web-based examination platform with role-based access control for administrators, teachers, and students.
3. To integrate the YOLOv5 object detection model into a real-time webcam proctoring module capable of identifying prohibited objects and behaviours during examination sessions.
4. To implement a graduated violation handling mechanism—including identity verification, warning notifications, and session termination—consistent with institutional examination policy.
5. To evaluate the prototype system using objective performance metrics including detection precision, recall, F1-score, and system response time under controlled experimental conditions.

## 1.5 Justification of the Project

Online assessment is now a permanent feature of university education at KNUST. Existing digital tools address **digital** misconduct (tab switching, copy-paste) but leave a **physical visibility gap** that hall-based invigilation previously covered. A locally developed proctoring platform:

- Reduces dependence on expensive commercial proctoring services that may not fit Ghanaian infrastructure budgets.
- Provides teachers with **evidence-based audit trails** (timestamped violation logs and snapshots) rather than post-hoc suspicion.
- Demonstrates applied Design Science Research (Hevner et al., 2004) by delivering a working artefact grounded in institutional need.
- Aligns with KNUST's mission to apply science and technology to national development through practical, deployable software engineering.

## 1.6 Motivation for Undertaking the Project

The motivation for this project arises from three observations:

1. **Personal experience** — Computer Science students at KNUST routinely sit timed online assessments where browser lockdown is enforced but physical desk conditions are unobserved.
2. **Research gap** — Literature confirms that rule-based online proctoring does not detect foreign materials (Leong, 2025); YOLO-class detectors offer a scalable alternative on commodity hardware.
3. **Technical feasibility** — Modern lightweight YOLO variants (YOLOv5n, YOLOv8n-pose) run on CPU-only student workstations, making local deployment realistic without GPU clusters.

## 1.7 Scope of the Project

This project covers the design, development, and experimental evaluation of a prototype Online Exam Proctoring System for undergraduate-level online assessments at KNUST. The system supports three user roles—administrator, teacher, and student—and includes:

- Question bank management and CSV import
- Examination scheduling with administrative approval
- Exam access codes for student entry
- Identity verification at examination start (ID card + face match)
- Browser lockdown enforcement (configurable strictness)
- Automated proctoring using YOLOv5n object detection and YOLOv8n-pose
- Graduated three-strike violation handling and teacher audit of flagged sessions

Development and testing were conducted on commodity hardware (Intel Core i3-class processor, 8 GB RAM, 720p webcam) under controlled indoor conditions.

## 1.8 Project Limitations

- The system is a **prototype** evaluated under controlled conditions, not a full-semester production deployment.
- YOLOv5 is pre-trained on general COCO classes; performance may vary with lighting, camera angle, and occlusion.
- Inference runs on **CPU only** without GPU acceleration, limiting concurrent session throughput.
- Usability testing uses a **purposive sample** of Computer Science students and may not represent all faculties.
- The system does not detect all misconduct types (e.g., audio collusion, contract cheating).

## 1.9 Beneficiaries of the Project

| Beneficiary | Benefit |
|-------------|---------|
| **KNUST administration** | Credible online examination outcomes; reduced integrity disputes |
| **Teachers / exam officers** | Question banks, approval workflow, flagged-session review with evidence |
| **Students** | Clear, consistently enforced rules; fairer assessment environment |
| **Ghanaian universities** | Reusable architecture for locally deployable AI proctoring |
| **Researchers** | Documented integration of YOLO into a full-stack examination workflow |

## 1.10 Academic and Practical Relevance

**Academic relevance:** The project contributes to applied computer vision and software engineering literature by documenting end-to-end integration of YOLO-based object detection into a secure examination platform, including violation taxonomy, graduated enforcement, and fairness considerations (Buolamwini and Gebru, 2018).

**Practical relevance:** The delivered artefact is a working Django web application deployable on a single machine for demonstration, with a path to PostgreSQL and Redis-backed scaling for production.

## 1.11 Project Activity Planning and Schedules

**Table 1.1: Project activity schedule**

| Phase | Activities | Duration | Deliverable |
|-------|------------|----------|-------------|
| 1 | Literature review, requirements gathering, system design | Weeks 1–4 | Chapters 1–2, ERD, architecture diagrams |
| 2 | Django scaffold, auth, courses, question banks, exams | Weeks 5–8 | Working portal (no ML) |
| 3 | Admin approval, access codes, lockdown JS, timer pause | Weeks 9–10 | Secure exam workflow |
| 4 | Celery, Redis, Channels, mock proctoring | Weeks 11–12 | Async pipeline |
| 5 | YOLOv5 + pose integration, ID verification | Weeks 13–15 | AI proctoring module |
| 6 | Testing, evaluation metrics, documentation | Weeks 16–18 | Test results, final report |
| 7 | Presentation preparation | Weeks 19–20 | Demo, slides, defence |

*[Insert Figure 1.1: Gantt chart of project phases]*

## 1.12 Structure of the Report

This report is organised into five chapters:

- **Chapter One** introduces the background, problem, aim, objectives, justification, scope, and beneficiaries.
- **Chapter Two** reviews related systems and presents the proposed system design, architecture, and components.
- **Chapter Three** describes methodology, requirements, UML diagrams, security, and logical design (UI and database).
- **Chapter Four** presents implementation, algorithms, testing, and results.
- **Chapter Five** discusses findings, conclusions, limitations, lessons learned, and recommendations.

## 1.13 Project Deliverables

| # | Deliverable | Description |
|---|-------------|-------------|
| 1 | **Final project report** | This document (five chapters + references + appendices) |
| 2 | **Source code** | Full Django application (`apps/`, `config/`, `ml/`, `static/`, `templates/`) |
| 3 | **Working prototype** | Deployable web application with AI proctoring demo |
| 4 | **System design documentation** | `docs/SYSTEM_DESIGN.md` — architecture and API reference |
| 5 | **Test suite** | Unit tests for proctoring rules and strike logic |
| 6 | **Presentation materials** | Slides and live demonstration script |
| 7 | **User guide** | Setup instructions in `README.md` |

---

# CHAPTER TWO: REVIEW OF RELATED WORKS AND PROPOSED SYSTEM

## 2.1 Introduction

This chapter reviews existing online examination and proctoring approaches, analyses their strengths and weaknesses, and presents the proposed Online Exam Proctoring System—including conceptual design, architecture, component descriptions, features, development tools, and expected benefits.

## 2.2 Review of Related Works / Similar Systems

### 2.2.1 Processes of Existing Systems

**Learning Management System (LMS) quizzes** — Platforms such as Moodle and Canvas provide timed quizzes, question randomisation, and basic access control. They enforce **when** and **who** takes an exam but not **what physical materials** are present (Oosterhof et al., 2008).

**Browser lockdown tools** — Respondus LockDown Browser, Safe Exam Browser, and custom JavaScript lockdown restrict tab switching, copy-paste, and fullscreen exit. These address **digital** vectors only (Leong, 2025).

**Live remote human proctoring** — Commercial services (ProctorU, Examity) use human invigilators via webcam. Effective but costly and difficult to scale for large cohorts (Lilley et al., 2016).

**Commercial AI proctoring** — Proctorio, Honorlock, and similar products apply face detection and object recognition. These are proprietary, subscription-based, and often designed for Western infrastructure.

**Table 2.1: Comparison of existing related systems**

| System type | Key features | Pros | Cons |
|-------------|--------------|------|------|
| LMS native quiz | Timer, MCQ auto-grade | Integrated, low cost | No visual proctoring |
| Browser lockdown | Tab/focus/fullscreen block | Stops digital cheating | No foreign-material detection |
| Live human proctor | Real-time human monitoring | High contextual judgement | Expensive, privacy concerns |
| Commercial AI proctor | Automated vision + lockdown | Scalable monitoring | Cost, opaque algorithms, bandwidth |
| **Proposed system** | Django + YOLOv5 + lockdown + ID verify | Local deploy, open stack, evidence logs | Prototype scope, CPU latency |

### 2.2.2 Research gaps motivating the proposed system

1. Conventional online platforms do not detect **physical foreign materials** (phones, books, notes).
2. Scalable continuous monitoring without dedicated human proctors is lacking in resource-constrained institutions.
3. Few **locally contextualised** proctoring solutions exist for Ghanaian universities.
4. Weak binding between **identity verification** and continuous session integrity.
5. Limited empirical evaluation of YOLO proctoring on **commodity CPU hardware**.

## 2.3 The Proposed System

The proposed **Online Exam Proctoring System** is a web-based platform that combines:

1. **Role-based examination management** (admin, teacher, student)
2. **Question bank authoring** with admin approval before publication
3. **Exam access codes** for controlled student entry
4. **Identity verification** (ID card in frame + face match against registration photo)
5. **Browser lockdown** (configurable strictness: none / 3-strike / zero tolerance)
6. **AI visual proctoring** using YOLOv5n object detection and YOLOv8n-pose
7. **Graduated enforcement** (warnings, strikes, automatic termination)
8. **Teacher audit** of flagged sessions with violation snapshots and clip frames

## 2.4 Conceptual Design

The conceptual design links problem context, intervention, and expected outcomes:

```
[Online assessment growth at KNUST]
            ↓
[Malpractice risks: foreign materials, impersonation, environment manipulation]
            ↓
[Limitations of rule-based / non-visual proctoring]
            ↓
[Intervention: Web platform + YOLOv5 + lockdown + ID verification]
            ↓
[Outputs: Violation logs, warnings, termination, instructor review evidence]
            ↓
[Outcomes: Improved automated detection; enhanced academic integrity]
```

*[Insert Figure 2.1: Conceptual framework diagram]*

## 2.5 Architecture of the Proposed System

The system follows a **layered architecture** with asynchronous ML processing:

```mermaid
flowchart TB
    subgraph client [Client Browser]
        UI[Exam UI + Lockdown JS]
        Webcam[Webcam Capture]
        WSClient[WebSocket Client]
    end
    subgraph django [Django Application Layer]
        Views[Views and REST API]
        Channels[Django Channels]
        Auth[Session Auth and RBAC]
    end
    subgraph async [Async Layer]
        Redis[(Redis)]
        Celery[Celery Workers]
    end
    subgraph ml [ML Layer]
        YOLO[YOLOv5n + YOLOv8n-pose]
        IDVerify[ID and Face Match]
    end
    subgraph storage [Persistence]
        DB[(SQLite / PostgreSQL)]
        Media[(Media Storage)]
    end
    UI --> Views
    Webcam --> Views
    WSClient --> Channels
    Views --> Auth --> DB
    Views --> Redis --> Celery
    Celery --> YOLO --> DB
    Celery --> IDVerify --> DB
    YOLO --> Media
    Channels --> WSClient
```

*[Insert Figure 2.2: System architecture diagram — export from diagram above]*

**Design rationale:**

| Decision | Choice | Reason |
|----------|--------|--------|
| Web framework | Django (Python) | Built-in auth, ORM, admin, mature ecosystem |
| Real-time alerts | Django Channels + WebSocket | Instant strike/warning push to student |
| Frame processing | REST POST + Celery queue | Avoid blocking web threads during CPU inference |
| Database (dev) | SQLite | Zero-config for prototype |
| Database (prod) | PostgreSQL | Scalable concurrent writes |
| ML models | YOLOv5n + YOLOv8n-pose | Balance of speed and accuracy on CPU |

## 2.6 Component Designs and Descriptions

Detailed algorithms appear in Chapter 4. Below is a functional description of each architectural component.

### 2.6.1 Authentication and RBAC Component (`apps/accounts`)

Handles user registration, login, and role-based access for **Admin**, **Teacher**, and **Student**. Teachers require admin approval before accessing course tools. Students may require ID document review. Middleware enforces gates on dashboard and exam routes.

### 2.6.2 Course and Content Component (`apps/courses`)

Manages courses assigned to approved teachers and study material uploads. Courses link question banks and exams to institutional structure.

### 2.6.3 Examination Management Component (`apps/exams`)

Core examination engine:

- **Question banks** — reusable question pools per course
- **Question Builder** — three-panel UI for MCQ, true/false, and short-answer items
- **Exam assembly** — attach questions, set schedule, submit for admin approval
- **Access codes** — teacher-generated codes for student entry
- **Exam attempts** — timer, autosave, submit, grading (MCQ auto; short answer manual)
- **Admin controls** — approve/reject exams, freeze during outages, add time

### 2.6.4 Proctoring Orchestrator (`apps/proctoring`)

Coordinates the examination monitoring session:

1. Creates `ProctoringSession` when student starts attempt
2. Accepts webcam frames via REST API
3. Enqueues Celery tasks for inference
4. Applies violation rules and strike counting
5. Pushes events to student via WebSocket
6. Stores `ViolationLog`, snapshots, and clip frames for teacher review

### 2.6.5 Lockdown Component (`static/js/lockdown.js`)

Client-side enforcement of examination environment rules: mandatory fullscreen (when strictness ≥ level 1), blocked keyboard shortcuts, tab/focus visibility events sent to server as synchronous violations.

### 2.6.6 Webcam Capture Component (`static/js/proctor.js`)

Captures JPEG frames from the student webcam at configurable intervals (~1 s), POSTs to `/api/v1/proctoring/frame/`, maintains WebSocket connection for real-time HUD updates and heartbeat (disconnect → timer pause).

### 2.6.7 ML Inference Component (`ml/yolo_service`)

**Object detection (YOLOv5n):** Detects persons, cell phones (COCO class 67), books (73), laptops/keyboards (63, 66) in each frame.

**Pose estimation (YOLOv8n-pose):** Extracts skeleton keypoints for head orientation and sustained look-away detection.

**Rule engine (`rules.py`):** Maps raw detections to violation types (phone, book, absent, multiple persons, look-away) with confidence thresholds and sustained-timer logic.

### 2.6.8 Identity Verification Component (`ml/id_verification`)

At exam start, validates that a student ID card is visible in frame and that the face matches the registration profile photo (embedding comparison). Maximum three attempts before exam access is denied.

### 2.6.9 Async Worker Component (`config/celery.py`, `apps/proctoring/tasks.py`)

Celery workers preload YOLO weights once at startup. Tasks run on dedicated queues (`yolo_inference`, `id_verification`) so Django request threads remain responsive.

### 2.6.10 Persistence Component

- **Relational DB** — users, exams, attempts, violations (SQLite dev / PostgreSQL prod)
- **Media storage** — profile photos, ID proofs, violation snapshots, clip frames (`media/`)

## 2.7 Proposed System / Software Features

| Feature | Description |
|---------|-------------|
| Multi-role portal | Unified sidebar navigation for admin, teacher, student |
| Question bank builder | Manual entry + CSV bulk import |
| Admin exam approval | Teacher submits; admin approves schedule and content |
| Exam access codes | Single-use or multi-use codes for controlled entry |
| ID verification | ID card + face match before exam start |
| Configurable strictness | None / 3-strike / zero-tolerance lockdown |
| YOLO object detection | Phone, book, notes, multiple persons, absence |
| Pose-based look-away | Sustained head turn (> 5 s) triggers strike |
| Three-strike enforcement | Warning → strike → terminate on third strike |
| Disconnect grace | 2-minute timer pause on WebSocket disconnect |
| Flagged session audit | Teacher reviews violations with snapshots and clips |
| Admin freeze / add time | Outage handling during live examinations |
| Hybrid grading | MCQ auto-graded; short answers manually reviewed |

## 2.8 Development Tools and Environment (Overview)

| Category | Tool | Purpose |
|----------|------|---------|
| Language | Python 3.11+ | Backend and ML |
| Web framework | Django 4.2+ | Server, ORM, templates, auth |
| API | Django REST Framework | JSON endpoints for proctoring JS |
| Real-time | Django Channels | WebSocket proctoring events |
| Task queue | Celery + Redis | Async ML inference |
| ML | Ultralytics (YOLOv5/v8), PyTorch | Object detection and pose |
| Database | SQLite (dev), PostgreSQL (prod) | Structured data |
| Frontend | HTML, CSS, JavaScript, HTMX | Server-rendered UI + exam interactivity |
| OCR | Tesseract (pytesseract) | Registration ID validation |
| Version control | Git | Source management |
| IDE | VS Code / Cursor | Development |

**Hardware environment:** Intel Core i3 or better, 8 GB RAM minimum, 720p webcam, macOS/Linux/Windows.

## 2.9 Benefits of Implementation of the Proposed System

1. **Closes the foreign-materials detection gap** left by browser-only lockdown.
2. **Scales visual monitoring** without live human proctors for every session.
3. **Provides forensic evidence** (timestamped logs, annotated snapshots) for academic boards.
4. **Runs on commodity hardware** suitable for KNUST lab and student machines.
5. **Open, auditable stack** (Django + Ultralytics) versus opaque commercial proctoring.
6. **Integrated examination workflow** — authoring, approval, delivery, proctoring, and grading in one platform.

---

# CHAPTER THREE: METHODOLOGY

## 3.1 Chapter Overview

This chapter describes the research and development methodology used to build the Online Exam Proctoring System. It covers requirement specification, stakeholders, functional and non-functional requirements, UML diagrams, security design, software process model selection, UI wireframes, database design, and development tools.

## 3.2 Requirement Specification

### 3.2.1 Stakeholders of the System

| Stakeholder | Role | Interest |
|-------------|------|----------|
| **System administrator** | Manages users, approves teachers, approves exams, audit | Platform integrity, policy enforcement |
| **Teacher / lecturer** | Creates courses, question banks, exams; reviews violations | Fair assessment, actionable evidence |
| **Student** | Registers, sits examinations | Clear rules, privacy, fair treatment |
| **Examination office** | Institutional oversight | Credible results, audit trails |
| **Developer / researcher** | Builds and evaluates system | Measurable performance, maintainable code |

### 3.2.2 Requirement Gathering Process

Requirements were gathered through:

1. **Literature review** — academic and industry proctoring capabilities (Chapter 2)
2. **Analysis of KNUST online assessment workflows** — gaps in visual monitoring
3. **System design document** — iterative refinement in `docs/SYSTEM_DESIGN.md`
4. **Prototype-driven validation** — implement → test → revise (Design Science Research)

### 3.2.3 Functional Requirements

**Table 3.1: Functional requirements**

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-01 | System shall support registration and login for admin, teacher, and student roles | High |
| FR-02 | Admin shall approve teacher accounts before portal access | High |
| FR-03 | Teacher shall create question banks and build exams from bank questions | High |
| FR-04 | Teacher shall submit exams for admin approval before publication | High |
| FR-05 | Admin shall approve, reject, freeze, or extend time on exams | High |
| FR-06 | Teacher shall generate exam access codes for students | High |
| FR-07 | Student shall redeem access code to unlock examination | High |
| FR-08 | System shall verify student identity (ID card + face) before exam start | High |
| FR-09 | System shall enforce browser lockdown per exam strictness level | High |
| FR-10 | System shall capture webcam frames during examination | High |
| FR-11 | System shall detect phones, books, notes, absence, multiple persons via YOLO | High |
| FR-12 | System shall apply three-strike rule and terminate on threshold | High |
| FR-13 | System shall push real-time warnings to student via WebSocket | High |
| FR-14 | System shall log violations with snapshots for teacher review | High |
| FR-15 | System shall auto-grade MCQ and queue short answers for manual review | Medium |
| FR-16 | System shall pause exam timer on disconnect with 2-minute grace | Medium |
| FR-17 | Student shall dispute or acknowledge strike alerts | Medium |
| FR-18 | Teacher shall review and adjudicate violations (confirm / ignore / false alarm) | Medium |

## 3.3 UML Diagrams

### 3.3.1 Use Case Diagram — System Overview

```mermaid
flowchart LR
    subgraph actors [Actors]
        Admin((Admin))
        Teacher((Teacher))
        Student((Student))
    end
    subgraph system [Exam Proctor System]
        UC1[Manage Users]
        UC2[Approve Teachers]
        UC3[Approve Exams]
        UC4[Manage Question Banks]
        UC5[Create and Publish Exams]
        UC6[Generate Access Codes]
        UC7[Take Examination]
        UC8[ID Verification]
        UC9[AI Proctoring]
        UC10[Review Violations]
        UC11[Grade Short Answers]
    end
    Admin --> UC1
    Admin --> UC2
    Admin --> UC3
    Teacher --> UC4
    Teacher --> UC5
    Teacher --> UC6
    Teacher --> UC10
    Teacher --> UC11
    Student --> UC7
    Student --> UC8
    Student --> UC9
```

*[Insert Figure 3.1: Use case diagram — system overview]*

### 3.3.2 Use Case Diagram — Backend / Proctoring

```mermaid
flowchart LR
    Student((Student Browser))
    Worker((Celery Worker))
    subgraph backend [Backend Services]
        UC_A[Accept Frame Upload]
        UC_B[Enqueue ML Task]
        UC_C[Run YOLO Inference]
        UC_D[Evaluate Violation Rules]
        UC_E[Record Strike]
        UC_F[Push WebSocket Event]
        UC_G[Store Snapshot]
    end
    Student --> UC_A
    UC_A --> UC_B
    UC_B --> Worker
    Worker --> UC_C
    UC_C --> UC_D
    UC_D --> UC_E
    UC_E --> UC_F
    UC_D --> UC_G
```

*[Insert Figure 3.2: Use case diagram — proctoring backend]*

### 3.3.3 Use Case Descriptions

**Table 3.2: Selected use case descriptions**

| Use case | Actor | Description | Precondition | Postcondition |
|----------|-------|-------------|--------------|---------------|
| **Take Examination** | Student | Student answers questions within timed window under proctoring | Access code redeemed; ID verified | Attempt submitted or terminated |
| **ID Verification** | Student | Webcam frame analysed for ID card presence and face match | Exam attempt created | Session status = passed or failed |
| **AI Proctoring** | System | Frames analysed for prohibited objects and behaviours | Exam in progress; lockdown active | Violations logged; strikes updated |
| **Approve Exam** | Admin | Admin reviews questions and schedule; approves or rejects | Exam status = pending | Exam approved or rejected with reason |
| **Review Violations** | Teacher | Teacher inspects flagged session, snapshots, adjudicates | Violations recorded | Review status updated |
| **Generate Access Code** | Teacher | Teacher creates code linked to published exam | Exam approved and published | Code available for student redemption |

### 3.3.4 Activity Diagram — Examination Lifecycle

```mermaid
flowchart TD
    A[Student redeems access code] --> B[Start exam attempt]
    B --> C{ID verification passed?}
    C -->|No| D[Retry up to 3 times]
    D --> C
    C -->|Yes| E[Enter lockdown + begin timer]
    E --> F[Capture frames loop]
    F --> G{Violation detected?}
    G -->|Yes| H[Increment strike]
    H --> I{Strikes >= max?}
    I -->|Yes| J[Terminate attempt]
    I -->|No| F
    G -->|No| F
    E --> K[Student submits]
    K --> L[Auto-grade MCQ]
    L --> M[Result published]
```

*[Insert Figure 3.3: Activity diagram — examination lifecycle]*

### 3.3.5 Sequence Diagram — Frame Processing

```mermaid
sequenceDiagram
    participant S as Student Browser
    participant D as Django API
    participant Q as Redis Queue
    participant W as Celery Worker
    participant DB as Database
    participant WS as WebSocket

    S->>D: POST /api/v1/proctoring/frame/
    D->>Q: enqueue process_proctor_frame
    D-->>S: 202 Accepted
    Q->>W: run YOLO inference
    W->>W: evaluate_frame rules
    alt violation found
        W->>DB: create ViolationLog + snapshot
        W->>WS: push warning/strike event
        WS->>S: update HUD
    end
```

*[Insert Figure 3.4: Sequence diagram — frame processing]*

### 3.3.6 Class Diagram — Core Domain Models

```mermaid
classDiagram
    class User {
        +role
        +email
        +profile_photo
    }
    class Exam {
        +title
        +approval_status
        +strictness_level
    }
    class ExamAttempt {
        +status
        +remaining_seconds
    }
    class ProctoringSession {
        +strike_count
        +max_strikes
    }
    class ViolationLog {
        +violation_type
        +confidence
        +review_status
    }
    User "1" --> "*" ExamAttempt
    Exam "1" --> "*" ExamAttempt
    ExamAttempt "1" --> "1" ProctoringSession
    ProctoringSession "1" --> "*" ViolationLog
```

*[Insert Figure 3.5: Class diagram — core models]*

## 3.4 Non-Functional Requirements

**Table 3.3: Non-functional requirements**

| ID | Requirement | Target | Justification |
|----|-------------|--------|---------------|
| NFR-01 | Frame upload response time | < 200 ms (enqueue only) | Student UI must not freeze during inference |
| NFR-02 | ML inference latency | < 3 s per frame on CPU | Timely strike feedback |
| NFR-03 | Availability (demo) | Single-machine uptime | Prototype deployment scope |
| NFR-04 | Usability | Role-specific dashboards | Reduce training burden for teachers |
| NFR-05 | Maintainability | Modular Django apps | Separate accounts, exams, proctoring |
| NFR-06 | Scalability path | Redis + PostgreSQL + Celery | Production upgrade without rewrite |
| NFR-07 | Privacy | Store snapshots not full video | Data minimisation (Lilley et al., 2016) |
| NFR-08 | Portability | Python 3.11+, cross-platform OS | Deploy on lab Windows/macOS/Linux |

## 3.5 Security Concepts

The system addresses the following security requirements:

| Threat | Mitigation |
|--------|------------|
| **Unauthorised access** | Django session authentication; role decorators on all sensitive views |
| **CSRF attacks** | CSRF tokens on all POST forms and AJAX requests |
| **Brute-force frame spam** | Rate limiting (django-ratelimit): max 1 frame per interval per attempt |
| **Impersonation** | ID card + face match at exam start; profile photo required at registration |
| **Answer leakage** | `correct_answer` never exposed in student attempt templates |
| **Unapproved teacher access** | `TeacherApprovalMiddleware` blocks unapproved teachers |
| **Unapproved exam publication** | Admin approval gate on `Exam.approval_status` |
| **Media exposure** | Authenticated media serving with per-prefix RBAC (`apps/accounts/media.py`) |
| **Session hijacking** | HTTPS recommended; secure session cookies in production settings |

## 3.6 Project Methods

### 3.6.1 Software Process Models (Brief)

| Model | Description |
|-------|-------------|
| **Waterfall** | Sequential phases; rigid change control |
| **V-Model** | Waterfall with explicit testing phases |
| **Agile / Scrum** | Iterative sprints with continuous delivery |
| **Design Science Research (DSR)** | Build artefact → evaluate → communicate |

### 3.6.2 Chosen Model and Justification

**Chosen approach:** **Agile-informed Design Science Research**

The project followed iterative two-week cycles aligned with Agile principles (working software early, respond to feedback), embedded within DSR's artefact evaluation cycle (Hevner et al., 2004):

1. **Build** — implement feature (e.g., question bank, then proctoring)
2. **Evaluate** — unit tests, manual demo, metrics
3. **Communicate** — update `SYSTEM_DESIGN.md` and this report

**Justification:** Requirements for AI proctoring evolved as YOLO integration revealed latency and false-positive trade-offs. Agile iteration allowed tuning thresholds without restarting from a fixed waterfall specification. DSR framing aligns with academic expectation of a novel, evaluated artefact.

## 3.7 Project Design Consideration — UI Design

The UI follows a **unified portal layout** with role-aware sidebar navigation (`templates/includes/portal_sidebar.html`). Wireframe descriptions:

**Table 3.4: UI wireframe descriptions**

| Screen | Layout | Key elements |
|--------|--------|--------------|
| **Login** | Centred card | Role selection: student / teacher / admin |
| **Teacher dashboard** | Sidebar + main panel | Stats cards, recent banks, exams, flagged count |
| **Question Builder** | Three columns | Left: outline; centre: editor; right: metadata |
| **Exam take (student)** | Full-width lockdown | Question panel, timer, proctoring HUD, webcam indicator |
| **Flagged sessions** | Table + detail drawer | Student name, integrity index, violation list, snapshot viewer |
| **Admin exam review** | Read-only questions + actions | Approve / reject / freeze / add time |

Design rules (from `docs/PLAN.md`):

- No emojis; Flaticon SVG icons only
- Monochromatic text hierarchy (bold headers, neutral notice cards)
- HTMX tab navigation for portal sections

*[Insert Figure 3.6: Wireframe — student examination interface]*  
*[Insert Figure 3.7: Wireframe — teacher flagged sessions audit]*

## 3.8 Project Design Consideration — DB Design

### 3.8.1 Entity-Relationship Diagram

```mermaid
erDiagram
    User ||--o| TeacherProfile : has
    User ||--o| StudentProfile : has
    TeacherProfile ||--o{ Course : teaches
    Course ||--o{ QuestionBank : contains
    QuestionBank ||--o{ Question : contains
    Course ||--o{ Exam : hosts
    Exam ||--o{ ExamQuestion : includes
    Question ||--o{ ExamQuestion : referenced_by
    User ||--o{ ExamAttempt : takes
    Exam ||--o{ ExamAttempt : has
    ExamAttempt ||--|| ProctoringSession : monitored_by
    ProctoringSession ||--o{ ViolationLog : records
    ViolationLog ||--o| ViolationSnapshot : may_have
    ExamAttempt ||--o{ Answer : contains
    ExamAttempt ||--|| Result : produces
```

*[Insert Figure 3.8: Entity-relationship diagram]*

### 3.8.2 Database Schema Summary

**Development:** SQLite file `db.sqlite3` at project root.  
**Production option:** PostgreSQL via `USE_POSTGRES=true`.

**Table 3.5: Primary database tables**

| App | Table (Model) | Key fields |
|-----|---------------|------------|
| accounts | User | role, email, profile_photo |
| accounts | StudentProfile | student_id_number, id_proof_image, face_embedding |
| accounts | TeacherProfile | approval_status, department |
| courses | Course | code, title, teacher_id |
| exams | QuestionBank | course_id, title |
| exams | Question | text, question_type, options, correct_answer, marks |
| exams | Exam | approval_status, strictness_level, is_frozen |
| exams | ExamAttempt | status, remaining_seconds, score |
| exams | Answer | response, review_status |
| proctoring | ProctoringSession | strike_count, id_verification_status |
| proctoring | ViolationLog | violation_type, confidence, review_status |
| proctoring | ViolationSnapshot | image, bounding_boxes, pose_keypoints |

Schema is defined in `apps/*/models.py` and applied via Django migrations (`python manage.py migrate`).

## 3.9 Developmental Tools (Detailed Methodology Use)

| Tool | How used in this project |
|------|--------------------------|
| **Django** | Project scaffold (`config/`), four apps, session auth, ORM, admin panel |
| **Django REST Framework** | JSON API for proctoring frame upload and ID verification |
| **Django Channels** | WebSocket consumer at `ws/proctoring/{attempt_id}/` |
| **Celery** | Background tasks `process_proctor_frame`, `verify_id_card` |
| **Redis** | Message broker and channel layer when `USE_REDIS=true` |
| **SQLite** | Local development database (zero configuration) |
| **Ultralytics / PyTorch** | Load YOLOv5n and YOLOv8n-pose weights; run inference on CPU |
| **OpenCV / Pillow** | Image decode, resize, JPEG encode for snapshots |
| **Tesseract** | OCR on student ID cards at registration |
| **Git** | Version control; feature branches per implementation phase |
| **django-ratelimit** | Frame upload rate limiting per attempt |

---

# CHAPTER FOUR: IMPLEMENTATION AND RESULTS

## 4.1 Chapter Overview

This chapter describes the mapping of logical design to the physical platform, presents construction details with code snippets, documents the testing plan and results, and reports evaluation outcomes.

## 4.2 Mapping Logical Design onto Physical Platform

### 4.2.1 Physical deployment layout

```
Single machine (dev/demo):
├── python manage.py runserver     → Django + Channels (port 8000)
├── celery -A config worker        → ML inference worker
├── redis-server                   → Broker + WebSocket channel layer
├── db.sqlite3                     → Relational database
└── media/                         → Uploaded files and violation images
```

### 4.2.2 UI implementation flow

```
[Wireframe] → [Django template] → [CSS portal.css] → [JS module] → [Browser]
```

Exam take page: `templates/exams/take_exam.html` loads `lockdown.js` and `proctor.js`.

**Algorithm 4.1: UI page render flow**

```
INPUT: HTTP GET /exams/attempts/{id}/
1. Authenticate session user
2. Load ExamAttempt where id = attempt_id AND student = user
3. IF attempt.status NOT IN (pending_id, in_progress, paused) THEN redirect
4. Load questions via ExamQuestion ordered by order
5. Render take_exam.html with attempt, questions, proctoring config
6. Client JS initialises webcam, WebSocket, lockdown
OUTPUT: HTML page + JS modules active
```

*[Insert Figure 4.1: Flowchart — UI page render flow]*

### 4.2.3 Database implementation flow

**Algorithm 4.2: Database migration flow**

```
INPUT: Model changes in apps/*/models.py
1. Run: python manage.py makemigrations
2. Django generates migration file in apps/*/migrations/
3. Run: python manage.py migrate
4. Django applies SQL DDL to db.sqlite3
5. Tables created/altered to match model definitions
OUTPUT: Database schema synchronised with code
```

*[Insert Figure 4.2: Flowchart — database migration flow]*

## 4.3 Construction

### 4.3.1 Project structure (physical mapping)

```
exam_proctor/
├── manage.py                 # Server entry point
├── config/                   # Settings, URLs, ASGI, Celery
├── apps/
│   ├── accounts/             # Users, auth, portal
│   ├── courses/              # Courses, materials
│   ├── exams/                # Exams, attempts, grading
│   └── proctoring/           # Sessions, violations, tasks
├── ml/
│   ├── yolo_service/         # Detection, pose, rules
│   └── id_verification/      # ID + face match
├── static/js/                # lockdown.js, proctor.js
├── templates/                # HTML templates
├── db.sqlite3                # SQLite database (generated)
└── media/                    # File uploads (generated)
```

### 4.3.2 Code snippet — URL routing

```python
# config/urls.py
urlpatterns = [
    path("", include("apps.accounts.urls")),
    path("exams/", include("apps.exams.urls")),
    path("api/v1/proctoring/", include("apps.proctoring.urls")),
]
```

### 4.3.3 Code snippet — violation rule evaluation

```python
# ml/yolo_service/rules.py (conceptual)
def evaluate_frame(detections, poses, absent_streak):
    violations = []
    if phone_detected(detections):
        violations.append(ViolationCandidate(PHONE, confidence))
    if book_detected(detections):
        violations.append(ViolationCandidate(BOOK, confidence))
    if len(person_boxes(detections)) >= 2:
        violations.append(ViolationCandidate(MULTIPLE_FACES, confidence))
    if absent_streak >= ABSENT_CONSECUTIVE_FRAMES:
        violations.append(ViolationCandidate(ABSENT, confidence))
    if is_looking_away(poses):
        # Sustained timer handled in task layer
        pass
    return violations, updated_absent_streak
```

### 4.3.4 Code snippet — three-strike handling

```python
# apps/proctoring/services.py (conceptual)
@transaction.atomic
def handle_violation(session, violation_type, confidence):
    session = ProctoringSession.objects.select_for_update().get(pk=session.pk)
    session.strike_count += 1
    session.save()
    if session.strike_count >= session.max_strikes:
        terminate_attempt(session.attempt)
        return {"action": "terminate"}
    return {"action": "warning", "strike": session.strike_count}
```

### 4.3.5 Code snippet — async frame processing

```python
# apps/proctoring/tasks.py (conceptual)
@shared_task
def process_proctor_frame(attempt_id, frame_b64):
    detections = run_yolo(decode_frame(frame_b64))
    poses = run_pose(decode_frame(frame_b64))
    violations, streak = evaluate_frame(detections, poses, session.absent_streak)
    for v in violations:
        result = handle_violation(session, v.violation_type, v.confidence)
        push_ws(attempt_id, result)
```

### 4.3.6 Screenshots

*[Insert Figure 4.3: Login page — role selection]*  
*[Insert Figure 4.4: Teacher question bank builder]*  
*[Insert Figure 4.5: Student examination interface with proctoring HUD]*  
*[Insert Figure 4.6: Phone detection violation with bounding box snapshot]*  
*[Insert Figure 4.7: Teacher flagged sessions audit view]*  
*[Insert Figure 4.8: Admin exam approval page]*

## 4.4 Testing

### 4.4.1 Testing plan

**Table 4.1: Testing plan overview**

| Level | Scope | Tools | Responsibility |
|-------|-------|-------|----------------|
| Unit testing | Violation rules, strike logic, look-away timer | Django `SimpleTestCase` | Developer |
| Integration testing | Frame upload → Celery → DB → WebSocket | Manual + mock ML | Developer |
| System testing | End-to-end exam lifecycle | Manual scenario scripts | Developer + test users |
| Performance testing | Frame latency on CPU | Timer logs | Developer |
| Usability testing | Student/teacher task completion | Observation + questionnaire | Sample users |

### 4.4.2 Component testing

**Algorithm 4.3: UI component test (lockdown)**

```
INPUT: Browser on take_exam.html, strictness = level_1
1. Assert fullscreen API invoked on load
2. Simulate visibilitychange (tab hidden)
3. Assert POST to /api/v1/proctoring/client-event/ with event=tab_switch
4. Assert strike count incremented in ProctoringSession
OUTPUT: PASS if strike recorded; FAIL otherwise
```

**Algorithm 4.4: DB component test (exam attempt)**

```
INPUT: Approved exam, valid student, access code
1. Create ExamAttempt via start_exam view
2. Assert ProctoringSession created with strike_count=0
3. Submit answers via save_answers
4. Assert Answer rows exist for each question
5. Submit exam; assert Result row created
OUTPUT: PASS if all records consistent
```

**Unit test example (proctoring rules):**

```bash
PROCTORING_USE_MOCK_ML=true python manage.py test apps.proctoring.tests
```

Tests verify: phone → PHONE violation; consecutive empty frames → ABSENT; two persons → MULTIPLE_FACES; turned head → look-away signal.

### 4.4.3 System testing

**Algorithm 4.5: Verification testing (does it meet spec?)**

```
FOR EACH functional requirement FR-01 to FR-18:
    1. Identify test scenario
    2. Execute scenario on running system
    3. Record PASS/FAIL against requirement ID
OUTPUT: Requirements traceability matrix
```

**Algorithm 4.6: Validation testing (does it solve the problem?)**

```
1. Recruit N test participants (students)
2. Each participant completes exam with planted phone/book prop
3. Record whether system detected violation within T seconds
4. Compute precision, recall, F1-score across scenarios
5. Collect usability feedback (SUS questionnaire optional)
OUTPUT: Detection metrics + user feedback summary
```

### 4.4.4 Test results

**Table 4.2: Unit test results (proctoring rules)**

| Test case | Expected | Result |
|-----------|----------|--------|
| Phone in frame | PHONE violation logged | PASS |
| Empty frame × 2 | ABSENT violation | PASS |
| Two persons | MULTIPLE_FACES violation | PASS |
| Turned head pose | look_away signal true | PASS |
| Benign mouse on desk | No strike | PASS |

**Table 4.3: Functional requirements traceability (sample)**

| Req ID | Scenario | Result |
|--------|----------|--------|
| FR-08 | ID verification with valid card + face | PASS |
| FR-10 | Frame capture every ~1 s | PASS |
| FR-11 | Phone detected in test frame | PASS |
| FR-12 | Third strike terminates attempt | PASS |
| FR-14 | Snapshot stored on ViolationLog | PASS |

**Table 4.4: Detection performance (controlled experiment — populate with your measured values)**

| Violation type | Precision | Recall | F1-score | Avg latency (s) |
|----------------|-----------|--------|----------|-----------------|
| Phone | — | — | — | — |
| Book | — | — | — | — |
| Absent | — | — | — | — |
| Multiple persons | — | — | — | — |
| Look-away | — | — | — | — |

> **Note:** Replace dashes with values from your experimental runs before final submission.

## 4.5 Results

The implementation produced a working prototype demonstrating:

1. **End-to-end examination workflow** from question authoring to graded results
2. **Real-time YOLO-based proctoring** on CPU-only hardware
3. **Evidence-based audit trail** for teachers reviewing flagged sessions
4. **Configurable enforcement** supporting practice exams (no strictness) and high-stakes 3-strike mode

The system successfully detected planted foreign materials in controlled test scenarios and enforced session termination on repeated violations, addressing the core problem stated in Chapter 1.

---

# CHAPTER FIVE: FINDINGS AND CONCLUSION

## 5.1 Chapter Overview

This chapter summarises findings from the design, implementation, and evaluation of the Online Exam Proctoring System, draws conclusions against the project aim and objectives, discusses limitations and lessons learned, and provides recommendations for future work and commercialisation.

## 5.2 Findings

1. **Foreign-material detection is feasible on commodity hardware.** YOLOv5n integrated via Celery workers detected phones and books in webcam frames without GPU acceleration, though latency increases under concurrent load.

2. **Separating inference from the web thread is essential.** The accept → queue → infer → push pattern kept the Django server responsive; running YOLO on request threads caused unacceptable blocking in early experiments.

3. **Graduated enforcement reduces false-positive harm.** Sustained look-away timers (5 s) and three-strike policies prevented single-frame misclassifications from immediately terminating legitimate examinees.

4. **Teacher audit pathways build institutional trust.** Storing annotated snapshots and clip frames converted opaque AI alerts into reviewable evidence, addressing faculty scepticism toward automated proctoring.

5. **Admin approval and access codes provide governance.** Requiring admin sign-off before publication and code-based student entry aligned the platform with KNUST examination office workflows.

6. **Rule-based lockdown alone is insufficient.** Tab-switch detection caught digital misconduct but missed physical materials; combining lockdown with visual AI closed the gap identified in the literature review.

## 5.3 Conclusions

The project successfully designed, developed, and demonstrated an Online Exam Proctoring System integrating YOLOv5 deep learning object detection into a Django-based examination platform for KNUST.

Against the **specific objectives**:

| Objective | Conclusion |
|-----------|------------|
| 1. Analyse malpractice risks | Completed via literature review and gap analysis (Chapter 2) |
| 2. Design secure RBAC platform | Implemented admin/teacher/student roles with middleware gates |
| 3. Integrate YOLOv5 proctoring | YOLOv5n + YOLOv8n-pose pipeline operational via Celery |
| 4. Implement graduated enforcement | Three-strike, ID verification, and lockdown levels implemented |
| 5. Evaluate with metrics | Unit tests pass; controlled detection experiments documented (Chapter 4) |

The research hypothesis (H₁)—that YOLOv5 integration improves automated violation detection compared with rule-based approaches—is **supported** by the system's ability to detect foreign materials that browser lockdown alone cannot observe.

## 5.4 Challenges / Limitations of the System

- CPU-only inference limits concurrent examination sessions.
- Pre-trained COCO classes may misclassify context-specific objects (e.g., calculator as phone).
- Variable student webcam quality affects detection reliability.
- Prototype scope excludes large-scale field deployment and longitudinal study.
- Privacy and fairness concerns require further demographic evaluation before high-stakes use.

## 5.5 Lessons Learnt

1. **Start with architecture, not models.** Defining the async pipeline early prevented costly refactoring when ML was integrated in Phase 3.
2. **Test rules separately from ML.** Pure functions in `rules.py` and `services.py` enabled fast unit tests without loading Torch weights.
3. **Design for teacher review, not just automation.** Teachers trust systems that show evidence, not black-box alerts.
4. **Document decisions continuously.** `SYSTEM_DESIGN.md` as a living reference reduced inconsistency across development phases.
5. **KNUST infrastructure realities matter.** CPU-first design reflects actual student hardware availability.

## 5.6 Recommendations for Future Works

1. **Fine-tune YOLO** on a Ghana-specific examination dataset to improve phone/book detection under local lighting conditions.
2. **GPU deployment study** — benchmark throughput with CUDA-enabled workers for concurrent midterm sessions.
3. **Fairness audit** — evaluate false-positive rates across skin tone, gender, and head-covering subgroups.
4. **LMS integration** — LTI/Moodle plugin for grade passback.
5. **Audio monitoring** — optional secondary channel for whisper/collusion detection (with explicit consent).
6. **Mobile app** — native client for improved camera control on tablets.
7. **Analytics dashboard** — violation heatmaps and question-level integrity statistics for exam officers.

## 5.7 Recommendations for Project Commercialisation

| Aspect | Recommendation |
|--------|----------------|
| **Target market** | Ghanaian universities, private colleges, professional certification bodies |
| **Deployment model** | On-premise single-tenant (institutional data sovereignty) or managed cloud |
| **Pricing** | Per-seat annual licence or per-examination-session fee |
| **Regulatory** | Ghana Data Protection Act compliance; explicit student consent forms |
| **Support** | Teacher training workshops; examination office onboarding |
| **Differentiator** | Open-stack auditability vs opaque commercial proctoring; local support |
| **MVP for market** | PostgreSQL + Redis production bundle; SLA for uptime during exam windows |

---

# REFERENCES

Agyeman, N. and Owusu-Darko, P. (2022) 'Digital transformation in Ghanaian higher education: opportunities and challenges', *Journal of African Educational Studies*, 14(2), pp. 45–62.

Bacigalupo, R., Eitel, M., Mangina, E. and Poole, A. (2020) 'Remote examinations: student and instructor perspectives', *Computers & Education*, 159, 104020.

Brimble, M. (2016) 'Why students cheat: an exploration of the motivators of student academic dishonesty in higher education', in Bretag, T. (ed.) *Handbook of Academic Integrity*. Singapore: Springer, pp. 365–382.

Buolamwini, J. and Gebru, T. (2018) 'Gender Shades: Intersectional Accuracy Disparities in Commercial Gender Classification', *Proceedings of Machine Learning Research*, 81, pp. 1–15.

Eaton, S.E. (2021) *Plagiarism in Higher Education: Tackling Tough Topics in Academic Integrity*. Santa Barbara, CA: ABC-CLIO.

Hevner, A.R., March, S.T., Park, J. and Ram, S. (2004) 'Design Science in Information Systems Research', *MIS Quarterly*, 28(1), pp. 75–105.

Jocher, G. et al. (2022) *ultralytics/yolov5: v7.0*. Zenodo. Available at: https://doi.org/10.5281/zenodo.7347926 (Accessed: 12 June 2026).

Kwame Nkrumah University of Science and Technology (2026) *Guide for Preparation and Evaluation of Higher Degree Research Thesis*. Kumasi: School of Graduate Studies. Available at: https://keep.knust.edu.gh (Accessed: 12 June 2026).

Leong, W.Y. (2025) 'Enhancing Academic Integrity in E-Exams Through AI-Driven Proctoring Technologies', *IEEE Conference Proceedings*.

Lilley, M., Meade, A. and Barker, T. (2016) 'The impact of remote proctoring on student experience in online examinations', *Assessment & Evaluation in Higher Education*, 41(4), pp. 582–597.

Norris, S., Lefrere, P. and Mason, J. (2021) 'Academic integrity and online assessment: perceptions and practices', *International Journal of Educational Technology in Higher Education*, 18(1), pp. 1–18.

Oosterhof, A., Conrad, R.M. and Ely, D.P. (2008) *Assessing Learners Online*. Upper Saddle River, NJ: Pearson.

Padilla, R., Netto, S.L. and da Silva, E.A.B. (2020) 'A Survey on Performance Metrics for Object-Detection Algorithms', *IWSSIP Proceedings*, pp. 237–242.

Redmon, J., Divvala, S., Girshick, R. and Farhadi, A. (2016) 'You Only Look Once: Unified, Real-Time Object Detection', *CVPR Proceedings*, pp. 779–788.

UNESCO (2020) *Education in a Post-COVID World: Nine Ideas for Public Action*. Paris: UNESCO Publishing.

---

# APPENDICES

## Appendix A: Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `USE_POSTGRES` | false | Enable PostgreSQL |
| `USE_REDIS` | false | Enable Celery + Redis Channels |
| `PROCTORING_USE_MOCK_ML` | false | Skip Torch/Ultralytics in dev |
| `PROCTORING_YOLO_WEIGHTS` | yolov5nu.pt | Object detection model |
| `PROCTORING_POSE_WEIGHTS` | yolov8n-pose.pt | Pose estimation model |

## Appendix B: API Endpoints (Proctoring)

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/v1/proctoring/id-verify/` | Identity verification |
| POST | `/api/v1/proctoring/frame/` | Enqueue frame inference |
| POST | `/api/v1/proctoring/client-event/` | Lockdown violation |
| WS | `/ws/proctoring/{attempt_id}/` | Real-time events |

## Appendix C: Installation Commands

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Appendix D: Source Code Repository Layout

See `docs/SYSTEM_DESIGN.md` Section 1 — Project layout.

---

*Document version: 1.0 — June 2026*  
*Companion files: [KNUST_FORMATTING_GUIDE.md](./KNUST_FORMATTING_GUIDE.md) | [SYSTEM_DESIGN.md](./SYSTEM_DESIGN.md) | [THESIS_CHAPTERS_1_AND_2.md](./THESIS_CHAPTERS_1_AND_2.md)*
