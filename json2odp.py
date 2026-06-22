#!/usr/bin/env python3
import json
import argparse
import sys
import os

# Import components from python3-odf
from odf.opendocument import load, OpenDocumentPresentation
from odf.style import Style, MasterPage, PageLayout, GraphicProperties, TextProperties
from odf.draw import Page, Frame, TextBox, Image
from odf.text import P
from odf.presentation import Notes

def add_clean_styled_frame(page, x, y, width, height, text_list, graphic_style_obj, paragraph_style_obj, bulleted=False):
    """Creates an unbordered text layout box and injects paragraphs with specific text styling."""
    frame = Frame(width=width, height=height, x=x, y=y, stylename=graphic_style_obj)
    box = TextBox()
    for text in text_list:
        prefix = "• " if bulleted else ""
        box.addElement(P(text=f"{prefix}{text}", stylename=paragraph_style_obj))
    frame.addElement(box)
    page.addElement(frame)

def add_graph_image(page, x, y, width, height, image_path, doc, graphic_style_obj):
    """Registers an external image file to the ODP package and renders it within a frame wrapper."""
    if not os.path.exists(image_path):
        print(f"Warning: Graph image file '{image_path}' not found. Skipping image placement.")
        return

    # Add picture file to presentation package registry zip structure
    image_href = doc.addPicture(image_path)

    # Instantiate borderless frame shape
    frame = Frame(width=width, height=height, x=x, y=y, stylename=graphic_style_obj)

    # Attach the inner image child node
    img_element = Image(href=image_href)
    frame.addElement(img_element)
    page.addElement(frame)

def create_odp_from_json(json_path, output_path, template_path=None):
    # Load and parse the input JSON file safely
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error reading JSON file: {e}", file=sys.stderr)
        sys.exit(1)

    # Extract global typography parameters
    title_config = data.get("global_title_style", {})
    body_config = data.get("global_body_style", {})

    # Establish Document Workspace Base (Template vs Blank)
    if template_path:
        try:
            doc = load(template_path)
            if doc.presentation:
                for existing_page in list(doc.presentation.childNodes):
                    doc.presentation.removeChild(existing_page)
                    
            master_pages = doc.masterstyles.getElementsByType(MasterPage)
            # FIXED: Safely index the first element ([0]) before calling getAttribute
            if master_pages and len(master_pages) > 0:
                master_page_name = master_pages[0].getAttribute("name")
            else:
                master_page_name = "StandardMasterPage"
        except Exception as e:
            print(f"Error loading template file '{template_path}': {e}", file=sys.stderr)
            sys.exit(1)
    else:
        doc = OpenDocumentPresentation()
        page_layout = PageLayout(name="StandardPageLayout")
        doc.automaticstyles.addElement(page_layout)
        master_page_obj = MasterPage(name="StandardMasterPage", pagelayoutname=page_layout)
        doc.masterstyles.addElement(master_page_obj)
        master_page_name = "StandardMasterPage"

    # Register Transparent Graphic Style (Forces border boxes to disappear)
    transparent_style = Style(name="CleanBoxStyle", family="graphic")
    transparent_style.addElement(GraphicProperties(stroke="none", fill="none"))
    doc.automaticstyles.addElement(transparent_style)

    # Register Custom Typography Styles using JSON settings
    title_paragraph_style = Style(name="JsonTitleParagraphStyle", family="paragraph")
    title_paragraph_style.addElement(TextProperties(
        fontname=title_config.get("font_name", "Arial"),
        fontsize=title_config.get("font_size", "44pt"),
        fontweight=title_config.get("font_weight", "bold")
    ))
    doc.automaticstyles.addElement(title_paragraph_style)

    body_paragraph_style = Style(name="JsonBodyParagraphStyle", family="paragraph")
    body_paragraph_style.addElement(TextProperties(
        fontname=body_config.get("font_name", "Arial"),
        fontsize=body_config.get("font_size", "22pt"),
        fontweight=body_config.get("font_weight", "normal")
    ))
    doc.automaticstyles.addElement(body_paragraph_style)

    # Process Presentation Slide Layout Maps
    for index, slide_data in enumerate(data.get("slides", [])):
        page = Page(name=f"Slide_{index + 1}", masterpagename=master_page_name)
        doc.presentation.addElement(page)

        # 1. Create Title Block (Always Present)
        title_text = slide_data.get("title", f"Slide {index + 1}")
        add_clean_styled_frame(
            page=page, x="2cm", y="1.2cm", width="24cm", height="2.2cm", 
            text_list=[title_text], graphic_style_obj=transparent_style, 
            paragraph_style_obj=title_paragraph_style
        )

        # 2. Create Subtitle Block (If Present)
        subtitle_text = slide_data.get("subtitle")
        if subtitle_text:
            add_clean_styled_frame(
                page=page, x="2cm", y="3.6cm", width="24cm", height="1.5cm", 
                text_list=[subtitle_text], graphic_style_obj=transparent_style, 
                paragraph_style_obj=body_paragraph_style
            )

        # 3. Dynamic Structural Positioning Logic based on layout_type
        layout = slide_data.get("layout_type", "single_column")
        bullets_col1 = slide_data.get("bullets", [])
        graph_file = slide_data.get("graph_path")

        # 3.1 Layout: Full Size Graph Only 
        if layout == "graph_only" and graph_file:
            add_graph_image(
                page=page, x="4cm", y="5.0cm", width="20cm", height="12.5cm",
                image_path=graph_file, doc=doc, graphic_style_obj=transparent_style
            )
            
        # 3.2 Layout: Split Text and Graph Side-by-Side
        elif layout == "text_and_graph" and graph_file:
            add_clean_styled_frame(
                page=page, x="2cm", y="5.2cm", width="11.5cm", height="11cm", 
                text_list=bullets_col1, graphic_style_obj=transparent_style, 
                paragraph_style_obj=body_paragraph_style, bulleted=True
            )
            add_graph_image(
                page=page, x="14.5cm", y="5.2cm", width="11.5cm", height="11cm",
                image_path=graph_file, doc=doc, graphic_style_obj=transparent_style
            )
            
        # 3.3 Layout: Two Column Bullets
        elif layout == "two_column":
            add_clean_styled_frame(
                page=page, x="2cm", y="5.2cm", width="11.5cm", height="11cm", 
                text_list=bullets_col1, graphic_style_obj=transparent_style, 
                paragraph_style_obj=body_paragraph_style, bulleted=True
            )
            bullets_col2 = slide_data.get("bullets_col2", [])
            add_clean_styled_frame(
                page=page, x="14.5cm", y="5.2cm", width="11.5cm", height="11cm", 
                text_list=bullets_col2, graphic_style_obj=transparent_style, 
                paragraph_style_obj=body_paragraph_style, bulleted=True
            )
            
        # 3.4 Layout: Standard Full Width Single Column
        else:
            add_clean_styled_frame(
                page=page, x="2cm", y="5.2cm", width="24cm", height="11cm", 
                text_list=bullets_col1, graphic_style_obj=transparent_style, 
                paragraph_style_obj=body_paragraph_style, bulleted=True
            )

        # 4. Presenter Speaker Notes Area (Invisible on screen)
        notes_data = slide_data.get("notes") or slide_data.get("speaker_notes", [])
        if notes_data:
            notes_element = Notes()
            notes_frame = Frame(width="15cm", height="10cm", x="2cm", y="2cm")
            notes_box = TextBox()
            for note in notes_data:
                notes_box.addElement(P(text=str(note)))
            notes_frame.addElement(notes_box)
            notes_element.addElement(notes_frame)
            page.addElement(notes_element)

    # 5. Compile and Write ODP presentation file
    doc.save(output_path)
    print(f"Success: Fully configured template presentation built at '{output_path}'")

def main():
    parser = argparse.ArgumentParser(
        description="Convert structured JSON schemas directly into clean, borderless ODP slide presentations."
    )
    parser.add_argument("-i", "--input", required=True, help="Path to input source schema .json file.")
    parser.add_argument("-o", "--output", required=True, help="Target destination path where final output .odp is written.")
    parser.add_argument("-t", "--template", default=None, help="Optional presentation base layout template file (.odp).")
    
    args = parser.parse_args()
    create_odp_from_json(args.input, args.output, args.template)

if __name__ == "__main__":
    main()
