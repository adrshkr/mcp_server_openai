#!/usr/bin/env python3
"""
Enhanced Document Generation Demo Script

This script demonstrates the enhanced document generation capabilities including:
- DOC generation with Pandoc
- HTML generation with modern templates
- PDF generation with multiple engines
- Advanced formatting and templates
"""

import asyncio
import os
import sys

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from mcp_server_openai.tools.enhanced_document_generator import generate_document


async def demo_document_generation():
    """Demonstrate enhanced document generation capabilities."""
    print("🚀 Enhanced Document Generation Demo")
    print("=" * 50)

    # Sample content for testing
    sample_content = """# Introduction to Enhanced Document Generation

This is a comprehensive demonstration of our enhanced document generation capabilities.

## Key Features

- **Multiple Formats**: Support for DOCX, PDF, HTML, Markdown, LaTeX, and RTF
- **Advanced Templates**: Professional, academic, creative, minimalist, and corporate styles
- **Modern CSS**: Tailwind CSS integration for beautiful HTML output
- **Fallback Engines**: Multiple PDF generation engines for reliability
- **Custom Styling**: Support for custom CSS and metadata

## Technical Capabilities

- Pandoc integration for high-quality document conversion
- WeasyPrint for HTML to PDF conversion
- ReportLab for direct PDF generation
- Responsive design with modern web standards
- SEO optimization and accessibility features

## Use Cases

- Business documents and reports
- Academic papers and research
- Creative content and presentations
- Technical documentation
- Web content generation

This system provides enterprise-grade document generation with professional output quality."""

    # Test different output formats
    formats_to_test = ["html", "pdf", "docx", "md"]
    templates_to_test = ["professional", "academic", "creative", "minimalist", "corporate"]

    print(f"\n📋 Testing {len(formats_to_test)} output formats:")
    for fmt in formats_to_test:
        print(f"  - {fmt.upper()}")

    print(f"\n🎨 Testing {len(templates_to_test)} templates:")
    for template in templates_to_test:
        print(f"  - {template.capitalize()}")

    print("\n" + "=" * 50)

    # Test HTML generation with different templates
    print("\n🌐 Testing HTML Generation with Different Templates")
    print("-" * 50)

    for template in templates_to_test:
        try:
            print(f"\n📝 Generating HTML with '{template}' template...")

            result = await generate_document(
                title=f"Enhanced Document Demo - {template.capitalize()}",
                content=sample_content,
                output_format="html",
                template=template,
                language="en",
                font_size=14,
                line_spacing=1.6,
                include_toc=True,
                include_page_numbers=True,
                metadata={
                    "description": f"Demo document using {template} template",
                    "keywords": "document generation, demo, enhanced",
                    "author": "Enhanced Document Generator",
                    "date": "2024",
                    "company": "Demo Corp",
                },
            )

            if result.status == "success":
                print("  ✅ Successfully generated HTML document")
                print(f"  📁 File: {result.file_path}")
                print(f"  📊 Size: {result.file_size} bytes")
                print(f"  ⏱️  Time: {result.processing_time:.2f}s")
                print(f"  🎨 Template: {result.template_used}")
            else:
                print(f"  ❌ Failed to generate HTML: {result.error_message}")

        except Exception as e:
            print(f"  ❌ Error generating HTML with {template} template: {e}")

    # Test different output formats with professional template
    print("\n📄 Testing Different Output Formats")
    print("-" * 50)

    for fmt in formats_to_test:
        try:
            print(f"\n📝 Generating {fmt.upper()} document...")

            result = await generate_document(
                title=f"Enhanced Document Demo - {fmt.upper()}",
                content=sample_content,
                output_format=fmt,
                template="professional",
                language="en",
                font_size=12,
                line_spacing=1.5,
                include_toc=True,
                include_page_numbers=True,
                metadata={
                    "description": f"Demo document in {fmt} format",
                    "keywords": "document generation, demo, enhanced",
                    "author": "Enhanced Document Generator",
                },
            )

            if result.status == "success":
                print(f"  ✅ Successfully generated {fmt.upper()} document")
                print(f"  📁 File: {result.file_path}")
                print(f"  📊 Size: {result.file_size} bytes")
                print(f"  ⏱️  Time: {result.processing_time:.2f}s")
                print(f"  🎨 Template: {result.template_used}")
            else:
                print(f"  ❌ Failed to generate {fmt.upper()}: {result.error_message}")

        except Exception as e:
            print(f"  ❌ Error generating {fmt.upper()}: {e}")

    # Test custom CSS
    print("\n🎨 Testing Custom CSS Generation")
    print("-" * 50)

    custom_css = """
    .custom-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 1rem;
        margin-bottom: 2rem;
    }
    .custom-content {
        background: #f8fafc;
        padding: 2rem;
        border-radius: 0.5rem;
        border-left: 4px solid #3b82f6;
    }
    """

    try:
        print("📝 Generating HTML with custom CSS...")

        result = await generate_document(
            title="Enhanced Document Demo - Custom CSS",
            content=sample_content,
            output_format="html",
            template="professional",
            custom_css=custom_css,
            metadata={"description": "Demo document with custom CSS styling", "author": "Enhanced Document Generator"},
        )

        if result.status == "success":
            print("  ✅ Successfully generated HTML with custom CSS")
            print(f"  📁 File: {result.file_path}")
            print(f"  📊 Size: {result.file_size} bytes")
            print(f"  ⏱️  Time: {result.processing_time:.2f}s")
        else:
            print(f"  ❌ Failed to generate HTML with custom CSS: {result.error_message}")

    except Exception as e:
        print(f"  ❌ Error generating HTML with custom CSS: {e}")

    # Test multilingual support
    print("\n🌍 Testing Multilingual Support")
    print("-" * 50)

    languages_to_test = ["en", "es", "fr", "de"]

    for lang in languages_to_test:
        try:
            print(f"\n📝 Generating document in {lang}...")

            result = await generate_document(
                title=f"Enhanced Document Demo - {lang.upper()}",
                content=sample_content,
                output_format="html",
                template="professional",
                language=lang,
                metadata={"description": f"Demo document in {lang} language", "author": "Enhanced Document Generator"},
            )

            if result.status == "success":
                print(f"  ✅ Successfully generated document in {lang}")
                print(f"  📁 File: {result.file_path}")
                print(f"  📊 Size: {result.file_size} bytes")
            else:
                print(f"  ❌ Failed to generate document in {lang}: {result.error_message}")

        except Exception as e:
            print(f"  ❌ Error generating document in {lang}: {e}")

    print("\n" + "=" * 50)
    print("🎉 Enhanced Document Generation Demo Completed!")
    print("\n📁 Generated files are saved in the 'output/documents/' directory")
    print("🔧 Check the file paths above to locate your generated documents")


async def demo_advanced_features():
    """Demonstrate advanced document generation features."""
    print("\n🚀 Advanced Features Demo")
    print("=" * 50)

    # Test large document generation
    print("\n📚 Testing Large Document Generation")
    print("-" * 50)

    large_content = "# Large Document Test\n\n" + "\n\n".join(
        [
            f"## Section {i}\n\nThis is section {i} of the large document test. "
            f"It contains multiple paragraphs to test the system's ability to handle "
            f"larger content volumes and ensure proper formatting and structure.\n\n"
            f"### Subsection {i}.1\n\nSubsection content with additional details "
            f"and formatting examples.\n\n"
            f"### Subsection {i}.2\n\nMore content to demonstrate the system's "
            f"capabilities with complex document structures."
            for i in range(1, 6)
        ]
    )

    try:
        print("📝 Generating large HTML document...")

        result = await generate_document(
            title="Large Document Test",
            content=large_content,
            output_format="html",
            template="academic",
            language="en",
            font_size=12,
            line_spacing=1.8,
            include_toc=True,
            include_page_numbers=True,
            metadata={
                "description": "Large document test for system validation",
                "author": "Enhanced Document Generator",
                "category": "test",
            },
        )

        if result.status == "success":
            print("  ✅ Successfully generated large HTML document")
            print(f"  📁 File: {result.file_path}")
            print(f"  📊 Size: {result.file_size} bytes")
            print(f"  ⏱️  Time: {result.processing_time:.2f}s")
        else:
            print(f"  ❌ Failed to generate large document: {result.error_message}")

    except Exception as e:
        print(f"  ❌ Error generating large document: {e}")

    # Test different font sizes and line spacing
    print("\n🔤 Testing Typography Options")
    print("-" * 50)

    typography_tests = [
        {"font_size": 10, "line_spacing": 1.2, "name": "Small, Compact"},
        {"font_size": 14, "line_spacing": 1.6, "name": "Medium, Readable"},
        {"font_size": 18, "line_spacing": 2.0, "name": "Large, Spacious"},
    ]

    for test in typography_tests:
        try:
            print(f"\n📝 Testing {test['name']} typography...")

            result = await generate_document(
                title=f"Typography Test - {test['name']}",
                content=sample_content,
                output_format="html",
                template="minimalist",
                language="en",
                font_size=test["font_size"],
                line_spacing=test["line_spacing"],
                metadata={
                    "description": f"Typography test with {test['name']} settings",
                    "author": "Enhanced Document Generator",
                },
            )

            if result.status == "success":
                print(f"  ✅ Successfully generated document with {test['name']} typography")
                print(f"  📁 File: {result.file_path}")
                print(f"  📊 Size: {result.file_size} bytes")
            else:
                print(f"  ❌ Failed to generate document: {result.error_message}")

        except Exception as e:
            print(f"  ❌ Error generating document: {e}")


async def main():
    """Run the enhanced document generation demo."""
    try:
        await demo_document_generation()
        await demo_advanced_features()

        print("\n🎯 Demo Summary")
        print("=" * 50)
        print("✅ HTML generation with multiple templates")
        print("✅ Multiple output formats (HTML, PDF, DOCX, MD)")
        print("✅ Custom CSS styling")
        print("✅ Multilingual support")
        print("✅ Large document handling")
        print("✅ Typography customization")
        print("✅ Advanced metadata support")

        print("\n🚀 The Enhanced Document Generation system is ready for production use!")

    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
