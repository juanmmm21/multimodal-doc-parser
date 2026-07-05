# Multimodal Document Parser

This subproject is part of the ai-core-infra modular AI infrastructure. It implements a document parsing and extraction pipeline (Multimodal Document Parser) capable of transforming PDF files and complex images with variable layouts into structured documents in Markdown format (GitHub Flavored Markdown).

This system uses PyMuPDF (fitz) to render and manipulate pages directly in memory, enabling a portable, high-performance pipeline without requiring complex system dependencies like poppler.

## Ingestion Architecture and Rendering Fundamentals

The pipeline consists of three fundamental phases:

### 1. Reading and High-Resolution Rendering
The parser receives the input file. If it's an image (PNG, JPG, JPEG), it's read directly as bytes. If it's a PDF file, it's opened and each page is rendered as a high-resolution PNG image by applying a scaling transformation matrix:

$$\text{Matrix}(s_x, s_y) = \begin{pmatrix} s_x & 0 & 0 \\ 0 & s_y & 0 \\ 0 & 0 & 1 \end{pmatrix}$$

With $s_x = s_y = 2.0$, which doubles the dimensions of the page's bounding box (scaling the standard 72 DPI resolution to 144 DPI). This ensures small text and table borders remain legible for vision models.

### 2. Backend Abstraction and Extraction Strategies
An abstract `ParserBackend` interface is defined that allows switching the processing strategy:

*   **LocalExtractBackend (Local):** A free extractor that obtains the PDF's native digital text using PyMuPDF and organizes it into structured paragraphs and headers using local heuristics based on font size and vertical spacing.
*   **VLMParserBackend (Vision API):** Sends the rendered page (as PNG bytes) to a Vision Language Model (VLM) such as Google Gemini (`gemini-2.5-flash`) or OpenAI's GPT-4o. The model receives a system prompt instructing it to accurately transcribe the document's structure into GFM Markdown:
    *   Preserve measurable tables as Markdown tables (`| col1 | col2 |`).
    *   Preserve header hierarchy (`#`, `##`, `###`).
    *   Replace figures and images with explicit descriptive annotations: `* [Figure: detailed description] *`.

### 3. Fault Tolerance and Resilient Local Fallback
If the network call to the VLM API fails (due to rate limits, network errors, or missing credentials), the pipeline catches the exception, reports a warning, and performs an automatic, safe fallback to `LocalExtractBackend`, ensuring execution continues:

```python
try:
    markdown_content = vlm_backend.parse_page(page_image)
except Exception as e:
    logger.warning(f"VLM failed. Activating local fallback. Reason: {e}")
    markdown_content = local_backend.parse_page(page)
```

## Installation Requirements

*   Python 3.10 or higher
*   PyMuPDF (fitz)
*   Pillow
*   Google-Genai
*   OpenAI

To install the local dependencies, run:
```bash
pip install -r requirements.txt
```

## Environment Configuration (Optional)

To enable the real VLM:
```bash
export GEMINI_API_KEY="your-google-genai-api-key"
# Or
export OPENAI_API_KEY="your-openai-api-key"
```

## Execution and Verification Guide

### 1. Run Unit Tests
The tests simulate fictional PDF pages using `unittest.mock` to verify resilience and fallback behavior:
```bash
python3 -m unittest test_parser.py
```

### 2. Run the Demo
```bash
python3 example.py
```
The script will generate an interactive test PDF document, process it with both backends, and write the unified output to `output_report.md`.

## Connectivity within the ai-core-infra Ecosystem

The `multimodal-doc-parser` module is the entry point for complex documents:
*   Its structured Markdown outputs feed the [semantic-chunking-engine](https://github.com/juanmmm21/semantic-chunking-engine).
*   It interconnects with [bpe-tokenizer-from-scratch](https://github.com/juanmmm21/bpe-tokenizer-from-scratch) to verify that extracted pages don't exceed physical limits.
*   Structured paragraphs and tables are semantically indexed in [nano-vector-db](https://github.com/juanmmm21/nano-vector-db) to enable hybrid search in [nexus-second-brain](https://github.com/juanmmm21/nexus-second-brain).
