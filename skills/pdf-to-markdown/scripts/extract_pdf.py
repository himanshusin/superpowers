#!/usr/bin/env python3
"""
PDF to Markdown Extractor
Combines local Python extraction with LLM enhancement for high-fidelity PDF to Markdown conversion.

Usage:
    python extract_pdf.py <input.pdf> [output.md] [--llm-enhance] [--verbose]

Dependencies:
    pip install pdfplumber pdf2image pytesseract Pillow pandas --break-system-packages
"""

import argparse
import base64
import io
import json
import os
import re
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class ExtractionMetrics:
    """Track extraction quality metrics for fetch score calculation."""
    total_pages: int = 0
    pages_with_text: int = 0
    pages_with_tables: int = 0
    pages_with_images: int = 0
    tables_extracted: int = 0
    images_extracted: int = 0
    ocr_pages: int = 0
    llm_enhanced: bool = False
    text_confidence: float = 0.0
    structure_confidence: float = 0.0
    warnings: list = field(default_factory=list)
    
    def calculate_fetch_score(self) -> dict:
        """Calculate overall fetch score (0-100) with component breakdown."""
        scores = {}
        
        # Text extraction score (40% weight)
        if self.total_pages > 0:
            text_ratio = self.pages_with_text / self.total_pages
            scores['text_extraction'] = min(100, text_ratio * 100 + self.text_confidence * 20)
        else:
            scores['text_extraction'] = 0
            
        # Structure preservation score (30% weight)
        structure_score = 50  # Base score
        if self.tables_extracted > 0:
            structure_score += 25
        if self.images_extracted > 0:
            structure_score += 15
        if self.llm_enhanced:
            structure_score += 10
        scores['structure_preservation'] = min(100, structure_score + self.structure_confidence * 20)
        
        # Completeness score (30% weight)
        completeness = 100
        if self.ocr_pages > 0 and self.ocr_pages == self.total_pages:
            completeness -= 20  # OCR-only docs have lower confidence
        if len(self.warnings) > 0:
            completeness -= min(30, len(self.warnings) * 5)
        scores['completeness'] = max(0, completeness)
        
        # Overall weighted score
        overall = (
            scores['text_extraction'] * 0.4 +
            scores['structure_preservation'] * 0.3 +
            scores['completeness'] * 0.3
        )
        
        return {
            'overall_score': round(overall, 1),
            'components': {k: round(v, 1) for k, v in scores.items()},
            'grade': self._score_to_grade(overall),
            'total_pages': self.total_pages,
            'tables_found': self.tables_extracted,
            'images_found': self.images_extracted,
            'ocr_required': self.ocr_pages > 0,
            'llm_enhanced': self.llm_enhanced,
            'warnings': self.warnings
        }
    
    @staticmethod
    def _score_to_grade(score: float) -> str:
        if score >= 90: return 'A - Excellent'
        if score >= 80: return 'B - Good'
        if score >= 70: return 'C - Acceptable'
        if score >= 60: return 'D - Fair'
        return 'F - Poor'


class PDFExtractor:
    """Main PDF extraction class with multi-method extraction."""
    
    def __init__(self, pdf_path: str, verbose: bool = False):
        self.pdf_path = Path(pdf_path)
        self.verbose = verbose
        self.metrics = ExtractionMetrics()
        self.extracted_images_dir = None
        
    def log(self, msg: str):
        if self.verbose:
            print(f"[INFO] {msg}", file=sys.stderr)
    
    def extract(self) -> tuple[str, dict]:
        """
        Main extraction pipeline.
        Returns: (markdown_content, fetch_score_dict)
        """
        import pdfplumber
        
        self.log(f"Opening PDF: {self.pdf_path}")
        
        markdown_parts = []
        
        with pdfplumber.open(self.pdf_path) as pdf:
            self.metrics.total_pages = len(pdf.pages)
            self.log(f"Total pages: {self.metrics.total_pages}")
            
            for page_num, page in enumerate(pdf.pages, 1):
                self.log(f"Processing page {page_num}/{self.metrics.total_pages}")
                page_md = self._extract_page(page, page_num)
                if page_md.strip():
                    markdown_parts.append(page_md)
                    
        # Combine all pages
        markdown_content = "\n\n---\n\n".join(markdown_parts)
        
        # Calculate final metrics
        if self.metrics.pages_with_text > 0:
            self.metrics.text_confidence = min(1.0, self.metrics.pages_with_text / self.metrics.total_pages)
        
        fetch_score = self.metrics.calculate_fetch_score()
        
        return markdown_content, fetch_score
    
    def _extract_page(self, page, page_num: int) -> str:
        """Extract content from a single page."""
        parts = []
        
        # Add page header
        parts.append(f"<!-- Page {page_num} -->")
        
        # 1. Extract text
        text = page.extract_text()
        if text and text.strip():
            self.metrics.pages_with_text += 1
            formatted_text = self._format_text(text)
            parts.append(formatted_text)
        else:
            # Try OCR if no text found
            ocr_text = self._try_ocr(page, page_num)
            if ocr_text:
                self.metrics.ocr_pages += 1
                self.metrics.pages_with_text += 1
                parts.append(f"<!-- OCR extracted -->\n{ocr_text}")
            else:
                self.metrics.warnings.append(f"Page {page_num}: No text extracted")
        
        # 2. Extract tables
        tables = page.extract_tables()
        if tables:
            self.metrics.pages_with_tables += 1
            for i, table in enumerate(tables):
                if table and len(table) > 0:
                    self.metrics.tables_extracted += 1
                    table_md = self._table_to_markdown(table)
                    parts.append(f"\n{table_md}\n")
        
        # 3. Extract images
        images = page.images
        if images:
            self.metrics.pages_with_images += 1
            for i, img in enumerate(images):
                self.metrics.images_extracted += 1
                img_ref = f"![Image {page_num}.{i+1}](image_p{page_num}_{i+1}.png)"
                parts.append(f"\n{img_ref}\n")
        
        return "\n\n".join(parts)
    
    def _format_text(self, text: str) -> str:
        """Format extracted text with basic structure detection."""
        lines = text.split('\n')
        formatted_lines = []
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                formatted_lines.append('')
                continue
                
            # Detect potential headers (short lines, possibly all caps or with numbers)
            if len(stripped) < 80 and stripped.isupper():
                formatted_lines.append(f"## {stripped.title()}")
            elif re.match(r'^[\d.]+\s+[A-Z]', stripped):
                # Numbered section headers
                formatted_lines.append(f"### {stripped}")
            elif re.match(r'^[•\-\*]\s+', stripped):
                # Bullet points
                formatted_lines.append(f"- {stripped[2:].strip()}")
            elif re.match(r'^\d+\.\s+', stripped):
                # Numbered lists
                formatted_lines.append(stripped)
            else:
                formatted_lines.append(stripped)
        
        return '\n'.join(formatted_lines)
    
    def _table_to_markdown(self, table: list) -> str:
        """Convert extracted table to markdown format."""
        if not table or len(table) == 0:
            return ""
        
        # Clean table cells
        cleaned_table = []
        for row in table:
            if row:
                cleaned_row = [str(cell).strip() if cell else '' for cell in row]
                cleaned_table.append(cleaned_row)
        
        if not cleaned_table:
            return ""
        
        # Determine column count
        max_cols = max(len(row) for row in cleaned_table)
        
        # Normalize rows
        for row in cleaned_table:
            while len(row) < max_cols:
                row.append('')
        
        md_lines = []
        
        # Header row
        header = cleaned_table[0]
        md_lines.append('| ' + ' | '.join(header) + ' |')
        md_lines.append('| ' + ' | '.join(['---'] * max_cols) + ' |')
        
        # Data rows
        for row in cleaned_table[1:]:
            md_lines.append('| ' + ' | '.join(row) + ' |')
        
        return '\n'.join(md_lines)
    
    def _try_ocr(self, page, page_num: int) -> Optional[str]:
        """Attempt OCR on page if regular extraction fails."""
        try:
            from pdf2image import convert_from_path
            import pytesseract
            
            self.log(f"Attempting OCR on page {page_num}")
            
            # Convert specific page to image
            images = convert_from_path(
                str(self.pdf_path),
                first_page=page_num,
                last_page=page_num,
                dpi=300
            )
            
            if images:
                text = pytesseract.image_to_string(images[0])
                if text and text.strip():
                    return self._format_text(text)
        except ImportError:
            self.metrics.warnings.append(f"Page {page_num}: OCR libraries not available")
        except Exception as e:
            self.metrics.warnings.append(f"Page {page_num}: OCR failed - {str(e)}")
        
        return None


def enhance_with_llm(markdown: str, pdf_path: str, verbose: bool = False) -> str:
    """
    Use Claude API to enhance the extracted markdown.
    Improves structure, fixes formatting issues, and adds semantic understanding.
    """
    try:
        import anthropic
        
        if verbose:
            print("[INFO] Enhancing with LLM...", file=sys.stderr)
        
        client = anthropic.Anthropic()
        
        # Truncate if too long
        max_chars = 100000
        if len(markdown) > max_chars:
            markdown = markdown[:max_chars] + "\n\n<!-- Content truncated for LLM processing -->"
        
        prompt = f"""You are a document formatting expert. I have extracted text from a PDF and need you to improve the markdown formatting while preserving ALL content exactly.

Your tasks:
1. Fix any broken formatting (merged lines, incorrect headers, etc.)
2. Properly format headers based on document hierarchy (use #, ##, ###)
3. Fix table formatting if any tables appear malformed
4. Preserve all original text - do not summarize or remove content
5. Add appropriate markdown formatting (bold, italic) where it seems intended
6. Keep page markers as HTML comments: <!-- Page N -->

Source PDF: {Path(pdf_path).name}

Extracted content:
{markdown}

Return ONLY the improved markdown, no explanations."""

        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=8192,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return message.content[0].text
        
    except ImportError:
        if verbose:
            print("[WARN] anthropic library not available, skipping LLM enhancement", file=sys.stderr)
        return markdown
    except Exception as e:
        if verbose:
            print(f"[WARN] LLM enhancement failed: {e}", file=sys.stderr)
        return markdown


def generate_report(markdown: str, fetch_score: dict, output_path: str) -> str:
    """Generate the final markdown with fetch score report appended."""
    
    score_section = f"""

---

## 📊 Extraction Report

| Metric | Value |
|--------|-------|
| **Overall Score** | {fetch_score['overall_score']}/100 ({fetch_score['grade']}) |
| **Text Extraction** | {fetch_score['components']['text_extraction']}/100 |
| **Structure Preservation** | {fetch_score['components']['structure_preservation']}/100 |
| **Completeness** | {fetch_score['components']['completeness']}/100 |

### Details
- **Total Pages**: {fetch_score['total_pages']}
- **Tables Found**: {fetch_score['tables_found']}
- **Images Found**: {fetch_score['images_found']}
- **OCR Required**: {'Yes' if fetch_score['ocr_required'] else 'No'}
- **LLM Enhanced**: {'Yes' if fetch_score['llm_enhanced'] else 'No'}

"""
    
    if fetch_score['warnings']:
        score_section += "### ⚠️ Warnings\n"
        for warning in fetch_score['warnings']:
            score_section += f"- {warning}\n"
    
    return markdown + score_section


def main():
    parser = argparse.ArgumentParser(
        description='Extract PDF to Markdown with fetch score',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python extract_pdf.py document.pdf
    python extract_pdf.py document.pdf output.md --llm-enhance
    python extract_pdf.py document.pdf --verbose
        """
    )
    parser.add_argument('input_pdf', help='Path to input PDF file')
    parser.add_argument('output_md', nargs='?', help='Output markdown path (default: input_name.md)')
    parser.add_argument('--llm-enhance', action='store_true', help='Use LLM to enhance extraction')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--score-only', action='store_true', help='Output only the fetch score as JSON')
    
    args = parser.parse_args()
    
    # Validate input
    input_path = Path(args.input_pdf)
    if not input_path.exists():
        print(f"Error: File not found: {input_path}", file=sys.stderr)
        sys.exit(1)
    
    # Determine output path
    if args.output_md:
        output_path = Path(args.output_md)
    else:
        output_path = input_path.with_suffix('.md')
    
    # Extract
    extractor = PDFExtractor(str(input_path), verbose=args.verbose)
    markdown, fetch_score = extractor.extract()
    
    # LLM enhancement if requested
    if args.llm_enhance:
        markdown = enhance_with_llm(markdown, str(input_path), args.verbose)
        fetch_score['llm_enhanced'] = True
        # Recalculate with LLM bonus
        extractor.metrics.llm_enhanced = True
        fetch_score = extractor.metrics.calculate_fetch_score()
    
    if args.score_only:
        print(json.dumps(fetch_score, indent=2))
        return
    
    # Generate final output with report
    final_markdown = generate_report(markdown, fetch_score, str(output_path))
    
    # Write output
    output_path.write_text(final_markdown, encoding='utf-8')
    
    if args.verbose:
        print(f"\n[SUCCESS] Output written to: {output_path}", file=sys.stderr)
        print(f"[SCORE] Fetch Score: {fetch_score['overall_score']}/100 ({fetch_score['grade']})", file=sys.stderr)
    else:
        print(f"Output: {output_path}")
        print(f"Fetch Score: {fetch_score['overall_score']}/100 ({fetch_score['grade']})")


if __name__ == '__main__':
    main()
