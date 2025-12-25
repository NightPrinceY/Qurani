#!/usr/bin/env python3
"""
Script to convert Markdown files to PDF
"""
import os
import sys
from pathlib import Path
import markdown
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration

def markdown_to_pdf(md_file_path, pdf_file_path, title="Document"):
    """Convert a Markdown file to PDF"""
    # Read the Markdown file
    with open(md_file_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Convert Markdown to HTML
    html_content = markdown.markdown(
        md_content,
        extensions=['extra', 'codehilite', 'tables', 'toc']
    )
    
    # Create full HTML document with styling
    html_doc = f"""
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8">
        <title>{title}</title>
        <style>
            @page {{
                size: A4;
                margin: 2cm;
                @top-center {{
                    content: "{title}";
                    font-size: 12pt;
                    color: #666;
                }}
                @bottom-center {{
                    content: "Page " counter(page) " of " counter(pages);
                    font-size: 10pt;
                    color: #666;
                }}
            }}
            body {{
                font-family: 'DejaVu Sans', 'Arial', sans-serif;
                font-size: 11pt;
                line-height: 1.6;
                color: #333;
                direction: rtl;
                text-align: right;
            }}
            h1 {{
                color: #2c3e50;
                font-size: 24pt;
                margin-top: 30pt;
                margin-bottom: 15pt;
                border-bottom: 2px solid #3498db;
                padding-bottom: 10pt;
            }}
            h2 {{
                color: #34495e;
                font-size: 18pt;
                margin-top: 25pt;
                margin-bottom: 12pt;
                border-bottom: 1px solid #bdc3c7;
                padding-bottom: 8pt;
            }}
            h3 {{
                color: #34495e;
                font-size: 14pt;
                margin-top: 20pt;
                margin-bottom: 10pt;
            }}
            h4 {{
                color: #34495e;
                font-size: 12pt;
                margin-top: 15pt;
                margin-bottom: 8pt;
            }}
            p {{
                margin-bottom: 10pt;
                text-align: justify;
            }}
            ul, ol {{
                margin-bottom: 10pt;
                padding-right: 20pt;
            }}
            li {{
                margin-bottom: 5pt;
            }}
            code {{
                background-color: #f4f4f4;
                padding: 2pt 4pt;
                border-radius: 3pt;
                font-family: 'Courier New', monospace;
                font-size: 10pt;
            }}
            pre {{
                background-color: #f4f4f4;
                padding: 10pt;
                border-radius: 5pt;
                overflow-x: auto;
                margin: 10pt 0;
                direction: ltr;
                text-align: left;
            }}
            pre code {{
                background-color: transparent;
                padding: 0;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 15pt 0;
            }}
            th, td {{
                border: 1px solid #ddd;
                padding: 8pt;
                text-align: right;
            }}
            th {{
                background-color: #3498db;
                color: white;
                font-weight: bold;
            }}
            tr:nth-child(even) {{
                background-color: #f2f2f2;
            }}
            hr {{
                border: none;
                border-top: 1px solid #ddd;
                margin: 20pt 0;
            }}
            strong {{
                color: #2c3e50;
                font-weight: bold;
            }}
            blockquote {{
                border-right: 4px solid #3498db;
                padding-right: 15pt;
                margin: 15pt 0;
                color: #555;
                font-style: italic;
            }}
        </style>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """
    
    # Convert HTML to PDF
    font_config = FontConfiguration()
    html = HTML(string=html_doc)
    html.write_pdf(pdf_file_path, font_config=font_config)
    
    print(f"✓ Converted: {md_file_path} -> {pdf_file_path}")

def main():
    """Main function"""
    docs_dir = Path(__file__).parent / "docs"
    
    # Files to convert
    files_to_convert = [
        ("PROJECT_DOCUMENTATION_AR.md", "PROJECT_DOCUMENTATION_AR.pdf", "مساعد القرآن الصوتي متعدد الوكلاء"),
        ("PROJECT_DOCUMENTATION_EN.md", "PROJECT_DOCUMENTATION_EN.pdf", "Multi-Agent Voice Quran Assistant"),
    ]
    
    for md_file, pdf_file, title in files_to_convert:
        md_path = docs_dir / md_file
        pdf_path = docs_dir / pdf_file
        
        if not md_path.exists():
            print(f"✗ Error: {md_path} not found")
            continue
        
        try:
            markdown_to_pdf(md_path, pdf_path, title)
        except Exception as e:
            print(f"✗ Error converting {md_file}: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()

