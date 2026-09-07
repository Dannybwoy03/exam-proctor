# KNUST Project Documentation — Formatting Guide

Use this guide when converting `PROJECT_DOCUMENTATION.md` to Word or PDF for submission. Standards are drawn from the **KNUST School of Graduate Studies — Guide for Preparation and Evaluation of Higher Degree Research Thesis** and the **KNUST undergraduate thesis sample (APA-style notes, G.Y. Annum)**.

> **Confirm with your supervisor.** Some Computer Science departments add local requirements (cover page layout, binding, plagiarism report). This guide covers the most commonly cited KNUST rules.

---

## Page setup

| Setting | Value |
|---------|--------|
| Paper size | A4 (21.0 × 29.7 cm) |
| Margins | 2.5 cm on all sides |
| Gutter margin | 4 cm (for binding) |
| Text alignment | Justified |
| Print | Double-sided where required by department |

---

## Font and spacing

| Element | Font | Size | Spacing | Alignment |
|---------|------|------|---------|-----------|
| Body text | Times New Roman | 12 pt | **1.5 line** (SGS thesis) or **double** (undergrad APA sample) | Justified |
| Abstract | Times New Roman | 12 pt | Single | Justified |
| Footnotes | Times New Roman | Smaller than body | Single | — |
| References / bibliography | Times New Roman | 12 pt | Single | Left, hanging indent 0.5 cm |
| Table / figure captions | Times New Roman | 12 pt | Single | Below figure / above table |
| Block quotations (> 40 words) | Times New Roman | 10 pt | Single | Indented 1 cm left and right |

**Paragraphs:** Separate with one blank line. First-line indent 0.5 cm (or no indent if your supervisor prefers block paragraphs with blank-line separation only).

---

## Heading hierarchy

Follow this pattern consistently (undergraduate APA sample):

| Level | Example | Font | Size | Style | Alignment | Numbering |
|-------|---------|------|------|-------|-----------|-----------|
| Chapter | CHAPTER ONE | Times New Roman | 14 pt | **Bold, UPPERCASE** | Centre | Words (“Chapter One”) |
| Major section | 1.1 BACKGROUND OF THE STUDY | 12 pt | **Bold, UPPERCASE** | Left | 1.1, 1.2, … |
| Sub-section | 1.1.1 Problem context | 12 pt | **Bold, Title Case** | Left | 1.1.1, 1.1.2, … |

- One blank line **before** a major section heading.
- No blank line **after** a sub-section heading (body text follows immediately).

---

## Pagination

| Section | Page numbers |
|---------|----------------|
| Title page | No number (counts as page i) |
| Preliminary pages (declaration, abstract, TOC) | Lower-case Roman numerals (ii, iii, iv …), centred at bottom |
| Main body (Chapter 1 onward) | Arabic numerals (1, 2, 3 …), centred at bottom |
| Each new chapter | Starts on a new page |

---

## Figures, tables, and diagrams

1. **Number consecutively** by chapter: Figure 3.1, Table 2.1.
2. **Caption** below figures; above tables.
3. **Reference in text** before the figure appears: “… as shown in Figure 3.2.”
4. **UML / architecture diagrams** — export from Mermaid (in this repo) or draw in draw.io; minimum 300 dpi for print.
5. **Screenshots** — full browser width or cropped UI; caption with role and screen name (e.g. “Figure 4.5: Student examination interface with proctoring HUD”).

---

## Referencing

The project documentation uses **Harvard** author–date style (consistent with `THESIS_CHAPTERS_1_AND_2.md`):

- In-text: `(Author, Year)` or `Author (Year)`
- Reference list: alphabetical by author surname; single-spaced with hanging indent

Verify every citation against your library database before final submission.

---

## Recommended front matter (before Chapter 1)

1. Title page (project title, your name, index number, department, supervisor, KNUST, date)
2. Declaration / originality statement (department template)
3. Abstract (150–300 words; single-spaced)
4. Acknowledgements (optional)
5. Table of contents
6. List of figures
7. List of tables

---

## Export workflow

### Option A — Microsoft Word (recommended)

1. Open `docs/PROJECT_DOCUMENTATION.md` in Word or paste sections.
2. Apply styles: **Heading 1** = chapter, **Heading 2** = section, **Heading 3** = sub-section.
3. Set Normal style to Times New Roman 12 pt, justified, 1.5 spacing.
4. Insert page breaks before each chapter.
5. Generate TOC: References → Table of Contents.
6. Add screenshots where marked `[Insert Figure X.X: …]`.

### Option B — PDF from existing script

```bash
python scripts/generate_thesis_chapters_pdf.py   # Chapters 1–2 PDF only
```

Extend this script or use Word → Save as PDF for the full five-chapter document.

---

## Checklist before submission

- [ ] Times New Roman 12 pt throughout body
- [ ] 1.5 or double spacing on body (match supervisor preference)
- [ ] Margins 2.5 cm; gutter 4 cm
- [ ] All chapters start on new pages
- [ ] Page numbers correct (Roman / Arabic)
- [ ] All figures and tables numbered and listed
- [ ] References complete and single-spaced
- [ ] No placeholder text remaining (`[Insert …]`)
- [ ] Supervisor name and approval page included
