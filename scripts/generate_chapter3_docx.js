const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  AlignmentType, BorderStyle, WidthType, ShadingType, LevelFormat
} = require('docx');
const fs = require('fs');
const path = require('path');

const OUT_PATH = path.join(__dirname, '..', 'docs', 'Chapter3_KNUST.docx');

// ── Style constants (matching Ch1 & Ch2) ─────────────────────────────────────
const TNR = "Times New Roman";
const BODY_SIZE = 24;   // 12pt
const HEAD_SIZE = 24;   // bold 12pt for section headings
const TITLE_SIZE = 28;  // 14pt bold for chapter title

const border = { style: BorderStyle.SINGLE, size: 4, color: "AAAAAA" };
const borders = { top: border, bottom: border, left: border, right: border };

// ── Helpers ───────────────────────────────────────────────────────────────────
const chapterTitle = text => new Paragraph({
  alignment: AlignmentType.CENTER,
  spacing: { before: 0, after: 120, line: 240 },
  children: [new TextRun({ text, font: TNR, size: TITLE_SIZE, bold: true })]
});

const sectionHeading = text => new Paragraph({
  alignment: AlignmentType.LEFT,
  spacing: { before: 200, after: 0, line: 240 },
  children: [new TextRun({ text, font: TNR, size: HEAD_SIZE, bold: true })]
});

const subHeading = text => new Paragraph({
  alignment: AlignmentType.LEFT,
  spacing: { before: 160, after: 0, line: 240 },
  children: [new TextRun({ text, font: TNR, size: BODY_SIZE, bold: true })]
});

const body = (text, spacingAfter = 240) => new Paragraph({
  alignment: AlignmentType.BOTH,
  spacing: { before: 0, after: spacingAfter, line: 240 },
  children: [new TextRun({ text, font: TNR, size: BODY_SIZE })]
});

const caption = text => new Paragraph({
  alignment: AlignmentType.LEFT,
  spacing: { before: 80, after: 240, line: 240 },
  children: [new TextRun({ text, font: TNR, size: BODY_SIZE, italics: true })]
});

const spacer = () => new Paragraph({
  spacing: { before: 0, after: 120, line: 240 },
  children: [new TextRun({ text: "", font: TNR, size: BODY_SIZE })]
});

const numItem = (num, text) => new Paragraph({
  alignment: AlignmentType.BOTH,
  spacing: { before: 0, after: 120, line: 240 },
  indent: { left: 720, hanging: 360 },
  children: [new TextRun({ text: `${num}.\t${text}`, font: TNR, size: BODY_SIZE })]
});

const figPlaceholder = text => new Paragraph({
  alignment: AlignmentType.LEFT,
  spacing: { before: 80, after: 240, line: 240 },
  children: [new TextRun({ text, font: TNR, size: BODY_SIZE, italics: true })]
});

// ── Table builder ─────────────────────────────────────────────────────────────
function makeTable(headers, rows, colWidths) {
  const totalWidth = colWidths.reduce((a, b) => a + b, 0);

  const makeCell = (text, width, isHeader = false) => new TableCell({
    borders,
    width: { size: width, type: WidthType.DXA },
    shading: { fill: isHeader ? "D5E8F0" : "FFFFFF", type: ShadingType.CLEAR },
    margins: { top: 80, bottom: 80, left: 120, right: 120 },
    children: [new Paragraph({
      spacing: { before: 0, after: 0, line: 240 },
      children: [new TextRun({ text, font: TNR, size: 22, bold: isHeader })]
    })]
  });

  return new Table({
    width: { size: totalWidth, type: WidthType.DXA },
    columnWidths: colWidths,
    rows: [
      new TableRow({ children: headers.map((h, i) => makeCell(h, colWidths[i], true)) }),
      ...rows.map(row => new TableRow({ children: row.map((c, i) => makeCell(c, colWidths[i])) }))
    ]
  });
}

// ── Content ───────────────────────────────────────────────────────────────────
const ch = [];

// Title
ch.push(chapterTitle("CHAPTER THREE"));
ch.push(chapterTitle("METHODOLOGY"));
ch.push(spacer());

// 3.1 Chapter Overview
ch.push(sectionHeading("3.1 Chapter Overview"));
ch.push(body(
  "This chapter describes the research and development methodology used to design and build the Online Exam Proctoring System. It covers requirement specification, stakeholder identification, functional and non-functional requirements, UML diagrams with use case descriptions, security design, software process model selection and justification, logical design artefacts including user interface wireframe descriptions and database design, and a detailed description of how each development tool was applied in the project."
));

// 3.2 Requirement Specification
ch.push(sectionHeading("3.2 Requirement Specification"));

ch.push(subHeading("3.2.1 Stakeholders of the System"));
ch.push(body(
  "The following stakeholders have a direct interest in the Online Exam Proctoring System. Their roles and interests informed the functional and non-functional requirements specified in this chapter."
));
ch.push(body("Table 3.1 presents the identified stakeholders, their roles, and their interests.", 120));
ch.push(makeTable(
  ["Stakeholder", "Role", "Interest"],
  [
    ["System administrator", "Manages users, approves teacher accounts, approves examinations, and oversees the audit trail", "Platform integrity and institutional policy enforcement"],
    ["Teacher / lecturer", "Creates courses, question banks, and examinations; reviews flagged violation sessions; adjudicates strikes", "Fair assessment delivery and access to actionable violation evidence"],
    ["Student", "Registers on the platform, redeems access codes, sits examinations under automated proctoring", "Clear and transparent rules, privacy of webcam data, fair treatment in violation adjudication"],
    ["Examination office", "Provides institutional oversight of examination scheduling and results", "Credible and auditable examination outcomes"],
    ["Developer / researcher", "Designs, builds, and evaluates the system prototype", "Measurable system performance, maintainable and extensible codebase"],
  ],
  [2600, 3200, 3560]
));
ch.push(caption("Table 3.1: System stakeholders, roles, and interests"));

ch.push(subHeading("3.2.2 Requirement Gathering Process"));
ch.push(body(
  "Requirements for the Online Exam Proctoring System were gathered through four complementary activities:"
));
ch.push(numItem("i", "Literature review — academic publications and industry documentation on online examination systems and proctoring capabilities were reviewed in Chapter 2 to establish baseline functional expectations and identify gaps."));
ch.push(numItem("ii", "Analysis of KNUST online assessment workflows — existing examination procedures at KNUST were examined to identify specific gaps in visual monitoring and identity verification that the proposed system must address."));
ch.push(numItem("iii", "System design documentation — requirements were iteratively refined in a system design document (docs/SYSTEM_DESIGN.md) maintained throughout the development process, capturing decisions and rationale as the system evolved."));
ch.push(numItem("iv", "Prototype-driven validation — following the Design Science Research methodology, requirements were further refined through implementation and testing cycles in which observed latency and false-positive trade-offs informed threshold tuning and feature prioritisation."));
ch.push(spacer());

ch.push(subHeading("3.2.3 Functional Requirements"));
ch.push(body(
  "Table 3.2 presents the functional requirements of the Online Exam Proctoring System, organised by identifier, requirement description, and priority."
));
ch.push(makeTable(
  ["ID", "Requirement", "Priority"],
  [
    ["FR-01", "The system shall support registration and login for administrator, teacher, and student roles with role-based access control", "High"],
    ["FR-02", "The administrator shall approve teacher accounts before teachers can access course and examination management tools", "High"],
    ["FR-03", "The teacher shall create question banks and build examinations from bank questions", "High"],
    ["FR-04", "The teacher shall submit examinations for administrator approval before they are published to students", "High"],
    ["FR-05", "The administrator shall approve, reject, freeze, or extend time on submitted or active examinations", "High"],
    ["FR-06", "The teacher shall generate examination access codes for student entry control", "High"],
    ["FR-07", "The student shall redeem a valid access code to unlock and begin an examination session", "High"],
    ["FR-08", "The system shall verify student identity by detecting an ID card in frame and matching the student's face against the registration photograph before examination access is granted", "High"],
    ["FR-09", "The system shall enforce browser lockdown rules per the examination's configured strictness level", "High"],
    ["FR-10", "The system shall capture webcam frames from the student's browser at configurable intervals throughout the examination", "High"],
    ["FR-11", "The system shall detect prohibited objects and behaviours — including mobile phones, books, notes, student absence, and multiple persons — using the YOLOv5 object detection model", "High"],
    ["FR-12", "The system shall apply the configured three-strike rule and automatically terminate the examination session when the strike threshold is reached", "High"],
    ["FR-13", "The system shall push real-time warning and strike notifications to the student browser via WebSocket during the examination", "High"],
    ["FR-14", "The system shall log all violations with timestamped snapshots and store them for teacher review and adjudication", "High"],
    ["FR-15", "The system shall auto-grade multiple-choice and true/false questions on submission and queue short-answer questions for manual teacher review", "Medium"],
    ["FR-16", "The system shall pause the examination timer on WebSocket disconnect and allow a two-minute grace period before recording a disconnection violation", "Medium"],
    ["FR-17", "The student shall be able to dispute or acknowledge strike alert notifications during the examination", "Medium"],
    ["FR-18", "The teacher shall review flagged sessions and adjudicate violations by marking them as confirmed, ignored, or a false alarm", "Medium"],
  ],
  [900, 6720, 1260]
));
ch.push(caption("Table 3.2: Functional requirements"));

// 3.3 UML Diagrams
ch.push(sectionHeading("3.3 UML Diagrams"));

ch.push(subHeading("3.3.1 Use Case Diagram — System Overview (Front-End Models)"));
ch.push(body(
  "Figure 3.1 presents the system-level use case diagram showing the three primary actors — Administrator, Teacher, and Student — and their interactions with the system's front-end use cases. The Administrator manages users and approvals, the Teacher manages course content and examination creation, and the Student takes examinations and undergoes identity verification and AI proctoring."
));
ch.push(figPlaceholder("[Insert Figure 3.1: Use case diagram — system overview showing Admin, Teacher, and Student actors with their respective use cases]"));

ch.push(subHeading("3.3.2 Use Case Diagram — Back-End / Proctoring Models"));
ch.push(body(
  "Figure 3.2 presents the back-end proctoring use case diagram showing the interactions between the Student Browser actor, the Celery Worker actor, and the internal back-end services. The diagram illustrates how a submitted webcam frame is accepted, enqueued, processed through YOLO inference, evaluated against violation rules, and resolved in a recorded strike or snapshot, with a real-time WebSocket event pushed to the student."
));
ch.push(figPlaceholder("[Insert Figure 3.2: Use case diagram — proctoring backend showing frame upload, task enqueue, YOLO inference, violation rule evaluation, strike recording, WebSocket push, and snapshot storage]"));

ch.push(subHeading("3.3.3 Use Case Descriptions"));
ch.push(body(
  "Table 3.3 provides structured use case descriptions for the principal use cases identified in the system overview and proctoring backend diagrams. Each description specifies the actor, a summary of the interaction, the precondition that must be satisfied before the use case begins, and the postcondition that results from its execution."
));
ch.push(makeTable(
  ["Use Case", "Actor", "Description", "Precondition", "Postcondition"],
  [
    ["Take Examination", "Student", "Student answers examination questions within the timed window under automated proctoring and browser lockdown", "Access code redeemed; identity verification passed", "Attempt submitted and graded, or automatically terminated on strike threshold"],
    ["ID Verification", "Student", "Webcam frame is analysed for the presence of the student's ID card and for a face match against the stored registration photograph", "Examination attempt created and identity verification initiated", "Session verification status set to passed or failed; access denied after three failed attempts"],
    ["AI Proctoring", "System", "Submitted webcam frames are analysed for prohibited objects and examination violation behaviours throughout the active session", "Examination in progress; browser lockdown active", "Violations logged with snapshots; strike count updated; WebSocket events pushed to student"],
    ["Approve Examination", "Administrator", "Administrator reviews the submitted examination questions and schedule, then approves or rejects with a written reason", "Examination status is pending administrator review", "Examination status set to approved and published, or rejected with reason communicated to teacher"],
    ["Review Violations", "Teacher", "Teacher inspects flagged session violation logs, timestamped snapshots, and clip frames, then adjudicates each violation", "Violation records have been created and associated with the examination attempt", "Violation review status updated to confirmed, ignored, or false alarm"],
    ["Generate Access Code", "Teacher", "Teacher creates a single-use or multi-use examination access code linked to an approved and published examination", "Examination has been approved and published by the administrator", "Access code available for student redemption to begin the examination"],
  ],
  [1600, 1200, 2600, 1800, 2160]
));
ch.push(caption("Table 3.3: Use case descriptions for principal use cases"));

ch.push(subHeading("3.3.4 Activity Diagram — Examination Lifecycle"));
ch.push(body(
  "Figure 3.3 presents the activity diagram for the full examination lifecycle, from the student redeeming an access code through identity verification, browser lockdown, the iterative frame capture and violation detection loop, and the termination or submission paths."
));
ch.push(figPlaceholder("[Insert Figure 3.3: Activity diagram — examination lifecycle showing access code redemption, identity verification decision, lockdown entry, frame capture loop, violation detection, strike counting, termination condition, student submission, auto-grading, and result publication]"));

ch.push(subHeading("3.3.5 Sequence Diagram — Frame Processing"));
ch.push(body(
  "Figure 3.4 presents the sequence diagram for the webcam frame processing pipeline. The student browser POSTs a frame to the Django REST API, which immediately enqueues a Celery task via Redis and returns an HTTP 202 Accepted response to avoid blocking the examination interface. The Celery worker runs YOLO inference and evaluates the frame against the violation rule engine. If a violation is found, the worker creates a ViolationLog record with a snapshot and pushes a real-time warning or strike event via the WebSocket channel to the student browser, which updates the proctoring heads-up display."
));
ch.push(figPlaceholder("[Insert Figure 3.4: Sequence diagram — frame processing showing Student Browser, Django API, Redis Queue, Celery Worker, Database, and WebSocket participants]"));

ch.push(subHeading("3.3.6 Class Diagram — Core Domain Models"));
ch.push(body(
  "Figure 3.5 presents the class diagram for the core domain models. A User may have an associated TeacherProfile or StudentProfile. Teachers are linked to Courses, which contain QuestionBanks and Exams. Students are linked to ExamAttempts, each of which is monitored by a single ProctoringSession. A ProctoringSession records multiple ViolationLog entries, and each ViolationLog may be associated with a ViolationSnapshot."
));
ch.push(figPlaceholder("[Insert Figure 3.5: Class diagram — core domain models showing User, TeacherProfile, StudentProfile, Course, QuestionBank, Question, Exam, ExamAttempt, ProctoringSession, ViolationLog, ViolationSnapshot, Answer, and Result with their attributes and relationships]"));

// 3.4 Non-Functional Requirements
ch.push(sectionHeading("3.4 Non-Functional Requirements"));
ch.push(body(
  "Table 3.4 presents the non-functional requirements of the system, each with a measurable target and a justification grounded in the operational context of the prototype deployment at KNUST."
));
ch.push(makeTable(
  ["ID", "Requirement", "Target / Measure", "Justification"],
  [
    ["NFR-01", "Frame upload response time", "Less than 200 ms for the enqueue operation", "The student examination interface must not freeze or become unresponsive during the inference processing cycle"],
    ["NFR-02", "ML inference latency", "Less than 3 seconds per frame on CPU hardware", "Timely strike feedback is necessary for the graduated enforcement protocol to function as intended"],
    ["NFR-03", "Availability", "Single-machine uptime for the prototype deployment scope", "The prototype is evaluated under controlled conditions; production deployment would require a load-balanced configuration"],
    ["NFR-04", "Usability", "Role-specific dashboards requiring no formal training to navigate", "Reducing the training burden for teachers and administrators is essential for practical adoption at KNUST"],
    ["NFR-05", "Maintainability", "Modular Django application structure separating accounts, exams, and proctoring", "Clean separation of concerns enables independent modification and testing of each functional domain"],
    ["NFR-06", "Scalability path", "Architecture supports upgrade to Redis, PostgreSQL, and multiple Celery workers without rewriting application logic", "The prototype must be extendable to production scale without requiring a complete system redesign"],
    ["NFR-07", "Privacy", "Store violation snapshots only; no continuous video recording", "Data minimisation principle: only the evidence necessary for adjudication is retained (Lilley et al., 2016)"],
    ["NFR-08", "Portability", "Compatible with Python 3.11+ on Windows, macOS, and Linux", "Development and testing must be possible on the cross-platform student and laboratory hardware available at KNUST"],
  ],
  [900, 2400, 2200, 3860]
));
ch.push(caption("Table 3.4: Non-functional requirements"));

// 3.5 Security Concepts
ch.push(sectionHeading("3.5 Security Concepts"));
ch.push(body(
  "The Online Exam Proctoring System handles sensitive data including student identity documents, facial photographs, and examination question content. The following security measures are implemented to address the principal threat vectors identified during system design."
));
ch.push(makeTable(
  ["Threat", "Mitigation"],
  [
    ["Unauthorised access", "Django session authentication is enforced on all views; role-based decorators restrict access to admin, teacher, and student routes independently"],
    ["Cross-site request forgery (CSRF)", "CSRF tokens are required on all POST forms and AJAX requests throughout the application"],
    ["Brute-force frame spam", "Rate limiting via django-ratelimit enforces a maximum of one frame per configured capture interval per active examination attempt"],
    ["Impersonation during examination", "Identity card detection and face embedding comparison at examination start; profile photograph required at student registration"],
    ["Examination answer leakage", "The correct_answer field of Question model records is never exposed in student-facing attempt templates or API responses"],
    ["Unapproved teacher portal access", "TeacherApprovalMiddleware blocks all course and examination management routes for teacher accounts that have not received administrator approval"],
    ["Unapproved examination publication", "Examination visibility to students is gated on the Exam.approval_status field, preventing access to any examination not explicitly approved by an administrator"],
    ["Violation media exposure", "Snapshot and clip media files are served through an authenticated media serving view with per-prefix role-based access control, preventing direct URL access"],
    ["Session hijacking", "HTTPS is required in production configuration; session cookies are configured with the Secure and HttpOnly flags in production settings"],
  ],
  [2800, 6560]
));
ch.push(caption("Table 3.5: Security threats and mitigations"));

// 3.6 Project Methods
ch.push(sectionHeading("3.6 Project Methods"));

ch.push(subHeading("3.6.1 Software Process Models"));
ch.push(body(
  "Several established software process models were considered for this project. Table 3.6 provides a brief description of each model reviewed."
));
ch.push(makeTable(
  ["Model", "Brief Description"],
  [
    ["Waterfall", "A sequential, plan-driven model in which each phase — requirements, design, implementation, testing, deployment — must be completed before the next begins. Suitable for projects with well-defined, stable requirements but inflexible in response to changing constraints."],
    ["V-Model", "An extension of the Waterfall model that pairs each development phase with a corresponding testing phase on a V-shaped timeline. Emphasises verification and validation but retains the sequential rigidity of Waterfall."],
    ["Agile / Scrum", "An iterative, incremental model that delivers working software in short sprints, typically two to four weeks. Prioritises responsiveness to change, continuous feedback, and collaboration. Appropriate for projects where requirements emerge through development."],
    ["Design Science Research (DSR)", "A research methodology for information systems that centres on the construction and rigorous evaluation of a novel artefact. The DSR cycle consists of three activities: Build the artefact, Evaluate it against defined criteria, and Communicate the findings (Hevner et al., 2004)."],
  ],
  [2200, 7160]
));
ch.push(caption("Table 3.6: Software process models considered"));

ch.push(subHeading("3.6.2 Chosen Model and Justification"));
ch.push(body(
  "Chosen approach: Agile-informed Design Science Research"
));
ch.push(body(
  "The project adopted an Agile-informed Design Science Research methodology. Development was organised into iterative two-week cycles aligned with Agile principles — delivering working software early and responding to feedback — embedded within the DSR artefact evaluation cycle described by Hevner et al. (2004). Each iteration followed three activities: Build, in which a system feature was implemented (for example, the question bank module, followed by the proctoring pipeline); Evaluate, in which the feature was subjected to unit tests, manual demonstration, and performance measurement; and Communicate, in which findings were recorded in the system design documentation and this report."
));
ch.push(body(
  "This approach is justified on two grounds. First, requirements for the AI proctoring component evolved during development as YOLO integration revealed latency and false-positive trade-offs that could not be fully anticipated at the outset. Agile iteration allowed violation confidence thresholds and capture intervals to be tuned through empirical observation without requiring a restart from a fixed waterfall specification. Second, the DSR framing aligns with the academic expectation that this project produces a novel, rigorously evaluated artefact that contributes to knowledge, rather than simply delivering a software product."
));

// 3.7 UI Design
ch.push(sectionHeading("3.7 Project Design Consideration — UI Design"));
ch.push(body(
  "The user interface follows a unified portal layout with role-aware sidebar navigation rendered from a shared template (templates/includes/portal_sidebar.html). The sidebar presents only the navigation items relevant to the authenticated user's role. Three global design rules apply across all screens: no emoji characters are used; Flaticon SVG icons provide visual affordance; and text hierarchy is expressed through bold headings and neutral notice cards rather than colour. HTMX is used for tab navigation within portal sections to avoid full-page reloads."
));
ch.push(body("Table 3.7 describes the wireframe layout and key elements of the principal screens.", 120));
ch.push(makeTable(
  ["Screen", "Layout", "Key Elements"],
  [
    ["Login", "Centred card on neutral background", "Role selection toggle (Student / Teacher / Admin), username and password fields, submit button"],
    ["Teacher dashboard", "Sidebar navigation with main content panel", "Statistics cards showing active courses, pending examinations, and flagged violations; recent question bank list; recent examination list"],
    ["Question Builder", "Three-column editor", "Left column: question outline and bank structure; centre column: question text editor with answer option fields; right column: metadata panel for marks, type, and tags"],
    ["Student examination interface", "Full-width lockdown screen", "Question panel with navigation controls, countdown timer, proctoring heads-up display with webcam indicator and strike counter, real-time warning overlay"],
    ["Flagged sessions (Teacher)", "Data table with slide-out detail drawer", "Student name, examination title, integrity index score, violation type list, timestamped snapshot viewer, adjudication action buttons"],
    ["Admin examination review", "Read-only question list with action bar", "Examination metadata, question preview, approve button, reject button with reason field, freeze toggle, add-time control"],
  ],
  [2400, 2800, 4160]
));
ch.push(caption("Table 3.7: UI wireframe descriptions"));
ch.push(figPlaceholder("[Insert Figure 3.6: Wireframe — student examination interface showing question panel, timer, proctoring HUD, and webcam indicator]"));
ch.push(figPlaceholder("[Insert Figure 3.7: Wireframe — teacher flagged sessions audit showing violation table, snapshot viewer, and adjudication controls]"));

// 3.8 DB Design
ch.push(sectionHeading("3.8 Project Design Consideration — DB Design"));

ch.push(subHeading("3.8.1 Entity-Relationship Diagram"));
ch.push(body(
  "Figure 3.8 presents the entity-relationship diagram for the Online Exam Proctoring System. A User may have an associated TeacherProfile or StudentProfile. A TeacherProfile is linked to one or more Courses. Each Course contains one or more QuestionBanks, and each QuestionBank contains one or more Questions. A Course hosts one or more Exams. An Exam references Questions through the ExamQuestion junction entity. Users are linked to ExamAttempts, each of which is associated with a single Exam and monitored by exactly one ProctoringSession. A ProctoringSession records multiple ViolationLog entries, each of which may be associated with a ViolationSnapshot. An ExamAttempt contains multiple Answer records and produces a single Result."
));
ch.push(figPlaceholder("[Insert Figure 3.8: Entity-relationship diagram showing User, TeacherProfile, StudentProfile, Course, QuestionBank, Question, Exam, ExamQuestion, ExamAttempt, ProctoringSession, ViolationLog, ViolationSnapshot, Answer, and Result entities with their relationships and cardinalities]"));

ch.push(subHeading("3.8.2 Database Schema Summary"));
ch.push(body(
  "The system uses SQLite as the database engine during prototype development and testing, configured as the default Django database at db.sqlite3 in the project root. PostgreSQL is supported for production deployment and is activated by setting the USE_POSTGRES environment variable to true. The schema is defined in Django model files (apps/*/models.py) and applied to the database through Django migrations using the command python manage.py migrate."
));
ch.push(body("Table 3.8 summarises the primary database tables, their application module, and key fields.", 120));
ch.push(makeTable(
  ["App", "Table (Model)", "Key Fields"],
  [
    ["accounts", "User", "role, email, profile_photo"],
    ["accounts", "StudentProfile", "student_id_number, id_proof_image, face_embedding"],
    ["accounts", "TeacherProfile", "approval_status, department"],
    ["courses", "Course", "code, title, teacher_id"],
    ["exams", "QuestionBank", "course_id, title"],
    ["exams", "Question", "text, question_type, options, correct_answer, marks"],
    ["exams", "Exam", "approval_status, strictness_level, is_frozen"],
    ["exams", "ExamAttempt", "status, remaining_seconds, score"],
    ["exams", "Answer", "response, review_status"],
    ["proctoring", "ProctoringSession", "strike_count, id_verification_status"],
    ["proctoring", "ViolationLog", "violation_type, confidence, review_status"],
    ["proctoring", "ViolationSnapshot", "image, bounding_boxes, pose_keypoints"],
  ],
  [2000, 2800, 4560]
));
ch.push(caption("Table 3.8: Primary database tables and key fields"));

// 3.9 Developmental Tools
ch.push(sectionHeading("3.9 Developmental Tools"));
ch.push(body(
  "This section provides a detailed description of how each development tool presented in Chapter 2 was applied within the project methodology. The tools are described in terms of their specific role in the system implementation rather than as general-purpose technologies."
));
ch.push(makeTable(
  ["Tool", "Application in This Project"],
  [
    ["Django", "The project scaffold is organised under config/ with four application modules: accounts, courses, exams, and proctoring. Django's built-in session authentication, role-based middleware, ORM, and admin panel are used throughout without modification to the framework core."],
    ["Django REST Framework", "Provides the JSON API endpoints for webcam frame upload (POST /api/v1/proctoring/frame/) and identity verification submission. Serialisers validate incoming frame data and return structured violation event responses."],
    ["Django Channels", "Powers the WebSocket consumer mounted at ws/proctoring/{attempt_id}/. The consumer receives heartbeat messages from the student browser and broadcasts strike and warning events generated by Celery workers back to the connected client."],
    ["Celery", "Executes two background task types: process_proctor_frame, which runs YOLO inference on a submitted webcam frame and evaluates the violation rule engine; and verify_id_card, which runs identity and face match verification at examination start."],
    ["Redis", "Serves as the Celery message broker and as the Django Channels channel layer when USE_REDIS is set to true in the environment configuration. In development, an in-memory channel layer is used to remove the Redis dependency."],
    ["SQLite", "Used as the local development database with zero configuration. All Django migrations are applied to db.sqlite3 during development and testing cycles. No external database service is required to run the prototype."],
    ["Ultralytics / PyTorch", "YOLOv5n and YOLOv8n-pose model weights are loaded once at Celery worker startup using the Ultralytics API. Inference is executed on CPU using PyTorch, returning bounding box coordinates and confidence scores for each detected object or keypoint set."],
    ["OpenCV / Pillow", "OpenCV decodes incoming JPEG frame bytes and resizes frames to the model input resolution before inference. Pillow is used to encode annotated violation snapshots as JPEG files for storage in the media directory."],
    ["Tesseract (pytesseract)", "Applied during student registration to perform OCR on uploaded identity document images. Extracted text is used to cross-reference the student ID number against the declared registration information."],
    ["Git", "Version control is maintained with feature branches corresponding to each implementation phase: authentication, course management, examination engine, proctoring pipeline, and evaluation tooling."],
    ["django-ratelimit", "Applied as a decorator on the frame upload endpoint to enforce a per-attempt maximum submission rate, preventing runaway frame spam from a malfunctioning client or adversarial requests."],
  ],
  [2400, 6960]
));
ch.push(caption("Table 3.9: Development tools and their application in the project methodology"));

// ── Build doc ─────────────────────────────────────────────────────────────────
const doc = new Document({
  numbering: {
    config: [{
      reference: "bullets",
      levels: [{
        level: 0,
        format: LevelFormat.BULLET,
        text: "\u2022",
        alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 720, hanging: 360 } } }
      }]
    }]
  },
  sections: [{
    properties: {
      page: {
        size: { width: 12240, height: 15840 },
        margin: { top: 1440, right: 1440, bottom: 1440, left: 1800 }
      }
    },
    children: ch
  }]
});

Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync(OUT_PATH, buf);
  console.log(`Done: ${OUT_PATH}`);
}).catch(err => {
  console.error(err);
  process.exit(1);
});
