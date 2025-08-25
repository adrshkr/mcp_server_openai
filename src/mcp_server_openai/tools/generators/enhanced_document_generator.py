"""
Enhanced Document Generation Tool

This tool provides comprehensive document generation capabilities including:
- DOC generation with Pandoc, WeasyPrint, and LaTeX templates
- HTML generation with modern CSS frameworks and SEO optimization
- PDF generation with multiple engines (WeasyPrint, ReportLab, Pandoc)
- Advanced formatting, templates, and accessibility features
"""

import asyncio
import json
import logging
import os
import subprocess
import tempfile
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# Default configuration
DEFAULT_OUTPUT_FORMAT = "docx"
DEFAULT_TEMPLATE = "professional"
DEFAULT_LANGUAGE = "en"
DEFAULT_FONT_SIZE = 12
DEFAULT_LINE_SPACING = 1.5

# Supported formats and templates
SUPPORTED_FORMATS = ["docx", "pdf", "html", "md", "tex", "rtf"]
DOCUMENT_TEMPLATES = ["professional", "academic", "creative", "minimalist", "corporate"]
LANGUAGES = ["en", "es", "fr", "de", "zh", "ja", "ar"]
CSS_FRAMEWORKS = ["tailwind", "bootstrap", "bulma", "foundation", "custom"]


@dataclass
class DocumentRequest:
    """Request for document generation."""

    title: str
    content: str
    output_format: str = DEFAULT_OUTPUT_FORMAT
    template: str = DEFAULT_TEMPLATE
    language: str = DEFAULT_LANGUAGE
    font_size: int = DEFAULT_FONT_SIZE
    line_spacing: float = DEFAULT_LINE_SPACING
    include_toc: bool = True
    include_page_numbers: bool = True
    custom_css: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    client_id: str | None = None


@dataclass
class DocumentResult:
    """Result from document generation."""

    file_path: str
    file_size: int
    output_format: str
    template_used: str
    processing_time: float
    status: str = "success"
    error_message: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class DocumentTemplate:
    """Document template configuration."""

    name: str
    description: str
    category: str
    css_framework: str
    features: list[str]
    metadata: dict[str, Any] = field(default_factory=dict)


class PandocDocumentGenerator:
    """Document generation using Pandoc with advanced features."""

    def __init__(self):
        try:
            self.pandoc_path = self._find_pandoc()
        except RuntimeError:
            self.pandoc_path = None
            logger.warning("Pandoc not available - some features will be limited")
        self.templates_dir = Path("templates/pandoc")
        self.templates_dir.mkdir(parents=True, exist_ok=True)

    def _find_pandoc(self) -> str:
        """Find Pandoc installation path."""
        try:
            subprocess.run(["pandoc", "--version"], capture_output=True, text=True, check=True)
            return "pandoc"
        except (subprocess.CalledProcessError, FileNotFoundError):
            # Try common installation paths
            common_paths = ["/usr/local/bin/pandoc", "/usr/bin/pandoc", "C:\\Program Files\\Pandoc\\pandoc.exe"]
            for path in common_paths:
                if Path(path).exists():
                    return path
            raise RuntimeError("Pandoc not found. Please install Pandoc first.") from None

    async def generate_document(self, request: DocumentRequest) -> DocumentResult:
        """Generate document using Pandoc."""
        start_time = asyncio.get_event_loop().time()

        try:
            # Create temporary input file
            with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
                f.write(self._create_markdown_content(request))
                input_file = f.name

            # Prepare output file
            output_file = f"output/documents/{request.title.replace(' ', '_')}.{request.output_format}"
            Path(output_file).parent.mkdir(parents=True, exist_ok=True)

            # Build Pandoc command
            cmd = self._build_pandoc_command(input_file, output_file, request)

            # Execute Pandoc
            subprocess.run(cmd, capture_output=True, text=True, check=True)

            # Clean up input file
            os.unlink(input_file)

            # Get file size
            file_size = Path(output_file).stat().st_size if Path(output_file).exists() else 0

            processing_time = asyncio.get_event_loop().time() - start_time

            return DocumentResult(
                file_path=output_file,
                file_size=file_size,
                output_format=request.output_format,
                template_used=request.template,
                processing_time=processing_time,
                status="success",
            )

        except Exception as e:
            processing_time = asyncio.get_event_loop().time() - start_time
            logger.error(f"Pandoc document generation failed: {e}")
            return DocumentResult(
                file_path="",
                file_size=0,
                output_format=request.output_format,
                template_used=request.template,
                processing_time=processing_time,
                status="error",
                error_message=str(e),
            )

    def _create_markdown_content(self, request: DocumentRequest) -> str:
        """Create markdown content with metadata and formatting."""
        content = f"""---
title: {request.title}
language: {request.language}
template: {request.template}
fontsize: {request.font_size}
linestretch: {request.line_spacing}
toc: {str(request.include_toc).lower()}
numbersections: {str(request.include_page_numbers).lower()}
---

# {request.title}

{request.content}
"""
        return content

    def _build_pandoc_command(self, input_file: str, output_file: str, request: DocumentRequest) -> list[str]:
        """Build Pandoc command with appropriate options."""
        cmd = [self.pandoc_path, input_file, "-o", output_file]

        # Add format-specific options
        if request.output_format == "docx":
            cmd.extend(["--reference-doc", f"templates/pandoc/{request.template}.docx"])
        elif request.output_format == "pdf":
            cmd.extend(["--pdf-engine", "xelatex", "--template", f"templates/pandoc/{request.template}.tex"])
        elif request.output_format == "html":
            cmd.extend(
                ["--template", f"templates/pandoc/{request.template}.html", "--css", "templates/pandoc/styles.css"]
            )

        # Add metadata
        if request.metadata:
            for key, value in request.metadata.items():
                cmd.extend(["-M", f"{key}={value}"])

        return cmd


class WeasyPrintDocumentGenerator:
    """HTML to PDF conversion using WeasyPrint."""

    def __init__(self):
        try:
            from weasyprint import CSS, HTML

            self.HTML = HTML
            self.CSS = CSS
            self.available = True
        except ImportError:
            self.available = False
            logger.warning("WeasyPrint not available. Install with: pip install weasyprint")

    async def generate_pdf(self, html_content: str, css_content: str, output_path: str) -> DocumentResult:
        """Generate PDF from HTML using WeasyPrint."""
        if not self.available:
            raise RuntimeError("WeasyPrint not available")

        start_time = asyncio.get_event_loop().time()

        try:
            # Create HTML document
            html_doc = self.HTML(string=html_content)

            # Apply CSS
            css_doc = self.CSS(string=css_content)

            # Generate PDF
            html_doc.write_pdf(output_path, stylesheets=[css_doc])

            # Get file size
            file_size = Path(output_path).stat().st_size if Path(output_path).exists() else 0

            processing_time = asyncio.get_event_loop().time() - start_time

            return DocumentResult(
                file_path=output_path,
                file_size=file_size,
                output_format="pdf",
                template_used="weasyprint",
                processing_time=processing_time,
                status="success",
            )

        except Exception as e:
            processing_time = asyncio.get_event_loop().time() - start_time
            logger.error(f"WeasyPrint PDF generation failed: {e}")
            return DocumentResult(
                file_path="",
                file_size=0,
                output_format="pdf",
                template_used="weasyprint",
                processing_time=processing_time,
                status="error",
                error_message=str(e),
            )


class ReportLabDocumentGenerator:
    """Direct PDF generation using ReportLab."""

    def __init__(self):
        try:
            from reportlab.lib.pagesizes import A4, letter
            from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
            from reportlab.lib.units import inch
            from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

            self.available = True
            self.letter = letter
            self.A4 = A4
            self.SimpleDocTemplate = SimpleDocTemplate
            self.Paragraph = Paragraph
            self.Spacer = Spacer
            self.getSampleStyleSheet = getSampleStyleSheet
            self.ParagraphStyle = ParagraphStyle
            self.inch = inch
        except ImportError:
            self.available = False
            logger.warning("ReportLab not available. Install with: pip install reportlab")

    async def generate_pdf(self, request: DocumentRequest, output_path: str) -> DocumentResult:
        """Generate PDF directly using ReportLab."""
        if not self.available:
            raise RuntimeError("ReportLab not available")

        start_time = asyncio.get_event_loop().time()

        try:
            # Create PDF document
            doc = self.SimpleDocTemplate(output_path, pagesize=self.A4)
            styles = self.getSampleStyleSheet()

            # Create custom styles
            title_style = self.ParagraphStyle(
                "CustomTitle",
                parent=styles["Heading1"],
                fontSize=16,
                spaceAfter=30,
                alignment=1,  # Center alignment
            )

            content_style = self.ParagraphStyle(
                "CustomContent",
                parent=styles["Normal"],
                fontSize=request.font_size,
                spaceAfter=12,
                leading=request.line_spacing * request.font_size,
            )

            # Build content
            story = []

            # Add title
            story.append(self.Paragraph(request.title, title_style))
            story.append(self.Spacer(1, 20))

            # Add content
            paragraphs = request.content.split("\n\n")
            for para in paragraphs:
                if para.strip():
                    story.append(self.Paragraph(para.strip(), content_style))
                    story.append(self.Spacer(1, 12))

            # Build PDF
            doc.build(story)

            # Get file size
            file_size = Path(output_path).stat().st_size if Path(output_path).exists() else 0

            processing_time = asyncio.get_event_loop().time() - start_time

            return DocumentResult(
                file_path=output_path,
                file_size=file_size,
                output_format="pdf",
                template_used="reportlab",
                processing_time=processing_time,
                status="success",
            )

        except Exception as e:
            processing_time = asyncio.get_event_loop().time() - start_time
            logger.error(f"ReportLab PDF generation failed: {e}")
            return DocumentResult(
                file_path="",
                file_size=0,
                output_format="pdf",
                template_used="reportlab",
                processing_time=processing_time,
                status="error",
                error_message=str(e),
            )


class HTMLDocumentGenerator:
    """Modern HTML generation with advanced features."""

    def __init__(self):
        self.templates_dir = Path("templates/html")
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        self._create_default_templates()

    def _create_default_templates(self) -> None:
        """Create default HTML templates if they don't exist."""
        templates = {
            "professional": self._get_professional_template(),
            "academic": self._get_academic_template(),
            "creative": self._get_creative_template(),
            "minimalist": self._get_minimalist_template(),
            "corporate": self._get_corporate_template(),
        }

        for name, template in templates.items():
            template_file = self.templates_dir / f"{name}.html"
            if not template_file.exists():
                template_file.write_text(template)

    def _get_professional_template(self) -> str:
        """Professional HTML template with Tailwind CSS."""
        return """<!DOCTYPE html>
<html lang="{{language}}" class="scroll-smooth">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{{description}}">
    <meta name="keywords" content="{{keywords}}">
    <meta name="author" content="{{author}}">
    <title>{{title}}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Inter', sans-serif; }
        .prose { max-width: 65ch; margin: 0 auto; }
        .prose h1 { font-size: 2.25rem; font-weight: 700; margin-bottom: 1rem; }
        .prose h2 { font-size: 1.875rem; font-weight: 600; margin-bottom: 0.75rem; }
        .prose h3 { font-size: 1.5rem; font-weight: 600; margin-bottom: 0.5rem; }
        .prose p { margin-bottom: 1rem; line-height: 1.75; }
        .prose ul { margin-bottom: 1rem; padding-left: 1.5rem; }
        .prose li { margin-bottom: 0.5rem; }
    </style>
</head>
<body class="bg-gray-50 text-gray-900">
    <header class="bg-white shadow-sm border-b border-gray-200">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex justify-between items-center py-6">
                <h1 class="text-3xl font-bold text-gray-900">{{title}}</h1>
                <nav class="flex space-x-8">
                    <a href="#content" class="text-gray-500 hover:text-gray-700">Content</a>
                    <a href="#toc" class="text-gray-500 hover:text-gray-700">Table of Contents</a>
                </nav>
            </div>
        </div>
    </header>

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div class="grid grid-cols-1 lg:grid-cols-4 gap-8">
            <aside id="toc" class="lg:col-span-1">
                <div class="sticky top-8">
                    <h2 class="text-lg font-semibold text-gray-900 mb-4">Table of Contents</h2>
                    <nav class="space-y-2">
                        {{toc_items}}
                    </nav>
                </div>
            </aside>

            <article id="content" class="lg:col-span-3">
                <div class="prose prose-lg max-w-none">
                    {{content}}
                </div>
            </article>
        </div>
    </main>

    <footer class="bg-white border-t border-gray-200 mt-16">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <p class="text-center text-gray-500">&copy; {{year}} {{author}}. All rights reserved.</p>
        </div>
    </footer>
</body>
</html>"""

    def _get_academic_template(self) -> str:
        """Academic HTML template."""
        return """<!DOCTYPE html>
<html lang="{{language}}" class="scroll-smooth">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{{description}}">
    <meta name="keywords" content="{{keywords}}">
    <meta name="author" content="{{author}}">
    <title>{{title}}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link
        href="https://fonts.googleapis.com/css2?family=Source+Sans+Pro:wght@300;400;600;700&display=swap"
        rel="stylesheet">
    <style>
        body { font-family: 'Source Sans Pro', sans-serif; }
        .academic-content { max-width: 70ch; margin: 0 auto; }
        .academic-content h1 { font-size: 2rem; font-weight: 700; margin-bottom: 1.5rem; text-align: center; }
        .academic-content h2 { font-size: 1.5rem; font-weight: 600; margin-bottom: 1rem; margin-top: 2rem; }
        .academic-content h3 { font-size: 1.25rem; font-weight: 600; margin-bottom: 0.75rem; }
        .academic-content p { margin-bottom: 1.25rem; line-height: 1.8; text-align: justify; }
        .academic-content blockquote {
            border-left: 4px solid #e5e7eb;
            padding-left: 1rem;
            margin: 1.5rem 0;
            font-style: italic;
        }
        .academic-content .citation { font-size: 0.875rem; color: #6b7280; margin-top: 0.5rem; }
    </style>
</head>
<body class="bg-white text-gray-900">
    <header class="bg-gray-900 text-white py-8">
        <div class="max-w-4xl mx-auto px-4">
            <h1 class="text-4xl font-bold text-center">{{title}}</h1>
            <div class="text-center mt-4 text-gray-300">
                <p>Author: {{author}}</p>
                <p>Date: {{date}}</p>
            </div>
        </div>
    </header>

    <main class="max-w-4xl mx-auto px-4 py-12">
        <div class="academic-content">
            {{content}}
        </div>
    </main>

    <footer class="bg-gray-100 border-t border-gray-200 mt-16">
        <div class="max-w-4xl mx-auto px-4 py-8">
            <p class="text-center text-gray-600">Academic Document - {{title}}</p>
        </div>
    </footer>
</body>
</html>"""

    def _get_creative_template(self) -> str:
        """Creative HTML template."""
        return """<!DOCTYPE html>
<html lang="{{language}}" class="scroll-smooth">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{{description}}">
    <meta name="keywords" content="{{keywords}}">
    <meta name="author" content="{{author}}">
    <title>{{title}}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link
        href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap"
        rel="stylesheet">
    <style>
        body { font-family: 'Poppins', sans-serif; }
        .gradient-bg { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        .creative-content { max-width: 75ch; margin: 0 auto; }
        .creative-content h1 {
            font-size: 3rem;
            font-weight: 800;
            margin-bottom: 2rem;
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .creative-content h2 { font-size: 2rem; font-weight: 700; margin-bottom: 1.5rem; color: #4f46e5; }
        .creative-content h3 { font-size: 1.5rem; font-weight: 600; margin-bottom: 1rem; color: #7c3aed; }
        .creative-content p { margin-bottom: 1.5rem; line-height: 1.8; font-size: 1.1rem; }
        .card {
            background: white;
            border-radius: 1rem;
            padding: 2rem;
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
        }
    </style>
</head>
<body class="gradient-bg min-h-screen">
    <header class="text-white text-center py-16">
        <h1 class="text-6xl font-bold mb-4">{{title}}</h1>
        <p class="text-xl opacity-90">Creative Document</p>
    </header>

    <main class="max-w-6xl mx-auto px-4 pb-16">
        <div class="card">
            <div class="creative-content">
                {{content}}
            </div>
        </div>
    </main>
</body>
</html>"""

    def _get_minimalist_template(self) -> str:
        """Minimalist HTML template."""
        return """<!DOCTYPE html>
<html lang="{{language}}" class="scroll-smooth">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{{description}}">
    <meta name="keywords" content="{{keywords}}">
    <meta name="author" content="{{author}}">
    <title>{{title}}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Inter', sans-serif; }
        .minimalist-content { max-width: 60ch; margin: 0 auto; }
        .minimalist-content h1 { font-size: 2.5rem; font-weight: 300; margin-bottom: 2rem; color: #111827; }
        .minimalist-content h2 { font-size: 1.75rem; font-weight: 400; margin-bottom: 1.5rem; color: #374151; }
        .minimalist-content h3 { font-size: 1.25rem; font-weight: 400; margin-bottom: 1rem; color: #4b5563; }
        .minimalist-content p { margin-bottom: 1.5rem; line-height: 1.7; color: #6b7280; }
    </style>
</head>
<body class="bg-white text-gray-900">
    <main class="max-w-4xl mx-auto px-8 py-24">
        <div class="minimalist-content">
            <h1>{{title}}</h1>
            {{content}}
        </div>
    </main>
</body>
</html>"""

    def _get_corporate_template(self) -> str:
        """Corporate HTML template."""
        return """<!DOCTYPE html>
<html lang="{{language}}" class="scroll-smooth">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{{description}}">
    <meta name="keywords" content="{{keywords}}">
    <meta name="author" content="{{author}}">
    <title>{{title}}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Roboto', sans-serif; }
        .corporate-content { max-width: 80ch; margin: 0 auto; }
        .corporate-content h1 { font-size: 2.25rem; font-weight: 700; margin-bottom: 1.5rem; color: #1f2937; }
        .corporate-content h2 { font-size: 1.75rem; font-weight: 600; margin-bottom: 1.25rem; color: #374151; }
        .corporate-content h3 { font-size: 1.375rem; font-weight: 500; margin-bottom: 1rem; color: #4b5563; }
        .corporate-content p { margin-bottom: 1.25rem; line-height: 1.75; color: #6b7280; }
        .corporate-content .highlight {
            background-color: #f3f4f6;
            padding: 1rem;
            border-radius: 0.5rem;
            border-left: 4px solid #3b82f6;
        }
    </style>
</head>
<body class="bg-gray-50 text-gray-900">
    <header class="bg-white shadow-sm border-b border-gray-200">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex justify-between items-center py-6">
                <div class="flex items-center">
                    <div class="w-8 h-8 bg-blue-600 rounded-lg mr-3"></div>
                    <h1 class="text-2xl font-bold text-gray-900">{{title}}</h1>
                </div>
                <div class="text-sm text-gray-500">{{date}}</div>
            </div>
        </div>
    </header>

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
            <div class="corporate-content">
                {{content}}
            </div>
        </div>
    </main>

    <footer class="bg-white border-t border-gray-200 mt-16">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div class="text-center text-gray-500">
                <p>&copy; {{year}} {{company}}. All rights reserved.</p>
            </div>
        </div>
    </footer>
</body>
</html>"""

    async def generate_html(self, request: DocumentRequest) -> DocumentResult:
        """Generate HTML document with modern features."""
        start_time = asyncio.get_event_loop().time()

        try:
            # Load template
            template_file = self.templates_dir / f"{request.template}.html"
            if not template_file.exists():
                template_file = self.templates_dir / "professional.html"

            template_content = template_file.read_text()

            # Prepare content
            content = self._format_content(request.content)
            toc_items = self._generate_toc(request.content)

            # Replace template variables
            html_content = template_content.replace("{{title}}", request.title)
            html_content = html_content.replace("{{content}}", content)
            html_content = html_content.replace("{{toc_items}}", toc_items)
            html_content = html_content.replace("{{language}}", request.language)
            html_content = html_content.replace("{{description}}", request.metadata.get("description", ""))
            html_content = html_content.replace("{{keywords}}", request.metadata.get("keywords", ""))
            html_content = html_content.replace("{{author}}", request.metadata.get("author", "Unknown"))
            html_content = html_content.replace("{{date}}", request.metadata.get("date", ""))
            html_content = html_content.replace("{{year}}", str(datetime.now().year))
            html_content = html_content.replace("{{company}}", request.metadata.get("company", "Company"))

            # Add custom CSS if provided
            if request.custom_css:
                html_content = html_content.replace("</style>", f"{request.custom_css}\n</style>")

            # Save HTML file
            output_file = f"output/documents/{request.title.replace(' ', '_')}.html"
            Path(output_file).parent.mkdir(parents=True, exist_ok=True)
            Path(output_file).write_text(html_content)

            # Get file size
            file_size = Path(output_file).stat().st_size

            processing_time = asyncio.get_event_loop().time() - start_time

            return DocumentResult(
                file_path=output_file,
                file_size=file_size,
                output_format="html",
                template_used=request.template,
                processing_time=processing_time,
                status="success",
            )

        except Exception as e:
            processing_time = asyncio.get_event_loop().time() - start_time
            logger.error(f"HTML generation failed: {e}")
            return DocumentResult(
                file_path="",
                file_size=0,
                output_format="html",
                template_used=request.template,
                processing_time=processing_time,
                status="error",
                error_message=str(e),
            )

    def _format_content(self, content: str) -> str:
        """Format content with proper HTML markup."""
        # Convert markdown-like syntax to HTML
        lines = content.split("\n")
        formatted_lines = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            if line.startswith("# "):
                formatted_lines.append(f"<h1>{line[2:]}</h1>")
            elif line.startswith("## "):
                formatted_lines.append(f"<h2>{line[3:]}</h2>")
            elif line.startswith("### "):
                formatted_lines.append(f"<h3>{line[4:]}</h3>")
            elif line.startswith("- "):
                formatted_lines.append(f"<li>{line[2:]}</li>")
            elif line.startswith("> "):
                formatted_lines.append(f"<blockquote>{line[2:]}</blockquote>")
            else:
                formatted_lines.append(f"<p>{line}</p>")

        return "\n".join(formatted_lines)

    def _generate_toc(self, content: str) -> str:
        """Generate table of contents from content."""
        lines = content.split("\n")
        toc_items = []

        for line in lines:
            line = line.strip()
            if line.startswith("# "):
                title = line[2:]
                anchor = title.lower().replace(" ", "-").replace(":", "").replace(".", "")
                toc_items.append(
                    f'<a href="#{anchor}" class="block text-gray-600 hover:text-gray-900 py-1">{title}</a>'
                )
            elif line.startswith("## "):
                title = line[3:]
                anchor = title.lower().replace(" ", "-").replace(":", "").replace(".", "")
                toc_items.append(
                    f'<a href="#{anchor}" class="block text-gray-500 hover:text-gray-700 py-1 ml-4">{title}</a>'
                )

        return "\n".join(toc_items)


class EnhancedDocumentGenerator:
    """Main class for enhanced document generation."""

    def __init__(self):
        # Initialize generators with error handling
        try:
            self.pandoc_generator = PandocDocumentGenerator()
        except Exception as e:
            logger.warning(f"Pandoc generator initialization failed: {e}")
            self.pandoc_generator = None

        try:
            self.weasyprint_generator = WeasyPrintDocumentGenerator()
        except Exception as e:
            logger.warning(f"WeasyPrint generator initialization failed: {e}")
            self.weasyprint_generator = None

        try:
            self.reportlab_generator = ReportLabDocumentGenerator()
        except Exception as e:
            logger.warning(f"ReportLab generator initialization failed: {e}")
            self.reportlab_generator = None

        # HTML generator should always work (no external dependencies)
        self.html_generator = HTMLDocumentGenerator()

        # Check availability and set up generators
        self.generators = {}
        if self.pandoc_generator:
            self.generators.update(
                {
                    "docx": self.pandoc_generator,
                    "pdf": self.pandoc_generator,  # Primary
                    "md": self.pandoc_generator,
                    "tex": self.pandoc_generator,
                    "rtf": self.pandoc_generator,
                }
            )

        # HTML generator is always available
        self.generators["html"] = self.html_generator

        # Fallback generators for PDF (filter out None values)
        self.pdf_fallbacks = [
            g for g in [self.pandoc_generator, self.weasyprint_generator, self.reportlab_generator] if g is not None
        ]

    async def generate_document(self, request: DocumentRequest) -> DocumentResult:
        """Generate document using the best available generator."""
        start_time = asyncio.get_event_loop().time()

        try:
            # Validate request
            if request.output_format not in SUPPORTED_FORMATS:
                raise ValueError(f"Unsupported output format: {request.output_format}")

            # Create output directory
            output_dir = Path("output/documents")
            output_dir.mkdir(parents=True, exist_ok=True)

            # Generate document based on format
            if request.output_format == "html":
                return await self.html_generator.generate_html(request)
            elif request.output_format == "pdf":
                return await self._generate_pdf_with_fallbacks(request)
            elif request.output_format in ["docx", "md", "tex", "rtf"]:
                if self.pandoc_generator:
                    return await self.pandoc_generator.generate_document(request)
                else:
                    raise RuntimeError(
                        f"Pandoc is required for {request.output_format} generation but is not available"
                    )
            else:
                raise ValueError(f"Unsupported output format: {request.output_format}")

        except Exception as e:
            processing_time = asyncio.get_event_loop().time() - start_time
            logger.error(f"Document generation failed: {e}")
            return DocumentResult(
                file_path="",
                file_size=0,
                output_format=request.output_format,
                template_used=request.template,
                processing_time=processing_time,
                status="error",
                error_message=str(e),
            )

    async def _generate_pdf_with_fallbacks(self, request: DocumentRequest) -> DocumentResult:
        """Generate PDF using fallback strategies."""
        # Try Pandoc first (best quality)
        try:
            result = await self.pandoc_generator.generate_document(request)
            if result.status == "success":
                return result
        except Exception as e:
            logger.warning(f"Pandoc PDF generation failed: {e}")

        # Try WeasyPrint (HTML to PDF)
        try:
            # Generate HTML first
            html_request = DocumentRequest(
                title=request.title,
                content=request.content,
                output_format="html",
                template=request.template,
                language=request.language,
                font_size=request.font_size,
                line_spacing=request.line_spacing,
                include_toc=request.include_toc,
                include_page_numbers=request.include_page_numbers,
                custom_css=request.custom_css,
                metadata=request.metadata,
                client_id=request.client_id,
            )

            html_result = await self.html_generator.generate_html(html_request)
            if html_result.status == "success":
                # Convert HTML to PDF
                output_path = f"output/documents/{request.title.replace(' ', '_')}.pdf"
                return await self.weasyprint_generator.generate_pdf(
                    Path(html_result.file_path).read_text(),
                    "",
                    output_path,  # Default CSS
                )
        except Exception as e:
            logger.warning(f"WeasyPrint PDF generation failed: {e}")

        # Try ReportLab (direct PDF)
        try:
            output_path = f"output/documents/{request.title.replace(' ', '_')}.pdf"
            return await self.reportlab_generator.generate_pdf(request, output_path)
        except Exception as e:
            logger.warning(f"ReportLab PDF generation failed: {e}")

        # All generators failed
        raise RuntimeError("All PDF generation methods failed")


# Global instance
_document_generator = EnhancedDocumentGenerator()


async def generate_document(
    title: str,
    content: str,
    output_format: str = DEFAULT_OUTPUT_FORMAT,
    template: str = DEFAULT_TEMPLATE,
    language: str = DEFAULT_LANGUAGE,
    font_size: int = DEFAULT_FONT_SIZE,
    line_spacing: float = DEFAULT_LINE_SPACING,
    include_toc: bool = True,
    include_page_numbers: bool = True,
    custom_css: str | None = None,
    metadata: dict[str, Any] | None = None,
    client_id: str | None = None,
) -> DocumentResult:
    """Generate document with enhanced features."""
    request = DocumentRequest(
        title=title,
        content=content,
        output_format=output_format,
        template=template,
        language=language,
        font_size=font_size,
        line_spacing=line_spacing,
        include_toc=include_toc,
        include_page_numbers=include_page_numbers,
        custom_css=custom_css,
        metadata=metadata or {},
        client_id=client_id,
    )

    return await _document_generator.generate_document(request)


def register(mcp) -> None:
    """Register the enhanced document generation tools with the MCP server."""

    @mcp.tool()
    async def enhanced_document_generate(
        title: str,
        content: str,
        output_format: str = DEFAULT_OUTPUT_FORMAT,
        template: str = DEFAULT_TEMPLATE,
        language: str = DEFAULT_LANGUAGE,
        font_size: int = DEFAULT_FONT_SIZE,
        line_spacing: float = DEFAULT_LINE_SPACING,
        include_toc: bool = True,
        include_page_numbers: bool = True,
        custom_css: str | None = None,
        metadata: str | None = None,
        client_id: str | None = None,
    ) -> str:
        """Generate enhanced documents with multiple formats and advanced features."""
        try:
            # Parse metadata if provided as JSON string
            parsed_metadata = {}
            if metadata:
                try:
                    parsed_metadata = json.loads(metadata)
                except json.JSONDecodeError:
                    logger.warning(f"Invalid metadata JSON: {metadata}")

            result = await generate_document(
                title=title,
                content=content,
                output_format=output_format,
                template=template,
                language=language,
                font_size=font_size,
                line_spacing=line_spacing,
                include_toc=include_toc,
                include_page_numbers=include_page_numbers,
                custom_css=custom_css,
                metadata=parsed_metadata,
                client_id=client_id,
            )

            return json.dumps(
                {
                    "status": result.status,
                    "file_path": result.file_path,
                    "file_size": result.file_size,
                    "output_format": result.output_format,
                    "template_used": result.template_used,
                    "processing_time": result.processing_time,
                    "error_message": result.error_message,
                    "metadata": result.metadata,
                },
                indent=2,
            )

        except Exception as e:
            logger.error(f"Enhanced document generation failed: {e}")
            return json.dumps(
                {
                    "status": "error",
                    "error_message": str(e),
                    "file_path": "",
                    "file_size": 0,
                    "output_format": output_format,
                    "template_used": template,
                    "processing_time": 0,
                    "metadata": {},
                },
                indent=2,
            )

    @mcp.tool()
    async def enhanced_document_templates() -> str:
        """Get available document templates and their features."""
        templates = [
            {
                "name": "professional",
                "description": "Clean, business-ready documents",
                "category": "business",
                "css_framework": "tailwind",
                "features": ["responsive", "seo_optimized", "accessible", "modern_design"],
            },
            {
                "name": "academic",
                "description": "Formal academic documents with proper citations",
                "category": "academic",
                "css_framework": "tailwind",
                "features": ["citations", "references", "formal_structure", "print_optimized"],
            },
            {
                "name": "creative",
                "description": "Visually appealing creative documents",
                "category": "creative",
                "css_framework": "tailwind",
                "features": ["gradient_backgrounds", "modern_typography", "visual_elements", "interactive"],
            },
            {
                "name": "minimalist",
                "description": "Clean, distraction-free documents",
                "category": "minimalist",
                "css_framework": "tailwind",
                "features": ["clean_design", "focused_content", "fast_loading", "print_friendly"],
            },
            {
                "name": "corporate",
                "description": "Professional corporate documents with branding",
                "category": "corporate",
                "css_framework": "tailwind",
                "features": ["branding", "professional_layout", "structured_content", "business_ready"],
            },
        ]

        return json.dumps({"status": "success", "templates": templates, "total_count": len(templates)}, indent=2)

    @mcp.tool()
    async def enhanced_document_formats() -> str:
        """Get supported document formats and their capabilities."""
        formats = [
            {
                "format": "docx",
                "description": "Microsoft Word document",
                "engine": "pandoc",
                "features": ["templates", "styles", "tables", "images", "headers_footers"],
            },
            {
                "format": "pdf",
                "description": "Portable Document Format",
                "engines": ["pandoc", "weasyprint", "reportlab"],
                "features": ["print_ready", "secure", "universal_compatibility", "high_quality"],
            },
            {
                "format": "html",
                "description": "Web document with modern CSS",
                "engine": "custom",
                "features": ["responsive", "seo_optimized", "accessible", "interactive", "modern_design"],
            },
            {
                "format": "md",
                "description": "Markdown document",
                "engine": "pandoc",
                "features": ["simple_syntax", "version_control_friendly", "easy_editing", "portable"],
            },
            {
                "format": "tex",
                "description": "LaTeX document",
                "engine": "pandoc",
                "features": ["academic_quality", "mathematical_notation", "professional_typesetting", "bibliography"],
            },
            {
                "format": "rtf",
                "description": "Rich Text Format",
                "engine": "pandoc",
                "features": ["cross_platform", "basic_formatting", "universal_compatibility", "lightweight"],
            },
        ]

        return json.dumps({"status": "success", "formats": formats, "total_count": len(formats)}, indent=2)
