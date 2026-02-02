---
name: pdf-to-markdown
description: Convert PDF files to high-fidelity Markdown documents with a fetch score indicating extraction quality. Use when user wants to parse, extract, or convert a PDF to markdown/md format, or when user needs to extract all information (text, tables, images) from a PDF systematically. Produces markdown that mimics the original PDF structure, plus a quality score. Combines local Python extraction with optional LLM enhancement.
---

# PDF to Markdown Extraction

One-shot PDF to Markdown converter with quality scoring. Extracts text, tables, and images while preserving document structure.

## Quick Start

```bash
# Install dependencies
pip install pdfplumber pdf2image pytesseract Pillow pandas anthropic --break-system-packages

# Basic extraction
python scripts/extract_pdf.py input.pdf output.md

# With LLM enhancement (recommended for complex documents)
python scripts/extract_pdf.py input.pdf output.md --llm-enhance --verbose
```

## Workflow

### Step 1: Install Dependencies

```bash
pip install pdfplumber pdf2image pytesseract Pillow pandas --break-system-packages
```

For LLM enhancement (optional but recommended):
```bash
pip install anthropic --break-system-packages
```

For OCR support on scanned PDFs:
```bash
apt-get update && apt-get install -y poppler-utils tesseract-ocr
```

### Step 2: Run Extraction

Copy the PDF to working directory and run:

```bash
python /path/to/skill/scripts/extract_pdf.py input.pdf output.md --llm-enhance -v
```

### Step 3: Review Fetch Score

The output markdown includes an **Extraction Report** at the end with:

| Metric | Description |
|--------|-------------|
| **Overall Score** | 0-100 composite score with letter grade |
| **Text Extraction** | How well text was captured |
| **Structure Preservation** | Tables, images, formatting quality |
| **Completeness** | Missing elements, warnings |

**Score Interpretation:**
- **A (90-100)**: Excellent - minimal manual review needed
- **B (80-89)**: Good - minor formatting touch-ups may help
- **C (70-79)**: Acceptable - some manual correction expected
- **D (60-69)**: Fair - significant manual work likely
- **F (<60)**: Poor - consider alternative extraction methods

## Output Format

The generated markdown mimics PDF structure:

```markdown
<!-- Page 1 -->

## Document Title

Body text preserved with paragraph structure...

| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| Data     | Data     | Data     |

![Image 1.1](image_p1_1.png)

---

<!-- Page 2 -->

### Section Header

More content...

---

## 📊 Extraction Report

| Metric | Value |
|--------|-------|
| **Overall Score** | 85/100 (B - Good) |
| **Text Extraction** | 90/100 |
| **Structure Preservation** | 80/100 |
| **Completeness** | 85/100 |
```

## Features

### Local Python Extraction
- **pdfplumber**: Primary text and table extraction
- **pytesseract**: OCR fallback for scanned pages
- **pdf2image**: Page-to-image conversion for OCR

### LLM Enhancement (--llm-enhance)
- Fixes broken formatting and merged lines
- Improves header hierarchy detection
- Repairs malformed tables
- Adds semantic markdown formatting (bold, italic)
- Preserves all content without summarization

### Fetch Score Calculation
The score evaluates extraction quality across three dimensions:

1. **Text Extraction (40%)**: Pages with extractable text, OCR success rate
2. **Structure Preservation (30%)**: Tables found, images detected, LLM enhancement
3. **Completeness (30%)**: Warnings count, OCR-only penalty

## Command Options

```
python extract_pdf.py <input.pdf> [output.md] [options]

Arguments:
  input_pdf          Path to input PDF file
  output_md          Output markdown path (default: input_name.md)

Options:
  --llm-enhance      Use Claude API to enhance extraction quality
  --verbose, -v      Show detailed progress information
  --score-only       Output only fetch score as JSON (no markdown)
```

## Handling Edge Cases

### Scanned PDFs (Image-only)
The script automatically attempts OCR when no text is extracted. For best results:
```bash
# Ensure OCR tools installed
apt-get install -y poppler-utils tesseract-ocr
```

### Large PDFs
For PDFs >50 pages, process in batches or use without LLM enhancement:
```bash
python extract_pdf.py large.pdf output.md -v  # No --llm-enhance
```

### Complex Layouts
Multi-column layouts may require LLM enhancement for best results:
```bash
python extract_pdf.py complex.pdf output.md --llm-enhance -v
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Low text score | Check if PDF is scanned (needs OCR) |
| Tables not detected | Use --llm-enhance for better table parsing |
| Missing images | Images are referenced, not embedded in MD |
| OCR fails | Install tesseract-ocr and poppler-utils |
| LLM errors | Check ANTHROPIC_API_KEY environment variable |

## Integration Example

```python
from pathlib import Path
import subprocess
import json

def extract_pdf_to_md(pdf_path: str, enhance: bool = True) -> tuple[str, dict]:
    """Extract PDF and return (markdown_content, fetch_score)."""
    output_path = Path(pdf_path).with_suffix('.md')
    
    cmd = ['python', 'scripts/extract_pdf.py', pdf_path, str(output_path)]
    if enhance:
        cmd.append('--llm-enhance')
    
    subprocess.run(cmd, check=True)
    
    # Get score separately
    score_result = subprocess.run(
        ['python', 'scripts/extract_pdf.py', pdf_path, '--score-only'],
        capture_output=True, text=True
    )
    score = json.loads(score_result.stdout)
    
    return output_path.read_text(), score
```
