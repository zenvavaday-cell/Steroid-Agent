---
name: accessibility-format-conversion
description: Converts documents, slides, PDFs, and course materials into accessible formats with proper headings, reading order, alt text, table structure, captions, contrast, and tagged output that meets WCAG 2.2. Use for remediation, publishing, online courses, and public-sector accessibility compliance.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: education
---

# Accessibility Format Conversion

## Overview

Accessible conversion is structural, not cosmetic. A tagged PDF with a broken reading order is less accessible than a clean HTML page. The goal is content that works with a screen reader, keyboard, magnification, and text reflow.

Test with real assistive technology where possible. An automated score is a starting point, not a certificate.

## When to use

- Converting a Word document or slide deck to PDF.
- Remediating a scanned PDF or image-only handout.
- Publishing course materials online.
- Creating an EPUB or accessible HTML version.
- Auditing a document against WCAG 2.2.

## Workflow

### 1. Define the deliverable and standard

Specify:

- Target format: HTML, tagged PDF (PDF/UA), DOCX, EPUB 3, slides.
- Conformance target: WCAG 2.2 AA is the common baseline.
- Audience and assistive technologies.
- Whether the source is born-digital or scanned.

### 2. Audit the source

Check:

- Is there a text layer, or is it an image?
- Are headings real styles or bold text?
- Are lists real lists?
- Are tables data tables with headers, or layout tables?
- Are images informative or decorative?
- Is color the only carrier of meaning?
- Are there captions and transcripts?
- Is the reading order logical?

### 3. Fix structure before conversion

In the source document:

- Apply heading styles in a strict hierarchy (H1, H2, H3; no skipped levels).
- Use built-in list styles.
- Mark table header rows and scope.
- Add alt text to informative images; mark decorative images as decorative.
- Use meaningful link text, not "click here".
- Add captions to video and transcripts to audio.
- Avoid text boxes and floating objects that break reading order.
- Use sufficient contrast (4.5:1 for normal text, 3:1 for large text and UI components).

### 4. Write alt text

| Image type | Treatment |
| --- | --- |
| Informative | Describe the content and purpose in one or two sentences |
| Decorative | Empty alt (`alt=""`) or artifact |
| Functional (button, icon) | Describe the action, not the appearance |
| Complex (chart, diagram) | Short alt plus a long description or data table |
| Text in image | Reproduce the text; avoid images of text |

Do not start with "image of" or "picture of." A screen reader already announces the role.

### 5. Convert

HTML from Markdown:

```bash
pandoc source.md -o source.html --standalone --toc --mathml
```

DOCX to tagged PDF with LibreOffice:

```bash
soffice --headless --convert-to pdf:writer_pdf_Export \
  --outdir out/ source.docx
```

LibreOffice's PDF export can produce tagged output, but verify the result. For high-stakes PDFs, use a tool that supports PDF/UA and check the tag tree.

Scanned PDF:

```bash
ocrmypdf --skip-text --deskew --clean input.pdf output.pdf
```

OCR introduces text but not structure. Add tags, headings, and reading order afterward.

EPUB:

```bash
pandoc source.md -o book.epub --epub-metadata=metadata.xml
epubcheck book.epub
```

### 6. Validate

Automated:

```bash
npx @axe-core/cli "file://$PWD/page.html"
pa11y page.html
epubcheck book.epub
```

PDF structure:

- PAC 2024 or the PDF Accessibility Checker.
- Verify tags, reading order, alt text, table headers, language, and title.

Manual:

- Navigate with the keyboard only.
- Run a screen reader (NVDA, JAWS, VoiceOver) through the document.
- Zoom to 200% and check reflow.
- Check contrast with a color picker.
- Read the alt text in context.

### 7. Deliver

Provide the accessible format plus:

- A statement of known limitations.
- The contact path for accommodation requests.
- The source file so future edits preserve accessibility.
- Captions and transcripts as separate files where useful.

## Gotchas

- A high automated score can coexist with a broken reading order. Test manually.
- PDF tags are often lost when exporting from design tools. Check the tag tree.
- Scanned documents need OCR before anything else; untagged OCR is still hard to navigate.
- Merged table cells confuse screen readers. Simplify the table.
- Color-only status indicators fail for color-blind readers. Add text or icons.
- "Image of..." alt text wastes screen-reader time.
- Decorative images with descriptive alt text add noise.
- Accessibility overlays do not fix underlying markup. Do not rely on them.
- Math needs MathML or LaTeX with an accessible renderer; images of equations are not accessible.
- Captions must be accurate, not auto-generated and unedited.
- WCAG 2.2 adds focus appearance, dragging alternatives, and consistent help. Check the current criteria.
- Dyslexia-friendly formatting (spacing, font) is helpful but not a substitute for WCAG.

## Output contract

```json
{
  "source": "lecture-03.docx",
  "targets": ["out/lecture-03.pdf", "out/lecture-03.html"],
  "standard": "WCAG 2.2 AA",
  "checks": {
    "headings": "pass",
    "reading_order": "pass",
    "alt_text": {"total": 12, "informative": 8, "decorative": 4},
    "tables": "pass",
    "contrast": "pass",
    "captions": "present",
    "language": "en"
  },
  "manual_tests": ["NVDA reading order", "keyboard navigation", "200% zoom"],
  "known_limitations": ["complex org chart has a text summary instead of a data table"],
  "owner": "course-accessibility@example.edu"
}
```

## Checklist

- [ ] Standard and target formats defined.
- [ ] Source audited for structure and text layer.
- [ ] Headings, lists, and tables use real styles.
- [ ] Alt text written by image type.
- [ ] Contrast and color-only meaning checked.
- [ ] Captions and transcripts provided.
- [ ] Conversion preserves tags and reading order.
- [ ] Automated and manual tests passed.
- [ ] Known limitations and contact path published.
- [ ] Accessible source file retained.

## Related skills

- `differentiated-reading-level-adaptation` for plain-language versions.
- `rubric-aligned-essay-grading` for accessible feedback.
- `source-grounded-citation-verification` for accurate alt text and summaries.
