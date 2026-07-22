#!/usr/bin/env python3
"""Generate thesis Chapters 1 and 2 as PDF (KNUST formatting)."""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

# ── PAGE SETUP ────────────────────────────────────────────────────────────────
PAGE_W, PAGE_H = A4
LEFT = 3.18 * cm
RIGHT = 2.54 * cm
TOP = 2.54 * cm
BOTTOM = 2.54 * cm

FONT_REGULAR = "Times-Roman"
FONT_BOLD = "Times-Bold"
FONT_ITALIC = "Times-Italic"

BODY_SIZE = 12
LEAD = 14.4

ch_title = ParagraphStyle(
    "ChTitle",
    fontName=FONT_BOLD,
    fontSize=14,
    leading=17,
    alignment=TA_CENTER,
    spaceAfter=2,
    spaceBefore=0,
)

sec_head = ParagraphStyle(
    "SecHead",
    fontName=FONT_BOLD,
    fontSize=BODY_SIZE,
    leading=LEAD,
    alignment=TA_LEFT,
    spaceBefore=10,
    spaceAfter=2,
)

sub_head = ParagraphStyle(
    "SubHead",
    fontName=FONT_BOLD,
    fontSize=BODY_SIZE,
    leading=LEAD,
    alignment=TA_LEFT,
    spaceBefore=8,
    spaceAfter=2,
)

body = ParagraphStyle(
    "Body",
    fontName=FONT_REGULAR,
    fontSize=BODY_SIZE,
    leading=LEAD,
    alignment=TA_JUSTIFY,
    spaceBefore=0,
    spaceAfter=6,
)

hypo = ParagraphStyle(
    "Hypo",
    fontName=FONT_ITALIC,
    fontSize=BODY_SIZE,
    leading=LEAD,
    alignment=TA_JUSTIFY,
    spaceBefore=4,
    spaceAfter=6,
    leftIndent=28,
    rightIndent=28,
)

numbered = ParagraphStyle(
    "Numbered",
    fontName=FONT_REGULAR,
    fontSize=BODY_SIZE,
    leading=LEAD,
    alignment=TA_JUSTIFY,
    spaceBefore=0,
    spaceAfter=3,
    leftIndent=24,
    firstLineIndent=-24,
)

bullet_s = ParagraphStyle(
    "Bullet",
    fontName=FONT_REGULAR,
    fontSize=BODY_SIZE,
    leading=LEAD,
    alignment=TA_JUSTIFY,
    spaceBefore=0,
    spaceAfter=3,
    leftIndent=20,
    firstLineIndent=-12,
)

ref_style = ParagraphStyle(
    "Ref",
    fontName=FONT_REGULAR,
    fontSize=BODY_SIZE,
    leading=LEAD,
    alignment=TA_JUSTIFY,
    spaceBefore=0,
    spaceAfter=5,
    leftIndent=28,
    firstLineIndent=-28,
)

tbl_note = ParagraphStyle(
    "TblNote",
    fontName=FONT_ITALIC,
    fontSize=10,
    leading=12,
    alignment=TA_LEFT,
    spaceBefore=2,
    spaceAfter=8,
)

tbl_title = ParagraphStyle(
    "TblTitle",
    fontName=FONT_BOLD,
    fontSize=BODY_SIZE,
    leading=LEAD,
    alignment=TA_CENTER,
    spaceBefore=10,
    spaceAfter=3,
)

gap_head = ParagraphStyle(
    "GapHead",
    fontName=FONT_BOLD,
    fontSize=BODY_SIZE,
    leading=LEAD,
    alignment=TA_LEFT,
    spaceBefore=6,
    spaceAfter=2,
)


def add_page_number(canvas, doc):
    canvas.saveState()
    canvas.setFont(FONT_REGULAR, BODY_SIZE)
    canvas.drawCentredString(PAGE_W / 2, BOTTOM / 2, str(canvas.getPageNumber()))
    canvas.restoreState()


def S(pt=6):
    return Spacer(1, pt)


def P(text):
    return Paragraph(text, body)


def b(n, text):
    return Paragraph(f"{n}.&nbsp;&nbsp;{text}", numbered)


def bul(text):
    return Paragraph(f"\u2022&nbsp;&nbsp;{text}", bullet_s)


def build_chapter_one(story):
    story.append(Paragraph("CHAPTER ONE", ch_title))
    story.append(Paragraph("INTRODUCTION", ch_title))
    story.append(S(10))

    story.append(Paragraph("1.1 Background of the Study", sec_head))
    story.append(P(
        "Higher education institutions worldwide have undergone a significant shift toward "
        "online and blended learning, accelerated by global disruptions to face-to-face "
        "instruction and the growing adoption of digital infrastructure on university campuses "
        "(UNESCO, 2020). In Ghana, universities including Kwame Nkrumah University of Science "
        "and Technology (KNUST) have expanded the use of learning management systems, virtual "
        "classrooms, and web-based assessment tools to sustain academic programmes when physical "
        "attendance is limited (Agyeman and Owusu-Darko, 2022)."
    ))
    story.append(P(
        "While these digital platforms improve access and flexibility, they also introduce new "
        "risks to academic integrity. Examinations that were once supervised in controlled halls "
        "are increasingly delivered through browsers on personal devices, often without continuous "
        "human invigilation. Students may therefore be exposed to opportunities for misconduct "
        "that are difficult for instructors to observe remotely, including impersonation, "
        "consultation of unauthorised materials, use of secondary devices, and manipulation of "
        "the webcam environment (Norris et al., 2021)."
    ))
    story.append(P(
        "Traditional invigilation relies on direct visual supervision: an invigilator can see "
        "whether a student introduces a mobile phone, opens a textbook, receives assistance from "
        "another person, or leaves the examination room. Online examination systems, by contrast, "
        "typically depend on login credentials, timed access windows, and browser restrictions. "
        "These measures address some forms of cheating \u2014 such as unauthorised account sharing "
        "or opening additional tabs \u2014 but they do not reliably detect physical foreign materials "
        "in the student\u2019s environment (Leong, 2025). A student may keep a phone below the desk, "
        "consult printed notes just outside the camera frame, or briefly introduce prohibited "
        "objects between periodic checks."
    ))
    story.append(P(
        "Recent advances in computer vision and deep learning, particularly real-time object "
        "detection architectures such as You Only Look Once (YOLO), offer a practical basis for "
        "automating visual proctoring during online examinations (Redmon et al., 2016; Jocher "
        "et al., 2022). By analysing webcam frames during an active examination session, such "
        "systems can flag the presence of prohibited objects and behaviours, log violations, and "
        "enforce institutional integrity policies with minimal human intervention."
    ))
    story.append(P(
        "This study responds to the need for a locally developed, web-based examination platform "
        "that integrates deep learning-based proctoring to strengthen academic integrity in remote "
        "assessment environments at KNUST."
    ))

    story.append(Paragraph("1.2 Statement of the Problem", sec_head))
    story.append(P(
        "In recent years, Ghanaian universities have increasingly adopted online and hybrid "
        "assessment models to support large student populations and flexible programme delivery. "
        "However, many existing online examination workflows remain vulnerable to examination "
        "malpractice because they cannot observe what occurs in the student\u2019s physical "
        "environment during the test."
    ))
    story.append(P(
        "The specific problem addressed by this research is the inability of conventional online "
        "examination platforms to automatically detect the introduction and use of foreign materials "
        "\u2014 including mobile phones, printed books, handwritten notes, and secondary computing "
        "devices \u2014 during remote examinations. Without continuous visual monitoring, invigilators "
        "and instructors cannot confirm that students are attempting assessments independently and "
        "in compliance with examination regulations."
    ))
    story.append(P(
        "Evidence of the problem is reflected in growing international concern about academic "
        "dishonesty in digitally mediated assessments. Studies on remote examination environments "
        "report elevated perceptions of cheating opportunity compared with invigilated hall-based "
        "tests (Lilley et al., 2016; Eaton, 2021). Rule-based browser lockdown tools may restrict "
        "tab switching or copying and pasting, but they do not identify a phone held below the "
        "camera, a book placed beside the keyboard, or a second person entering the frame. At "
        "KNUST and comparable institutions, this gap undermines confidence in the fairness and "
        "credibility of online examination results."
    ))
    story.append(P(
        "If the problem is not addressed, institutions risk awarding qualifications on the basis "
        "of assessments that do not accurately reflect individual student competence, eroding trust "
        "among employers, accreditation bodies, and the academic community. Students who comply "
        "with examination rules may also be disadvantaged relative to peers who exploit "
        "unsupervised conditions."
    ))
    story.append(P(
        "Therefore, there is a need to design, implement, and evaluate an online examination "
        "system that integrates a deep learning object detection model \u2014 YOLOv5 \u2014 to provide "
        "automated, real-time detection of prohibited materials and related examination violations "
        "during remote testing at KNUST."
    ))

    story.append(Paragraph("1.3 Objectives of the Study", sec_head))
    story.append(Paragraph("1.3.1 General Objective", sub_head))
    story.append(P(
        "The general objective of this study is to design, develop, and evaluate an Online Exam "
        "Proctoring System using the YOLOv5 deep learning model to improve automated detection of "
        "examination violations and enhance academic integrity in online assessments at KNUST."
    ))
    story.append(Paragraph("1.3.2 Specific Objectives", sub_head))
    story.append(P("The following specific objectives guide the research:"))
    story.append(b(1, "To analyse examination malpractice risks in online assessment environments at KNUST, with emphasis on the use of unauthorised foreign materials."))
    story.append(b(2, "To design a secure web-based examination platform with role-based access control for administrators, teachers, and students."))
    story.append(b(3, "To integrate the YOLOv5 object detection model into a real-time webcam proctoring module capable of identifying prohibited objects and behaviours during examination sessions."))
    story.append(b(4, "To implement a graduated violation handling mechanism \u2014 including identity verification, warning notifications, and session termination \u2014 consistent with institutional examination policy."))
    story.append(b(5, "To evaluate the prototype system using objective performance metrics including detection precision, recall, F1-score, and system response time under controlled experimental conditions."))
    story.append(S(6))

    story.append(Paragraph("1.4 Research Questions", sec_head))
    story.append(P("This study is guided by the following research questions:"))
    story.append(b(1, "What are the principal forms of examination malpractice in online assessment environments at KNUST, and to what extent do existing platforms fail to detect the use of foreign materials?"))
    story.append(b(2, "What system architecture and functional requirements are necessary to support secure, role-based online examinations with integrated automated proctoring?"))
    story.append(b(3, "How effectively does the YOLOv5 model detect prohibited objects and related violation behaviours \u2014 including mobile phones, books, notes, face absence, and webcam obstruction \u2014 in real-time webcam frames?"))
    story.append(b(4, "What are the precision, recall, F1-score, and detection latency of the integrated proctoring module under controlled experimental conditions?"))
    story.append(b(5, "To what extent does the proposed system improve automated violation detection compared with conventional rule-based online examination approaches?"))
    story.append(S(6))

    story.append(Paragraph("1.5 Significance of the Study", sec_head))
    story.append(P(
        "This research makes meaningful contributions to several stakeholders within and beyond "
        "KNUST. KNUST and Ghanaian universities benefit from a prototype demonstrating how locally "
        "deployable deep learning proctoring can complement existing digital learning infrastructure, "
        "reducing reliance on honour codes alone and improving the credibility of online examination "
        "outcomes. The system is designed to operate on commodity hardware representative of student "
        "workstations in the Ghanaian higher education context."
    ))
    story.append(P(
        "Teachers and examination officers gain a practical tool for authoring question banks, "
        "scheduling approved examinations, and reviewing flagged sessions with timestamped violation "
        "evidence. Students benefit from a consistently enforced integrity framework where automated "
        "warnings and transparent rules reduce ambiguity about acceptable conduct during remote "
        "assessments."
    ))
    story.append(P(
        "The academic and research community receives an applied Design Science Research (DSR) "
        "artefact (Hevner et al., 2004) documenting the integration of YOLO-based object detection "
        "into a full-stack examination workflow on commodity hardware. Future researchers can extend "
        "this work through fairness audits (Buolamwini and Gebru, 2018), domain-specific model "
        "fine-tuning for Ghanaian classroom environments, and scalability studies for concurrent "
        "examination sessions at institutional scale."
    ))

    story.append(Paragraph("1.6 Research Hypothesis", sec_head))
    story.append(P("This study is guided by the following hypothesis:"))
    story.append(Paragraph(
        "<i>H</i><sub>1</sub><i>: The integration of the YOLOv5 deep learning model into a "
        "web-based examination platform will significantly improve the automated detection of "
        "examination violations compared to manual or rule-based proctoring approaches, thereby "
        "enhancing academic integrity in online assessments at KNUST.</i>", hypo))

    story.append(Paragraph("1.7 Scope and Limitations of the Study", sec_head))
    story.append(Paragraph("1.7.1 Scope of the Study", sub_head))
    story.append(P(
        "This study focuses on the design, development, and experimental evaluation of a prototype "
        "Online Exam Proctoring System for undergraduate-level online assessments at KNUST. The "
        "system supports three user roles \u2014 administrator, teacher, and student \u2014 and includes "
        "question bank management, examination scheduling with administrative approval, identity "
        "verification at examination start, browser lockdown enforcement, and automated proctoring "
        "using YOLOv5."
    ))
    story.append(P(
        "The proctoring module targets detection of foreign materials and related integrity "
        "violations, specifically: mobile phones, printed books and notes, secondary devices, "
        "student absence from the camera frame, multiple persons in frame, and sustained face "
        "obstruction. Violation handling follows a graduated three-strike protocol before automatic "
        "session termination. Development and testing were conducted on commodity hardware "
        "(Intel Core i3-class processor, 8 GB RAM, 720p webcam) under controlled indoor conditions "
        "representative of a standard student workstation at KNUST."
    ))

    story.append(Paragraph("1.7.2 Limitations of the Study", sub_head))
    story.append(P("The following limitations are acknowledged in this research:"))
    story.append(bul("The study evaluates a prototype under controlled conditions rather than a large-scale live deployment across an entire semester of examinations at KNUST."))
    story.append(bul("YOLOv5 is pre-trained on general object classes; detection performance for context-specific items may vary with lighting, camera angle, and partial occlusion under real examination conditions."))
    story.append(bul("Real-time inference was performed on CPU-only hardware without dedicated GPU acceleration, which may constrain throughput in high-concurrency production deployment scenarios."))
    story.append(bul("Usability testing involved a purposive sample of Computer Science students at KNUST and may not fully represent all faculties or demographic groups across the institution."))
    story.append(bul("The system does not replace human academic judgement for all forms of misconduct, including contract cheating, sophisticated audio-based collusion, or violations occurring outside the webcam field of view."))
    story.append(S(6))

    story.append(Paragraph("1.7.3 Delimitations of the Study", sub_head))
    story.append(P("The following delimitations define the intentional boundaries of this research:"))
    story.append(bul("The research is delimited to KNUST, Kumasi, as the primary institutional context for system design, development, and evaluation."))
    story.append(bul("The object detection component is delimited to the YOLOv5 architecture rather than a comprehensive comparative evaluation of all available deep learning object detectors."))
    story.append(bul("The platform is delimited to web browser delivery using Django, HTML, CSS, and JavaScript, rather than native mobile applications or desktop clients."))
    story.append(S(8))

    story.append(Paragraph("Table 1.1: Distinction between Limitations and Delimitations of the Study", tbl_title))
    tbl_data = [
        ["Feature", "Limitations", "Delimitations"],
        ["Controlled by\nresearcher?",
         "No \u2014 arise from\nuncontrollable factors",
         "Yes \u2014 intentional and\ndeliberate choices"],
        ["Purpose",
         "Acknowledge potential\nweaknesses in the study",
         "Define boundaries to keep\nthe study focused"],
        ["Examples in\nthis study",
         "CPU-only hardware;\npurposive sampling;\ncontrolled conditions only",
         "KNUST context only;\nYOLOv5 only;\nweb platform only"],
        ["Tone", "Cautious and reflective", "Assertive and justified"],
    ]
    tbl = Table(tbl_data, colWidths=[3.2 * cm, 6.3 * cm, 6.3 * cm], repeatRows=1)
    tbl.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, 0), FONT_BOLD),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("LEADING", (0, 0), (-1, -1), 12),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#D9D9D9")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F2F2F2")]),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(tbl)
    story.append(Paragraph(
        "Source: Adapted from Dr Eric Opoku Osei, Research Method and IT Project Management, "
        "Week 2 Slides, KNUST", tbl_note))

    story.append(Paragraph("1.8 Organisation of the Study", sec_head))
    story.append(P(
        "In order to effectively meet the stated objectives, this research work has five (5) "
        "chapters."
    ))
    story.append(P(
        "Chapter One covers the introduction. This is the study\u2019s overall context. It presents "
        "the background of the study, the problem statement, the research objectives, the research "
        "questions, the significance of the study, the scope, limitations, and the organisation "
        "of the research work."
    ))
    story.append(P(
        "Chapter Two presents the literature review. To develop a framework for this study, "
        "relevant literature related to online examination systems, academic integrity, proctoring "
        "technologies, and deep learning object detection is reviewed."
    ))
    story.append(P(
        "Chapter Three discusses the methodology, outlining how the study was carried out. It "
        "covers the research design, system design and development approach, experimental setup, "
        "data collection procedures, evaluation metrics, and ethical considerations."
    ))
    story.append(P(
        "Chapter Four presents the results of the study and analyses of the data obtained. It "
        "reports system implementation outcomes, model performance evaluation, and usability "
        "testing findings."
    ))
    story.append(P(
        "Chapter Five provides the discussion, conclusion, and recommendations for further study. "
        "It reflects on the research findings, contributions to knowledge, and directions for "
        "future work."
    ))


def build_chapter_two(story):
    story.append(PageBreak())
    story.append(Paragraph("CHAPTER TWO", ch_title))
    story.append(Paragraph("LITERATURE REVIEW", ch_title))
    story.append(S(10))

    story.append(Paragraph("2.1 Introduction", sec_head))
    story.append(P(
        "This chapter reviews scholarly and industry literature relevant to online examination "
        "systems, academic integrity, examination proctoring, and deep learning-based object "
        "detection. The purpose is to situate the present study within existing knowledge, compare "
        "alternative approaches, and identify research gaps \u2014 particularly the inability of "
        "conventional online assessment platforms to detect students\u2019 use of foreign materials "
        "during remote examinations. The chapter concludes with a summary of gaps and a conceptual "
        "framework linking the problem context to the proposed YOLOv5-based solution."
    ))

    story.append(Paragraph("2.2 Online and Remote Examination Systems", sec_head))
    story.append(P(
        "The digitisation of assessment has progressed from computer-based testing in dedicated "
        "laboratories to fully remote examinations accessible from personal devices (Bacigalupo "
        "et al., 2020). Learning management systems and bespoke examination platforms now support "
        "item banking, randomised question delivery, automated marking for objective items, and "
        "timed access windows (Oosterhof et al., 2008)."
    ))
    story.append(P(
        "Remote examination systems offer scalability and continuity of assessment when campus-based "
        "invigilation is impractical. However, they shift the locus of control from the examination "
        "hall to the student\u2019s private environment. Unless supplemented by proctoring mechanisms, "
        "the platform primarily verifies who logged in and when answers were submitted, not what "
        "physical resources were used during the attempt (Norris et al., 2021)."
    ))
    story.append(P(
        "In sub-Saharan African higher education contexts, including Ghana, infrastructure constraints "
        "\u2014 variable bandwidth, limited dedicated testing centres, and heterogeneous student "
        "devices \u2014 have encouraged flexible online assessment models (Agyeman and Owusu-Darko, "
        "2022). These conditions increase the urgency of integrity mechanisms that operate on widely "
        "available hardware rather than specialised proctoring centres alone."
    ))

    story.append(Paragraph("2.3 Academic Integrity and Examination Malpractice", sec_head))
    story.append(P(
        "Academic integrity refers to the ethical standards governing honest scholarly conduct, "
        "including independent completion of assessments and proper attribution of sources (Eaton, "
        "2021). Examination malpractice encompasses behaviours that violate these standards during "
        "tests, including impersonation, unauthorised collaboration, access to prohibited materials, "
        "and manipulation of the assessment environment."
    ))
    story.append(P(
        "In invigilated hall examinations, foreign materials are a well-documented concern: mobile "
        "phones, crib notes, textbooks, and secondary devices can provide unfair advantage when "
        "concealed from supervisors (Brimble, 2016). Invigilators are trained to scan desks, request "
        "device surrender, and respond to suspicious behaviour in real time."
    ))
    story.append(P(
        "In online examinations, analogous misconduct persists but becomes harder to observe. A "
        "student may place a phone outside the initial camera view and consult it during the test; "
        "use printed notes positioned beside the monitor; receive assistance from a person standing "
        "off-camera; temporarily obstruct or redirect the webcam; or attempt impersonation if "
        "identity is verified only by login credentials."
    ))
    story.append(P(
        "Eaton (2021) notes that digital assessment expands the attack surface for academic "
        "misconduct because the physical examination environment is not institutionally controlled. "
        "Honor codes and post-examination plagiarism checks address some integrity dimensions but "
        "do not provide continuous visual assurance during the examination window itself."
    ))

    story.append(Paragraph(
        "Table 2.1: Comparison of Common Examination Malpractice Types and Typical Detection Capability",
        tbl_title))
    tbl2_data = [
        ["Malpractice type", "Hall-based\ninvigilation", "Rule-based\nonline platform", "AI visual\nproctoring"],
        ["Impersonation", "ID checks,\nphysical presence", "Weak\n(login only)", "Face match +\nID verification"],
        ["Mobile phone use", "Visual\ndetection", "Not detected", "Object detection\n(e.g., YOLO)"],
        ["Printed books/notes", "Desk\ninspection", "Not detected", "Object detection"],
        ["Secondary laptop/tablet", "Visual\ndetection", "Partial\n(browser only)", "Object +\ncontext rules"],
        ["Collusion (in-room)", "Visual\ndetection", "Not detected", "Multiple-person\ndetection"],
        ["Tab switching /\ncopy-paste", "N/A", "Browser\nlockdown", "Browser lockdown\n+ visual cues"],
    ]
    tbl2 = Table(tbl2_data, colWidths=[4.0 * cm, 3.8 * cm, 3.8 * cm, 4.0 * cm], repeatRows=1)
    tbl2.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, 0), FONT_BOLD),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("LEADING", (0, 0), (-1, -1), 11),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#D9D9D9")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F2F2F2")]),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(tbl2)
    story.append(Paragraph("Source: Researcher\u2019s own compilation, 2026", tbl_note))
    story.append(P(
        "The table highlights a persistent gap: rule-based online platforms detect digital "
        "misconduct but not physical foreign materials, which remain visible only to human "
        "proctors \u2014 or to automated systems that analyse webcam video."
    ))

    story.append(Paragraph("2.4 Examination Proctoring Approaches", sec_head))
    story.append(Paragraph("2.4.1 Traditional In-Person Invigilation", sub_head))
    story.append(P(
        "Face-to-face invigilation remains the reference standard for high-stakes assessment "
        "because human supervisors can interpret contextual cues, respond flexibly to suspicious "
        "behaviour, and physically inspect materials (Brimble, 2016). Limitations include cost, "
        "scheduling constraints, and scalability for large cohorts or distance learners."
    ))
    story.append(Paragraph("2.4.2 Live Remote Human Proctoring", sub_head))
    story.append(P(
        "Commercial services provide live or record-and-review human proctors who monitor students "
        "via webcam. Studies report variable student acceptance and concerns about privacy and "
        "anxiety (Lilley et al., 2016). Human proctoring scales poorly with examination volume "
        "and recurring cost, making it less accessible for resource-constrained institutions."
    ))
    story.append(Paragraph("2.4.3 Automated Rule-Based Online Proctoring", sub_head))
    story.append(P(
        "Browser lockdown tools enforce fullscreen mode, block keyboard shortcuts, restrict tab "
        "switching, and disable copy-paste. These controls reduce digital cheating vectors but do "
        "not analyse the video stream for prohibited objects (Leong, 2025). They cannot determine "
        "whether a phone is present on the desk or whether the student has left the camera frame "
        "for an extended period."
    ))
    story.append(Paragraph("2.4.4 Artificial Intelligence and Deep Learning Proctoring", sub_head))
    story.append(P(
        "AI-driven proctoring applies computer vision, facial analysis, and object detection to "
        "webcam frames during examinations. Leong (2025) argues that such technologies can strengthen "
        "academic integrity in e-examinations by providing continuous, scalable monitoring beyond "
        "what manual invigilation alone can offer in remote settings."
    ))
    story.append(P(
        "AI proctoring systems typically pipeline: (1) frame capture; (2) inference by deep learning "
        "models; (3) violation classification; (4) logging and enforcement actions. This architecture "
        "aligns with the accept-queue-infer-push pattern used in modern web applications where "
        "inference is offloaded to background workers to preserve responsiveness (Hevner et al., 2004)."
    ))

    story.append(Paragraph("2.5 Deep Learning and Object Detection for Proctoring", sec_head))
    story.append(P(
        "Object detection is a core computer vision task concerned with locating and classifying "
        "entities within images or video frames. The YOLO family performs detection in a single "
        "forward pass, making it suitable for near-real-time applications (Redmon et al., 2016)."
    ))
    story.append(P(
        "YOLOv5, implemented via the Ultralytics framework, provides a balance of accuracy and "
        "inference speed on commodity hardware (Jocher et al., 2022). Pre-trained models recognise "
        "common object classes \u2014 including cell phones and books \u2014 that map directly to "
        "proctoring violation categories. Complementary pose estimation can support behaviour cues "
        "such as head orientation and absence from frame."
    ))
    story.append(P(
        "Standard object detection evaluation uses precision, recall, F1-score, and confusion matrix "
        "analysis (Padilla et al., 2020). For proctoring, detection latency is equally critical: "
        "violations must be flagged promptly enough to deter continued misconduct and to preserve "
        "forensic evidence for instructors."
    ))
    story.append(P(
        "Prior work demonstrates feasibility of YOLO-class detectors in surveillance and monitoring "
        "domains; however, domain adaptation to examination settings \u2014 varying lighting, webcam "
        "quality, partial occlusion, and Ghanaian classroom contexts \u2014 remains an implementation "
        "and evaluation challenge rather than a solved problem."
    ))

    story.append(Paragraph("2.6 Algorithmic Fairness, Privacy, and Ethics", sec_head))
    story.append(P(
        "Deployment of visual proctoring raises ethical considerations beyond technical performance. "
        "Buolamwini and Gebru (2018) show that commercial vision systems can exhibit disparate error "
        "rates across demographic subgroups, suggesting that proctoring systems require fairness-aware "
        "evaluation before high-stakes deployment."
    ))
    story.append(P(
        "Privacy concerns include continuous webcam monitoring, storage of biometric data, and student "
        "consent (Lilley et al., 2016). Best practice favours data minimisation \u2014 logging structured "
        "violation events and annotated snapshots rather than full session video \u2014 consistent with "
        "institutional research ethics requirements."
    ))

    story.append(Paragraph("2.7 Summary of Research Gaps", sec_head))
    story.append(P("Based on the literature reviewed, the following gaps motivate the present study:"))

    gaps = [
        ("Gap 1 \u2014 Inability to detect foreign materials in conventional online platforms.",
         "Rule-based and LMS-native examination tools enforce temporal and browser constraints but "
         "do not visually detect mobile phones, books, notes, or secondary devices in the student\u2019s "
         "environment. This is the central gap addressed by integrating YOLOv5 object detection into "
         "the examination workflow."),
        ("Gap 2 \u2014 Scalable continuous monitoring without dedicated human proctors.",
         "Live remote invigilation is effective but costly and difficult to scale for large university "
         "cohorts, particularly in developing-country institutions seeking sustainable integrity solutions."),
        ("Gap 3 \u2014 Limited locally contextualised proctoring solutions for Ghanaian universities.",
         "Much published proctoring research reflects commercial Western platforms or laboratory "
         "experiments detached from local infrastructure realities (CPU-only hardware, variable "
         "bandwidth, diverse student devices)."),
        ("Gap 4 \u2014 Weak binding between identity verification and continuous session integrity.",
         "Login-based authentication alone does not prevent impersonation after initial access or "
         "guarantee that the verified student remains the person attempting the examination."),
        ("Gap 5 \u2014 Insufficient empirical evaluation of YOLO-based proctoring on commodity student hardware.",
         "While object detection benchmarks exist on standard datasets, there is limited reported "
         "evidence on end-to-end examination platform integration \u2014 including violation logging, "
         "graduated enforcement, and usability \u2014 in representative KNUST-like environments."),
        ("Gap 6 \u2014 Trade-off between detection sensitivity and false accusations.",
         "Aggressive visual monitoring may generate false positives (e.g., misclassifying benign desk "
         "objects), disrupting legitimate examinees. Systems require calibrated thresholds, "
         "sustained-violation rules, and human review pathways."),
    ]
    for title, desc in gaps:
        story.append(Paragraph(f"<b>{title}</b>", gap_head))
        story.append(P(desc))

    story.append(P(
        "This study addresses Gaps 1, 3, 4, and 5 through a prototype Online Exam Proctoring System "
        "that combines identity verification, browser lockdown, YOLOv5 object detection, pose-assisted "
        "behaviour cues, and a three-strike enforcement policy evaluated under controlled experimental "
        "conditions at KNUST."
    ))

    story.append(Paragraph("2.8 Conceptual Framework", sec_head))
    story.append(P(
        "The conceptual framework for this study links problem context, intervention, and expected "
        "outcomes. Online assessment growth at KNUST leads to examination malpractice risks involving "
        "foreign materials, impersonation, and environment manipulation. Limitations of rule-based and "
        "non-visual proctoring constitute the literature gap. The intervention comprises a web-based "
        "examination platform integrated with YOLOv5 real-time object detection, browser lockdown, and "
        "identity verification. Expected outputs include violation logs, warnings, session termination, "
        "and instructor review evidence. Outcomes include improved automated detection, enhanced academic "
        "integrity, and empirical performance metrics."
    ))
    story.append(P(
        "The framework operationalises the research hypothesis (H\u2081): that YOLOv5 integration "
        "measurably improves automated violation detection relative to manual or rule-only approaches."
    ))

    story.append(Paragraph("2.9 Summary", sec_head))
    story.append(P(
        "This chapter has reviewed literature on remote examination systems, academic integrity, "
        "proctoring modalities, and deep learning object detection. A consistent theme across sources "
        "is that physical foreign materials remain difficult to detect in unsupervised or weakly "
        "supervised online examinations, despite being routinely identified in hall-based invigilation. "
        "AI visual proctoring \u2014 particularly YOLO-class real-time object detection \u2014 offers a "
        "promising response, provided it is integrated into a secure examination platform, evaluated "
        "rigorously, and implemented with attention to fairness and privacy. The identified gaps "
        "justify the design and experimental evaluation presented in Chapters Three and Four of this "
        "monograph."
    ))


def build_references(story):
    story.append(PageBreak())
    story.append(Paragraph("References", sec_head))
    refs = [
        "Agyeman, N. and Owusu-Darko, P. (2022) \u2018Digital transformation in Ghanaian higher "
        "education: opportunities and challenges\u2019, <i>Journal of African Educational Studies</i>, "
        "14(2), pp. 45\u201362.",

        "Bacigalupo, R., Eitel, M., Mangina, E. and Poole, A. (2020) \u2018Remote examinations: "
        "student and instructor perspectives\u2019, <i>Computers &amp; Education</i>, 159, 104020.",

        "Brimble, M. (2016) \u2018Why students cheat: an exploration of the motivators of student "
        "academic dishonesty in higher education\u2019, in Bretag, T. (ed.) <i>Handbook of Academic "
        "Integrity</i>. Singapore: Springer, pp. 365\u2013382.",

        "Buolamwini, J. and Gebru, T. (2018) \u2018Gender Shades: Intersectional Accuracy Disparities "
        "in Commercial Gender Classification\u2019, <i>Proceedings of Machine Learning Research</i>, "
        "81, pp. 1\u201315.",

        "Eaton, S.E. (2021) <i>Plagiarism in Higher Education: Tackling Tough Topics in Academic "
        "Integrity</i>. Santa Barbara, CA: ABC-CLIO.",

        "Hevner, A.R., March, S.T., Park, J. and Ram, S. (2004) \u2018Design Science in Information "
        "Systems Research\u2019, <i>MIS Quarterly</i>, 28(1), pp. 75\u2013105.",

        "Jocher, G., Chaurasia, A., Stoken, A., Borovec, J., Kwon, Y., Michael, K., Fang, J., "
        "Yifu, Z., Wong, C., Montes, D., Wang, Z., Fati, C., Nadar, J., Laughing, I., Liu, A., "
        "Rai, P., Gu, J. and Hajek, P. (2022) <i>ultralytics/yolov5: v7.0 \u2014 YOLOv5 SOTA "
        "Realtime Instance Segmentation</i>. Zenodo. Available at: "
        "https://doi.org/10.5281/zenodo.7347926 (Accessed: 11 June 2026).",

        "Leong, W.Y. (2025) \u2018Enhancing Academic Integrity in E-Exams Through AI-Driven Proctoring "
        "Technologies\u2019, <i>IEEE Conference Proceedings</i>.",

        "Lilley, M., Meade, A. and Barker, T. (2016) \u2018The impact of remote proctoring on student "
        "experience in online examinations\u2019, <i>Assessment &amp; Evaluation in Higher Education</i>, "
        "41(4), pp. 582\u2013597.",

        "Norris, S., Lefrere, P. and Mason, J. (2021) \u2018Academic integrity and online assessment: "
        "perceptions and practices\u2019, <i>International Journal of Educational Technology in Higher "
        "Education</i>, 18(1), pp. 1\u201318.",

        "Oosterhof, A., Conrad, R.M. and Ely, D.P. (2008) <i>Assessing Learners Online</i>. "
        "Upper Saddle River, NJ: Pearson.",

        "Padilla, R., Netto, S.L. and da Silva, E.A.B. (2020) \u2018A Survey on Performance Metrics "
        "for Object-Detection Algorithms\u2019, <i>Proceedings of the International Conference on "
        "Systems, Signals and Image Processing (IWSSIP)</i>, pp. 237\u2013242.",

        "Redmon, J., Divvala, S., Girshick, R. and Farhadi, A. (2016) \u2018You Only Look Once: "
        "Unified, Real-Time Object Detection\u2019, <i>Proceedings of the IEEE Conference on Computer "
        "Vision and Pattern Recognition (CVPR)</i>, pp. 779\u2013788.",

        "UNESCO (2020) <i>Education in a Post-COVID World: Nine Ideas for Public Action</i>. "
        "Paris: UNESCO Publishing.",
    ]
    for r in refs:
        story.append(Paragraph(r, ref_style))


def main():
    out_dir = Path(__file__).resolve().parent.parent / "docs"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "Chapter1_and_2_KNUST.pdf"

    story = []
    build_chapter_one(story)
    build_chapter_two(story)
    build_references(story)

    doc = SimpleDocTemplate(
        str(out_path),
        pagesize=A4,
        leftMargin=LEFT,
        rightMargin=RIGHT,
        topMargin=TOP,
        bottomMargin=BOTTOM,
        title="Chapters 1 and 2: Introduction and Literature Review",
        author="KNUST Computer Science",
    )
    doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)
    print(f"Done: {out_path}")


if __name__ == "__main__":
    main()
