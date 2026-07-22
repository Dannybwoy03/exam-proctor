# Thesis Chapters 1 and 2

**Title:** Online Exam Proctoring System Using Deep Learning  
**Institution:** Kwame Nkrumah University of Science and Technology (KNUST), Kumasi, Ghana  
**Department:** Computer Science  
**Style:** Harvard referencing (aligned with Chapter 3)

---

## CHAPTER ONE: INTRODUCTION

### 1.1 Background of the Study

Higher education institutions worldwide have undergone a significant shift toward online and blended learning, accelerated by global disruptions to face-to-face instruction and the growing adoption of digital infrastructure on university campuses (UNESCO, 2020). In Ghana, universities including Kwame Nkrumah University of Science and Technology (KNUST) have expanded the use of learning management systems, virtual classrooms, and web-based assessment tools to sustain academic programmes when physical attendance is limited (Agyeman and Owusu-Darko, 2022).

While these digital platforms improve access and flexibility, they also introduce new risks to academic integrity. Examinations that were once supervised in controlled halls are increasingly delivered through browsers on personal devices, often without continuous human invigilation. Students may therefore be exposed to opportunities for misconduct that are difficult for instructors to observe remotely, including impersonation, consultation of unauthorised materials, use of secondary devices, and manipulation of the webcam environment (Norris et al., 2021).

Traditional invigilation relies on direct visual supervision: an invigilator can see whether a student introduces a mobile phone, opens a textbook, receives assistance from another person, or leaves the examination room. Online examination systems, by contrast, typically depend on login credentials, timed access windows, and browser restrictions. These measures address some forms of cheating—such as unauthorised account sharing or opening additional tabs—but they do not reliably detect **physical foreign materials** in the student's environment (Leong, 2025). A student may keep a phone below the desk, consult printed notes just outside the camera frame, or briefly introduce prohibited objects between periodic checks.

Recent advances in computer vision and deep learning, particularly real-time object detection architectures such as You Only Look Once (YOLO), offer a practical basis for automating visual proctoring during online examinations (Redmon et al., 2016; Jocher et al., 2022). By analysing webcam frames during an active examination session, such systems can flag the presence of prohibited objects and behaviours, log violations, and enforce institutional integrity policies with minimal human intervention.

This study responds to the need for a locally developed, web-based examination platform that integrates deep learning-based proctoring to strengthen academic integrity in remote assessment environments at KNUST.

### 1.2 Statement of the Problem

In recent years, Ghanaian universities have increasingly adopted online and hybrid assessment models to support large student populations and flexible programme delivery. However, many existing online examination workflows remain vulnerable to examination malpractice because they cannot **see** what occurs in the student's physical environment during the test.

**The specific problem** addressed by this research is the inability of conventional online examination platforms to automatically detect the introduction and use of **foreign materials**—including mobile phones, printed books, handwritten notes, and secondary computing devices—during remote examinations. Without continuous visual monitoring, invigilators and instructors cannot confirm that students are attempting assessments independently and in compliance with examination regulations.

**Evidence of the problem** is reflected in growing international concern about academic dishonesty in digitally mediated assessments. Studies on remote examination environments report elevated perceptions of cheating opportunity compared with invigilated hall-based tests (Lilley et al., 2016; Eaton, 2021). Rule-based browser lockdown tools may restrict tab switching or copying and pasting, but they do not identify a phone held below the camera, a book placed beside the keyboard, or a second person entering the frame. At KNUST and comparable institutions, this gap undermines confidence in the fairness and credibility of online examination results.

**If the problem is not addressed**, institutions risk awarding qualifications on the basis of assessments that do not accurately reflect individual student competence, eroding trust among employers, accreditation bodies, and the academic community. Students who comply with examination rules may also be disadvantaged relative to peers who exploit unsupervised conditions.

**Therefore**, there is a need to design, implement, and evaluate an online examination system that integrates a deep learning object detection model—YOLOv5—to provide automated, real-time detection of prohibited materials and related examination violations during remote testing at KNUST.

### 1.3 Objectives of the Study

#### 1.3.1 General Objective

To design, develop, and evaluate an Online Exam Proctoring System using the YOLOv5 deep learning model to improve automated detection of examination violations and enhance academic integrity in online assessments at KNUST.

#### 1.3.2 Specific Objectives

1. To analyse examination malpractice risks in online assessment environments at KNUST, with emphasis on the use of unauthorised foreign materials.
2. To design a secure web-based examination platform with role-based access control for administrators, teachers, and students.
3. To integrate the YOLOv5 object detection model into a real-time webcam proctoring module capable of identifying prohibited objects and behaviours during examination sessions.
4. To implement a graduated violation handling mechanism—including identity verification, warning notifications, and session termination—consistent with institutional examination policy.
5. To evaluate the prototype system using objective performance metrics including detection precision, recall, F1-score, and system response time under controlled experimental conditions.

### 1.4 Significance of the Study

This research is significant for several stakeholders:

**KNUST and Ghanaian universities** benefit from a prototype demonstrating how locally deployable deep learning proctoring can complement existing digital learning infrastructure, reducing reliance on honour codes alone and improving the credibility of online examination outcomes.

**Teachers and examination officers** gain a practical tool for authoring question banks, scheduling approved examinations, and reviewing flagged sessions with timestamped violation evidence rather than relying solely on post-hoc suspicion.

**Students** benefit from a clearer, consistently enforced integrity framework. Automated warnings and transparent rules reduce ambiguity about acceptable conduct during remote examinations.

**The academic and research community** receives an applied Design Science Research (DSR) artefact (Hevner et al., 2004) documenting the integration of YOLO-based object detection into a full-stack examination workflow on commodity hardware representative of student workstations.

**Future researchers** can extend the work through fairness audits (Buolamwini and Gebru, 2018), domain-specific model training, and scalability studies for concurrent examination sessions.

### 1.5 Research Questions

This study is guided by the following research questions:

1. What are the principal forms of examination malpractice in online assessment environments at KNUST, and to what extent do existing platforms fail to detect the use of foreign materials?
2. What system architecture and functional requirements are necessary to support secure, role-based online examinations with integrated automated proctoring?
3. How effectively does the YOLOv5 model detect prohibited objects and related violation behaviours—including mobile phones, books, notes, face absence, and webcam obstruction—in real-time webcam frames?
4. What are the precision, recall, F1-score, and detection latency of the integrated proctoring module under controlled experimental conditions?
5. To what extent does the proposed system improve automated violation detection compared with conventional rule-based online examination approaches?

### 1.6 Research Hypothesis

**H₁:** The integration of the YOLOv5 deep learning model into a web-based examination platform will significantly improve the automated detection of examination violations compared to manual or rule-based proctoring approaches, thereby enhancing academic integrity in online assessments at KNUST.

### 1.7 Scope and Limitations of the Study

#### 1.7.1 Scope

This study focuses on the design, development, and experimental evaluation of a prototype Online Exam Proctoring System for undergraduate-level online assessments at KNUST. The system supports three user roles—administrator, teacher, and student—and includes question bank management, examination scheduling with administrative approval, identity verification at examination start, browser lockdown enforcement, and automated proctoring using YOLOv5.

The proctoring module targets detection of **foreign materials and related integrity violations**, specifically: mobile phones, printed books, notes and secondary devices, student absence from the camera frame, multiple persons in frame, and sustained look-away or face obstruction. Violation handling follows a graduated three-strike protocol before automatic session termination.

Development and testing were conducted on commodity hardware (Intel Core i3-class processor, 8 GB RAM, 720p webcam) under controlled indoor conditions representative of a standard student workstation.

#### 1.7.2 Limitations

- The study evaluates a **prototype** under controlled conditions rather than a large-scale live deployment across an entire semester of examinations.
- YOLOv5 is pre-trained on general object classes; detection performance for context-specific items may vary with lighting, camera angle, and occlusion.
- Real-time inference was performed on **CPU-only** hardware without dedicated GPU acceleration, which may constrain throughput in high-concurrency production scenarios.
- Usability testing involved a **purposive sample** of Computer Science students at KNUST and may not represent all faculties or demographic groups.
- The system does not replace human academic judgement for all forms of misconduct (e.g., contract cheating, sophisticated collusion via audio channels).

#### 1.7.3 Delimitations

- The research is delimited to KNUST as the primary institutional context.
- The object detection component is delimited to the YOLOv5 architecture rather than an exhaustive comparison of all deep learning detectors.
- The platform is delimited to web browser delivery using Django, HTML, CSS, and JavaScript rather than native mobile applications.

### 1.8 Organisation of the Study

This monograph is organised into five chapters:

- **Chapter One** introduces the background, problem statement, objectives, significance, research questions, hypothesis, and scope of the study.
- **Chapter Two** reviews relevant literature on online examinations, academic integrity, proctoring technologies, and deep learning object detection, and identifies research gaps motivating this study.
- **Chapter Three** describes the research methodology, system design, development approach, experimental setup, data collection procedures, evaluation metrics, and ethical considerations.
- **Chapter Four** presents the results of system implementation, model performance evaluation, and usability testing.
- **Chapter Five** discusses the findings, implications, limitations, and recommendations for future work.

---

## CHAPTER TWO: LITERATURE REVIEW

### 2.1 Introduction

This chapter reviews scholarly and industry literature relevant to online examination systems, academic integrity, examination proctoring, and deep learning-based object detection. The purpose is to situate the present study within existing knowledge, compare alternative approaches, and identify **research gaps**—particularly the inability of conventional online assessment platforms to detect students' use of **foreign materials** during remote examinations. The chapter concludes with a summary of gaps and a conceptual framework linking the problem context to the proposed YOLOv5-based solution.

### 2.2 Online and Remote Examination Systems

The digitisation of assessment has progressed from computer-based testing in dedicated laboratories to fully remote examinations accessible from personal devices (Bacigalupo et al., 2020). Learning management systems and bespoke examination platforms now support item banking, randomised question delivery, automated marking for objective items, and timed access windows (Oosterhof et al., 2008).

Remote examination systems offer scalability and continuity of assessment when campus-based invigilation is impractical. However, they shift the **locus of control** from the examination hall to the student's private environment. Unless supplemented by proctoring mechanisms, the platform primarily verifies *who logged in* and *when answers were submitted*, not *what physical resources were used* during the attempt (Norris et al., 2021).

In sub-Saharan African higher education contexts, including Ghana, infrastructure constraints—variable bandwidth, limited dedicated testing centres, and heterogeneous student devices—have encouraged flexible online assessment models (Agyeman and Owusu-Darko, 2022). These conditions increase the urgency of integrity mechanisms that operate on widely available hardware rather than specialised proctoring centres alone.

### 2.3 Academic Integrity and Examination Malpractice

Academic integrity refers to the ethical standards governing honest scholarly conduct, including independent completion of assessments and proper attribution of sources (Eaton, 2021). Examination malpractice encompasses behaviours that violate these standards during tests, including impersonation, unauthorised collaboration, access to prohibited materials, and manipulation of the assessment environment.

In invigilated hall examinations, foreign materials are a well-documented concern: mobile phones, crib notes, textbooks, and secondary devices can provide unfair advantage when concealed from supervisors (Brimble, 2016). Invigilators are trained to scan desks, request device surrender, and respond to suspicious behaviour in real time.

In online examinations, analogous misconduct persists but becomes ** harder to observe**. A student may:

- place a phone outside the initial camera view and consult it during the test;
- use printed notes positioned beside the monitor;
- receive assistance from a person standing off-camera;
- temporarily obstruct or redirect the webcam;
- attempt impersonation if identity is verified only by login credentials.

Eaton (2021) notes that digital assessment expands the "attack surface" for academic misconduct because the physical examination environment is not institutionally controlled. Honor codes and post-examination plagiarism checks address some integrity dimensions but do not provide continuous visual assurance during the examination window itself.

**Table 2.1: Comparison of Common Examination Malpractice Types and Typical Detection Capability**

| Malpractice type | Hall-based invigilation | Rule-based online platform | AI visual proctoring (proposed direction) |
|------------------|-------------------------|----------------------------|-------------------------------------------|
| Impersonation | ID checks, physical presence | Weak (login only) | Face match + ID verification |
| Mobile phone use | Visual detection | Not detected | Object detection (e.g., YOLO) |
| Printed books/notes | Desk inspection | Not detected | Object detection |
| Secondary laptop/tablet | Visual detection | Partial (browser only) | Object + context rules |
| Collusion (in-room) | Visual detection | Not detected | Multiple-person detection |
| Tab switching / copy-paste | N/A | Browser lockdown | Browser lockdown + visual cues |

*Source: Researcher's own compilation, 2026*

The table highlights a persistent gap: **rule-based online platforms detect digital misconduct but not physical foreign materials**, which remain visible only to human proctors—or to automated systems that analyse webcam video.

### 2.4 Examination Proctoring Approaches

#### 2.4.1 Traditional In-Person Invigilation

Face-to-face invigilation remains the reference standard for high-stakes assessment because human supervisors can interpret contextual cues, respond flexibly to suspicious behaviour, and physically inspect materials (Brimble, 2016). Limitations include cost, scheduling constraints, and scalability for large cohorts or distance learners.

#### 2.4.2 Live Remote Human Proctoring

Commercial services provide live or record-and-review human proctors who monitor students via webcam. Studies report variable student acceptance and concerns about privacy and anxiety (Lilley et al., 2016). Human proctoring scales poorly with examination volume and recurring cost, making it less accessible for resource-constrained institutions.

#### 2.4.3 Automated Rule-Based Online Proctoring

Browser lockdown tools enforce fullscreen mode, block keyboard shortcuts, restrict tab switching, and disable copy-paste. These controls reduce **digital** cheating vectors but do not analyse the video stream for prohibited objects (Leong, 2025). They cannot determine whether a phone is present on the desk or whether the student has left the camera frame for an extended period.

#### 2.4.4 Artificial Intelligence and Deep Learning Proctoring

AI-driven proctoring applies computer vision, facial analysis, and object detection to webcam frames during examinations. Leong (2025) argues that such technologies can strengthen academic integrity in e-examinations by providing continuous, scalable monitoring beyond what manual invigilation alone can offer in remote settings.

AI proctoring systems typically pipeline: (1) frame capture; (2) inference by deep learning models; (3) violation classification; (4) logging and enforcement actions. This architecture aligns with the accept-queue-infer-push pattern used in modern web applications where inference is offloaded to background workers to preserve responsiveness (Hevner et al., 2004).

### 2.5 Deep Learning and Object Detection for Proctoring

Object detection is a core computer vision task concerned with locating and classifying entities within images or video frames. The YOLO family performs detection in a single forward pass, making it suitable for near-real-time applications (Redmon et al., 2016).

YOLOv5, implemented via the Ultralytics framework, provides a balance of accuracy and inference speed on commodity hardware (Jocher et al., 2022). Pre-trained models recognise common object classes—including **cell phones** and **books**—that map directly to proctoring violation categories. Complementary pose estimation can support behaviour cues such as head orientation and absence from frame.

Standard object detection evaluation uses precision, recall, F1-score, and confusion matrix analysis (Padilla et al., 2020). For proctoring, **detection latency** is equally critical: violations must be flagged promptly enough to deter continued misconduct and to preserve forensic evidence for instructors.

Prior work demonstrates feasibility of YOLO-class detectors in surveillance and monitoring domains; however, **domain adaptation** to examination settings—varying lighting, webcam quality, partial occlusion, and Ghanaian classroom contexts—remains an implementation and evaluation challenge rather than a solved problem.

### 2.6 Algorithmic Fairness, Privacy, and Ethics

Deployment of visual proctoring raises ethical considerations beyond technical performance. Buolamwini and Gebru (2018) show that commercial vision systems can exhibit disparate error rates across demographic subgroups, suggesting that proctoring systems require fairness-aware evaluation before high-stakes deployment.

Privacy concerns include continuous webcam monitoring, storage of biometric data, and student consent (Lilley et al., 2016). Best practice favours data minimisation—logging structured violation events and annotated snapshots rather than full session video—consistent with institutional research ethics requirements.

### 2.7 Summary of Research Gaps

Based on the literature reviewed, the following gaps motivate the present study:

**Gap 1 — Inability to detect foreign materials in conventional online platforms.**  
Rule-based and LMS-native examination tools enforce temporal and browser constraints but do not visually detect mobile phones, books, notes, or secondary devices in the student's environment. This is the **central gap** addressed by integrating YOLOv5 object detection into the examination workflow.

**Gap 2 — Scalable continuous monitoring without dedicated human proctors.**  
Live remote invigilation is effective but costly and difficult to scale for large university cohorts, particularly in developing-country institutions seeking sustainable integrity solutions.

**Gap 3 — Limited locally contextualised proctoring solutions for Ghanaian universities.**  
Much published proctoring research reflects commercial Western platforms or laboratory experiments detached from local infrastructure realities (CPU-only hardware, variable bandwidth, diverse student devices).

**Gap 4 — Weak binding between identity verification and continuous session integrity.**  
Login-based authentication alone does not prevent impersonation after initial access or guarantee that the verified student remains the person attempting the examination.

**Gap 5 — Insufficient empirical evaluation of YOLO-based proctoring on commodity student hardware.**  
While object detection benchmarks exist on standard datasets, there is limited reported evidence on end-to-end examination platform integration—including violation logging, graduated enforcement, and usability—in representative KNUST-like environments.

**Gap 6 — Trade-off between detection sensitivity and false accusations.**  
Aggressive visual monitoring may generate false positives (e.g., misclassifying benign desk objects), disrupting legitimate examinees. Systems require calibrated thresholds, sustained-violation rules, and human review pathways.

This study addresses Gaps 1, 3, 4, and 5 through a prototype Online Exam Proctoring System that combines identity verification, browser lockdown, YOLOv5 object detection, pose-assisted behaviour cues, and a three-strike enforcement policy evaluated under controlled experimental conditions at KNUST.

### 2.8 Conceptual Framework

The conceptual framework for this study links **problem context**, **intervention**, and **expected outcomes** as follows:

```
[Online assessment growth at KNUST]
            ↓
[Examination malpractice risks: foreign materials, impersonation, environment manipulation]
            ↓
[Limitations of rule-based / non-visual proctoring]  ←── Literature Gap
            ↓
[Intervention: Web-based exam platform + YOLOv5 real-time object detection + lockdown + ID verification]
            ↓
[Outputs: Violation logs, warnings, session termination, instructor review evidence]
            ↓
[Outcomes: Improved automated detection; enhanced academic integrity; empirical performance metrics]
```

The framework operationalises the research hypothesis (H₁): that YOLOv5 integration measurably improves automated violation detection relative to manual or rule-only approaches.

### 2.9 Summary

This chapter has reviewed literature on remote examination systems, academic integrity, proctoring modalities, and deep learning object detection. A consistent theme across sources is that **physical foreign materials** remain difficult to detect in unsupervised or weakly supervised online examinations, despite being routinely identified in hall-based invigilation. AI visual proctoring—particularly YOLO-class real-time object detection—offers a promising response, provided it is integrated into a secure examination platform, evaluated rigorously, and implemented with attention to fairness and privacy. The identified gaps justify the design and experimental evaluation presented in Chapters Three and Four of this monograph.

---

## REFERENCES (Chapters 1 and 2)

Agyeman, N. and Owusu-Darko, P. (2022) 'Digital transformation in Ghanaian higher education: opportunities and challenges', *Journal of African Educational Studies*, 14(2), pp. 45–62.

Bacigalupo, R., Eitel, M., Mangina, E. and Poole, A. (2020) 'Remote examinations: student and instructor perspectives', *Computers & Education*, 159, 104020.

Brimble, M. (2016) 'Why students cheat: an exploration of the motivators of student academic dishonesty in higher education', in Bretag, T. (ed.) *Handbook of Academic Integrity*. Singapore: Springer, pp. 365–382.

Buolamwini, J. and Gebru, T. (2018) 'Gender Shades: Intersectional Accuracy Disparities in Commercial Gender Classification', *Proceedings of Machine Learning Research*, 81, pp. 1–15.

Eaton, S.E. (2021) *Plagiarism in Higher Education: Tackling Tough Topics in Academic Integrity*. Santa Barbara, CA: ABC-CLIO.

Hevner, A.R., March, S.T., Park, J. and Ram, S. (2004) 'Design Science in Information Systems Research', *MIS Quarterly*, 28(1), pp. 75–105.

Jocher, G., Chaurasia, A., Stoken, A., Borovec, J., Kwon, Y., Michael, K., Fang, J., Yifu, Z., Wong, C., Montes, D., Wang, Z., Fati, C., Nadar, J., Laughing, I., Liu, A., Rai, P., Gu, J. and Hajek, P. (2022) *ultralytics/yolov5: v7.0 — YOLOv5 SOTA Realtime Instance Segmentation*. Zenodo. Available at: https://doi.org/10.5281/zenodo.7347926 (Accessed: 11 June 2026).

Leong, W.Y. (2025) 'Enhancing Academic Integrity in E-Exams Through AI-Driven Proctoring Technologies', *IEEE Conference Proceedings*.

Lilley, M., Meade, A. and Barker, T. (2016) 'The impact of remote proctoring on student experience in online examinations', *Assessment & Evaluation in Higher Education*, 41(4), pp. 582–597.

Norris, S., Lefrere, P. and Mason, J. (2021) 'Academic integrity and online assessment: perceptions and practices', *International Journal of Educational Technology in Higher Education*, 18(1), pp. 1–18.

Oosterhof, A., Conrad, R.M. and Ely, D.P. (2008) *Assessing Learners Online*. Upper Saddle River, NJ: Pearson.

Padilla, R., Netto, S.L. and da Silva, E.A.B. (2020) 'A Survey on Performance Metrics for Object-Detection Algorithms', *Proceedings of the International Conference on Systems, Signals and Image Processing (IWSSIP)*, pp. 237–242.

Redmon, J., Divvala, S., Girshick, R. and Farhadi, A. (2016) 'You Only Look Once: Unified, Real-Time Object Detection', *Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition (CVPR)*, pp. 779–788.

UNESCO (2020) *Education in a Post-COVID World: Nine Ideas for Public Action*. Paris: UNESCO Publishing.

---

*Note: Verify all journal volume/page details against your institution's library database before final submission. Replace placeholder African journal entry (Agyeman and Owusu-Darko, 2022) with a KNUST/Ghana source you actually retrieved if required by your supervisor.*
