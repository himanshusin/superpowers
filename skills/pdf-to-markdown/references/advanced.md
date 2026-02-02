# Advanced Extraction Reference

## Custom Extraction Patterns

### Extracting Specific Page Ranges

```python
import pdfplumber

def extract_pages(pdf_path: str, start: int, end: int) -> str:
    """Extract specific page range."""
    with pdfplumber.open(pdf_path) as pdf:
        text_parts = []
        for i, page in enumerate(pdf.pages[start-1:end], start):
            text = page.extract_text()
            if text:
                text_parts.append(f"<!-- Page {i} -->\n{text}")
    return "\n\n---\n\n".join(text_parts)
```

### Handling Multi-Column Layouts

```python
def extract_columns(page, num_columns: int = 2):
    """Extract text from multi-column layout."""
    width = page.width
    col_width = width / num_columns
    
    columns = []
    for i in range(num_columns):
        bbox = (i * col_width, 0, (i + 1) * col_width, page.height)
        cropped = page.within_bbox(bbox)
        text = cropped.extract_text()
        if text:
            columns.append(text)
    
    return "\n\n".join(columns)
```

### Enhanced Table Extraction

```python
import pandas as pd

def extract_tables_to_dataframes(pdf_path: str) -> list[pd.DataFrame]:
    """Extract all tables as pandas DataFrames."""
    with pdfplumber.open(pdf_path) as pdf:
        dfs = []
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                if table and len(table) > 1:
                    # Use first row as header
                    df = pd.DataFrame(table[1:], columns=table[0])
                    dfs.append(df)
    return dfs
```

### Image Extraction to Files

```python
from pdf2image import convert_from_path
from pathlib import Path

def extract_images(pdf_path: str, output_dir: str, dpi: int = 150):
    """Extract each page as an image."""
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    images = convert_from_path(pdf_path, dpi=dpi)
    paths = []
    for i, img in enumerate(images, 1):
        img_path = output_path / f"page_{i}.png"
        img.save(str(img_path), "PNG")
        paths.append(str(img_path))
    
    return paths
```

## Fetch Score Customization

### Adjusting Score Weights

Modify the `calculate_fetch_score` method weights:

```python
# Default weights
TEXT_WEIGHT = 0.4       # 40%
STRUCTURE_WEIGHT = 0.3  # 30%
COMPLETENESS_WEIGHT = 0.3  # 30%

# For text-heavy documents (reports, articles)
TEXT_WEIGHT = 0.6
STRUCTURE_WEIGHT = 0.2
COMPLETENESS_WEIGHT = 0.2

# For data-heavy documents (spreadsheets, forms)
TEXT_WEIGHT = 0.3
STRUCTURE_WEIGHT = 0.5
COMPLETENESS_WEIGHT = 0.2
```

### Custom Scoring Criteria

```python
def custom_score(metrics: dict) -> float:
    """Example custom scoring function."""
    score = 50  # Base score
    
    # Text quality bonuses
    if metrics['pages_with_text'] == metrics['total_pages']:
        score += 30
    elif metrics['pages_with_text'] > 0:
        score += 15
    
    # Structure bonuses
    if metrics['tables_extracted'] > 0:
        score += 10
    if metrics['images_extracted'] > 0:
        score += 5
    if metrics['llm_enhanced']:
        score += 5
    
    # Penalties
    score -= len(metrics['warnings']) * 2
    if metrics['ocr_pages'] == metrics['total_pages']:
        score -= 10
    
    return max(0, min(100, score))
```

## LLM Enhancement Prompts

### Structure-Focused Prompt

```python
STRUCTURE_PROMPT = """Analyze this extracted text and:
1. Identify document sections and create proper header hierarchy
2. Detect and properly format any lists (bulleted or numbered)
3. Identify any inline formatting (bold, italic, code)
4. Preserve all content exactly - no summarization

Return only the improved markdown."""
```

### Table-Repair Prompt

```python
TABLE_REPAIR_PROMPT = """This text contains tables that may be malformed.
1. Identify table boundaries
2. Align columns properly
3. Add markdown table syntax
4. Preserve all cell values

Return the fixed markdown tables."""
```

### OCR Cleanup Prompt

```python
OCR_CLEANUP_PROMPT = """This text was extracted via OCR and may have errors.
1. Fix obvious OCR mistakes (0/O, 1/l, etc.)
2. Restore broken words
3. Fix punctuation issues
4. Maintain original structure

Return cleaned text only."""
```

## Performance Optimization

### Batch Processing

```python
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

def batch_extract(pdf_paths: list[str], output_dir: str, workers: int = 4):
    """Process multiple PDFs in parallel."""
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    def process_one(pdf_path):
        from extract_pdf import PDFExtractor
        extractor = PDFExtractor(pdf_path)
        md, score = extractor.extract()
        
        out_file = output_path / (Path(pdf_path).stem + '.md')
        out_file.write_text(md)
        return pdf_path, score['overall_score']
    
    with ProcessPoolExecutor(max_workers=workers) as executor:
        results = list(executor.map(process_one, pdf_paths))
    
    return results
```

### Memory-Efficient Large PDF Processing

```python
def stream_extract(pdf_path: str, output_file: str, chunk_size: int = 10):
    """Process large PDFs in chunks to reduce memory."""
    import pdfplumber
    
    with pdfplumber.open(pdf_path) as pdf, \
         open(output_file, 'w', encoding='utf-8') as out:
        
        total = len(pdf.pages)
        for start in range(0, total, chunk_size):
            end = min(start + chunk_size, total)
            
            for i in range(start, end):
                page = pdf.pages[i]
                text = page.extract_text()
                if text:
                    out.write(f"<!-- Page {i+1} -->\n")
                    out.write(text)
                    out.write("\n\n---\n\n")
            
            # Force garbage collection between chunks
            import gc
            gc.collect()
```
