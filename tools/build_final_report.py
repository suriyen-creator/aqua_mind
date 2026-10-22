from __future__ import annotations

import re
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "AquaMind_Final_ReportV2.md"
OUTPUT = ROOT / "AquaMind_Final_Report_TH_Sarabun_New.docx"

BODY_FONT = "TH Sarabun New"
THAI_FONT = "TH Sarabun New"
NAVY = "17365D"
BLUE = "2E74B5"
DARK_BLUE = "1F4D78"
MUTED = "5B6573"
LIGHT_BLUE = "E8EEF5"
LIGHT_GRAY = "F2F4F7"
WHITE = "FFFFFF"
# A4 portrait with one-inch margins leaves about 6.27 inches of content width.
CONTENT_DXA = 9029


def set_cell_shading(cell, fill: str) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = tc_pr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tc_pr.append(shd)
    shd.set(qn("w:fill"), fill)


def set_cell_margins(cell, top=80, start=120, bottom=80, end=120) -> None:
    tc = cell._tc
    tc_pr = tc.get_or_add_tcPr()
    tc_mar = tc_pr.first_child_found_in("w:tcMar")
    if tc_mar is None:
        tc_mar = OxmlElement("w:tcMar")
        tc_pr.append(tc_mar)
    for margin, value in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        node = tc_mar.find(qn(f"w:{margin}"))
        if node is None:
            node = OxmlElement(f"w:{margin}")
            tc_mar.append(node)
        node.set(qn("w:w"), str(value))
        node.set(qn("w:type"), "dxa")


def set_repeat_table_header(row) -> None:
    tr_pr = row._tr.get_or_add_trPr()
    tbl_header = OxmlElement("w:tblHeader")
    tbl_header.set(qn("w:val"), "true")
    tr_pr.append(tbl_header)


def set_table_geometry(table, widths: list[int]) -> None:
    table.autofit = False
    table.alignment = WD_TABLE_ALIGNMENT.LEFT
    tbl_pr = table._tbl.tblPr
    tbl_w = tbl_pr.find(qn("w:tblW"))
    if tbl_w is None:
        tbl_w = OxmlElement("w:tblW")
        tbl_pr.append(tbl_w)
    tbl_w.set(qn("w:w"), str(sum(widths)))
    tbl_w.set(qn("w:type"), "dxa")
    tbl_ind = tbl_pr.find(qn("w:tblInd"))
    if tbl_ind is None:
        tbl_ind = OxmlElement("w:tblInd")
        tbl_pr.append(tbl_ind)
    tbl_ind.set(qn("w:w"), "120")
    tbl_ind.set(qn("w:type"), "dxa")

    grid = table._tbl.tblGrid
    for child in list(grid):
        grid.remove(child)
    for width in widths:
        col = OxmlElement("w:gridCol")
        col.set(qn("w:w"), str(width))
        grid.append(col)

    for row in table.rows:
        for idx, cell in enumerate(row.cells):
            tc_pr = cell._tc.get_or_add_tcPr()
            tc_w = tc_pr.find(qn("w:tcW"))
            if tc_w is None:
                tc_w = OxmlElement("w:tcW")
                tc_pr.append(tc_w)
            tc_w.set(qn("w:w"), str(widths[idx]))
            tc_w.set(qn("w:type"), "dxa")
            set_cell_margins(cell)
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER


def set_run_font(run, size=None, bold=None, italic=None, color=None, font=BODY_FONT) -> None:
    run.font.name = font
    run._element.get_or_add_rPr()
    rfonts = run._element.rPr.rFonts
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        run._element.rPr.insert(0, rfonts)
    rfonts.set(qn("w:ascii"), font)
    rfonts.set(qn("w:hAnsi"), font)
    rfonts.set(qn("w:eastAsia"), THAI_FONT)
    rfonts.set(qn("w:cs"), THAI_FONT)
    if size is not None:
        run.font.size = Pt(size)
    if bold is not None:
        run.bold = bold
    if italic is not None:
        run.italic = italic
    if color:
        run.font.color.rgb = RGBColor.from_string(color)


def add_field(paragraph, instruction: str, placeholder: str = "") -> None:
    run = paragraph.add_run()
    fld_char = OxmlElement("w:fldChar")
    fld_char.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = instruction
    separate = OxmlElement("w:fldChar")
    separate.set(qn("w:fldCharType"), "separate")
    text = OxmlElement("w:t")
    text.text = placeholder
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    run._r.extend([fld_char, instr, separate, text, end])


def add_hyperlink(paragraph, text: str, url: str):
    part = paragraph.part
    rel_id = part.relate_to(url, "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink", is_external=True)
    hyperlink = OxmlElement("w:hyperlink")
    hyperlink.set(qn("r:id"), rel_id)
    run = OxmlElement("w:r")
    r_pr = OxmlElement("w:rPr")
    color = OxmlElement("w:color")
    color.set(qn("w:val"), BLUE)
    underline = OxmlElement("w:u")
    underline.set(qn("w:val"), "single")
    rfonts = OxmlElement("w:rFonts")
    rfonts.set(qn("w:ascii"), BODY_FONT)
    rfonts.set(qn("w:hAnsi"), BODY_FONT)
    rfonts.set(qn("w:eastAsia"), THAI_FONT)
    r_pr.extend([rfonts, color, underline])
    run.append(r_pr)
    node = OxmlElement("w:t")
    node.text = text
    run.append(node)
    hyperlink.append(run)
    paragraph._p.append(hyperlink)


INLINE_RE = re.compile(r"(\*\*.+?\*\*|`.+?`|\*[^*]+?\*|\[[^\]]+\]\([^)]+\)|https?://[^\s)>]+)")


def add_inline(paragraph, text: str, size=None, color=None) -> None:
    pos = 0
    for match in INLINE_RE.finditer(text):
        if match.start() > pos:
            run = paragraph.add_run(text[pos:match.start()])
            set_run_font(run, size=size, color=color)
        token = match.group(0)
        if token.startswith("**"):
            run = paragraph.add_run(token[2:-2])
            set_run_font(run, size=size, bold=True, color=color)
        elif token.startswith("`"):
            run = paragraph.add_run(token[1:-1])
            set_run_font(run, size=(size or 16) - 1, color=DARK_BLUE, font=BODY_FONT)
            run.font.highlight_color = None
        elif token.startswith("*"):
            run = paragraph.add_run(token[1:-1])
            set_run_font(run, size=size, italic=True, color=color)
        elif token.startswith("["):
            label, target = re.match(r"\[([^\]]+)\]\(([^)]+)\)", token).groups()
            if target.startswith("http"):
                add_hyperlink(paragraph, label, target)
            else:
                run = paragraph.add_run(label)
                set_run_font(run, size=size, color=color)
        else:
            add_hyperlink(paragraph, token, token)
        pos = match.end()
    if pos < len(text):
        run = paragraph.add_run(text[pos:])
        set_run_font(run, size=size, color=color)


def configure_styles(doc: Document) -> None:
    styles = doc.styles
    normal = styles["Normal"]
    normal.font.name = BODY_FONT
    normal.font.size = Pt(16)
    normal._element.rPr.rFonts.set(qn("w:eastAsia"), THAI_FONT)
    normal.paragraph_format.space_after = Pt(6)
    normal.paragraph_format.line_spacing = 1.0
    normal.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    for name, size, color, before, after in (
        ("Heading 1", 24, BLUE, 16, 8),
        ("Heading 2", 20, BLUE, 12, 6),
        ("Heading 3", 18, DARK_BLUE, 8, 4),
        ("Heading 4", 16, DARK_BLUE, 6, 3),
    ):
        style = styles[name]
        style.font.name = BODY_FONT
        style.font.size = Pt(size)
        style.font.bold = True
        style.font.color.rgb = RGBColor.from_string(color)
        style._element.rPr.rFonts.set(qn("w:eastAsia"), THAI_FONT)
        style.paragraph_format.space_before = Pt(before)
        style.paragraph_format.space_after = Pt(after)
        style.paragraph_format.keep_with_next = True

    for name in ("List Bullet", "List Number"):
        style = styles[name]
        style.font.name = BODY_FONT
        style.font.size = Pt(16)
        style._element.rPr.rFonts.set(qn("w:eastAsia"), THAI_FONT)
        style.paragraph_format.left_indent = Inches(0.5)
        style.paragraph_format.first_line_indent = Inches(-0.25)
        style.paragraph_format.space_after = Pt(4)
        style.paragraph_format.line_spacing = 1.0

    if "Caption AquaMind" not in styles:
        cap = styles.add_style("Caption AquaMind", WD_STYLE_TYPE.PARAGRAPH)
    else:
        cap = styles["Caption AquaMind"]
    cap.font.name = BODY_FONT
    cap.font.size = Pt(14)
    cap.font.italic = True
    cap.font.color.rgb = RGBColor.from_string(MUTED)
    cap._element.rPr.rFonts.set(qn("w:eastAsia"), THAI_FONT)
    cap.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap.paragraph_format.space_before = Pt(3)
    cap.paragraph_format.space_after = Pt(10)


def configure_page(section) -> None:
    section.page_width = Inches(8.27)
    section.page_height = Inches(11.69)
    section.top_margin = Inches(1)
    section.bottom_margin = Inches(1)
    section.left_margin = Inches(1)
    section.right_margin = Inches(1)
    section.header_distance = Inches(0.492)
    section.footer_distance = Inches(0.492)
    section.different_first_page_header_footer = True
    pg_num_type = section._sectPr.find(qn("w:pgNumType"))
    if pg_num_type is None:
        pg_num_type = OxmlElement("w:pgNumType")
        section._sectPr.append(pg_num_type)
    # The cover is unnumbered, so the following page displays page 1.
    pg_num_type.set(qn("w:start"), "0")


def configure_header_footer(section) -> None:
    header = section.header
    p = header.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p.paragraph_format.space_after = Pt(0)
    run = p.add_run("AquaMind | รายงานฉบับสมบูรณ์")
    set_run_font(run, size=13, color=MUTED)

    footer = section.footer
    p = footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(0)
    run = p.add_run("หน้า ")
    set_run_font(run, size=13, color=MUTED)
    add_field(p, "PAGE", "1")


def add_cover(doc: Document) -> None:
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(120)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("รายงานฉบับสมบูรณ์")
    set_run_font(r, size=22, bold=True, color=BLUE)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(16)
    p.paragraph_format.space_after = Pt(8)
    r = p.add_run("AquaMind")
    set_run_font(r, size=38, bold=True, color=NAVY)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(28)
    add_inline(p, "แพลตฟอร์มเฝ้าระวังสภาพแวดล้อมชายฝั่งด้วย Weather/Ocean, Sentinel-2, XGBoost, SHAP และกฎแนะนำการตรวจน้ำ", size=20, color=DARK_BLUE)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(30)
    p.paragraph_format.space_after = Pt(6)
    add_inline(p, "การแข่งขันพัฒนาโปรแกรมคอมพิวเตอร์แห่งประเทศไทย ครั้งที่ 28 (NSC 2026)", size=17, color=MUTED)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(4)
    add_inline(p, "หมวดโปรแกรมเพื่องานการพัฒนาด้านวิทยาศาสตร์และเทคโนโลยี", size=16, color=MUTED)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(75)
    add_inline(p, "รายงานฉบับสมบูรณ์ | 17 สิงหาคม 2569", size=16, color=MUTED)
    p.add_run().add_break(WD_BREAK.PAGE)


def split_table_row(line: str) -> list[str]:
    content = line.strip().strip("|")
    return [cell.strip().replace("<br>", "\n").replace("<br/>", "\n") for cell in re.split(r"(?<!\\)\|", content)]


def is_separator_row(cells: list[str]) -> bool:
    return all(re.fullmatch(r":?-{3,}:?", cell.replace(" ", "")) for cell in cells)


def table_widths(rows: list[list[str]]) -> list[int]:
    cols = max(len(row) for row in rows)
    weights = []
    for idx in range(cols):
        lengths = [min(max(len(row[idx]) if idx < len(row) else 0, 4), 60) for row in rows]
        weights.append(max(lengths))
    total = sum(weights) or cols
    widths = [max(720, int(CONTENT_DXA * w / total)) for w in weights]
    diff = CONTENT_DXA - sum(widths)
    widths[-1] += diff
    if widths[-1] < 720:
        shortage = 720 - widths[-1]
        widths[-1] = 720
        donor = max(range(len(widths) - 1), key=lambda i: widths[i])
        widths[donor] -= shortage
    return widths


def add_table(doc: Document, rows: list[list[str]]) -> None:
    cols = max(len(row) for row in rows)
    table = doc.add_table(rows=len(rows), cols=cols)
    table.style = "Table Grid"
    widths = table_widths(rows)
    set_table_geometry(table, widths)
    for r_idx, values in enumerate(rows):
        for c_idx in range(cols):
            cell = table.cell(r_idx, c_idx)
            cell.text = ""
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(1.5)
            p.paragraph_format.line_spacing = 1.0
            value = values[c_idx] if c_idx < len(values) else ""
            for line_idx, segment in enumerate(value.split("\n")):
                if line_idx:
                    p.add_run().add_break()
                add_inline(p, segment, size=14)
            if r_idx == 0:
                set_cell_shading(cell, LIGHT_BLUE)
                for run in p.runs:
                    run.bold = True
                    run.font.color.rgb = RGBColor.from_string(NAVY)
            elif r_idx % 2 == 0:
                set_cell_shading(cell, "FAFBFC")
    set_repeat_table_header(table.rows[0])
    spacer = doc.add_paragraph()
    spacer.paragraph_format.space_after = Pt(2)


def add_code_block(doc: Document, lines: list[str]) -> None:
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Inches(0.18)
    p.paragraph_format.right_indent = Inches(0.18)
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(8)
    p.paragraph_format.line_spacing = 1.0
    p_pr = p._p.get_or_add_pPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), LIGHT_GRAY)
    p_pr.append(shd)
    for idx, line in enumerate(lines):
        if idx:
            p.add_run().add_break()
        run = p.add_run(line or " ")
        set_run_font(run, size=12, color="30343B", font=BODY_FONT)


def build() -> None:
    lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    doc = Document()
    configure_styles(doc)
    for section in doc.sections:
        configure_page(section)
        configure_header_footer(section)
    doc.core_properties.title = "รายงานฉบับสมบูรณ์โครงการ AquaMind"
    doc.core_properties.subject = "Weather-first Coastal Environmental Watch"
    doc.core_properties.author = "คณะผู้พัฒนาโครงการ AquaMind"
    doc.core_properties.keywords = "AquaMind, Sentinel-2, XGBoost, SHAP, Environmental Watch"
    update_fields = OxmlElement("w:updateFields")
    update_fields.set(qn("w:val"), "true")
    doc.settings.element.append(update_fields)

    add_cover(doc)

    # The cover replaces the first five Markdown heading lines.
    idx = 6
    first_major = True
    last_was_image = False
    while idx < len(lines):
        raw = lines[idx]
        line = raw.rstrip()
        stripped = line.strip()

        if stripped.startswith("```"):
            code_lines = []
            idx += 1
            while idx < len(lines) and not lines[idx].strip().startswith("```"):
                code_lines.append(lines[idx])
                idx += 1
            add_code_block(doc, code_lines)
            idx += 1
            last_was_image = False
            continue

        image_match = re.fullmatch(r"!\[(.*?)\]\((.*?)\)", stripped)
        if image_match:
            image_path = ROOT / image_match.group(2)
            if image_path.exists():
                p = doc.add_paragraph()
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p.paragraph_format.space_before = Pt(6)
                p.paragraph_format.space_after = Pt(3)
                run = p.add_run()
                with Image.open(image_path) as img:
                    px_width, px_height = img.size
                target_width = 6.15
                target_height = target_width * px_height / px_width
                if target_height > 7.5:
                    target_height = 7.5
                    target_width = target_height * px_width / px_height
                shape = run.add_picture(
                    str(image_path),
                    width=Inches(target_width),
                    height=Inches(target_height),
                )
                doc_pr = shape._inline.docPr
                doc_pr.set("title", image_match.group(1))
                doc_pr.set("descr", image_match.group(1))
                last_was_image = True
            else:
                p = doc.add_paragraph(style="Caption AquaMind")
                add_inline(p, f"[ไม่พบภาพ: {image_match.group(2)}]", size=9, color="9B1C1C")
                last_was_image = False
            idx += 1
            continue

        if stripped.startswith("|") and "|" in stripped[1:]:
            rows = []
            while idx < len(lines) and lines[idx].strip().startswith("|"):
                cells = split_table_row(lines[idx])
                if not is_separator_row(cells):
                    rows.append(cells)
                idx += 1
            if rows:
                add_table(doc, rows)
            last_was_image = False
            continue

        heading = re.match(r"^(#{1,4})\s+(.*)$", stripped)
        if heading:
            level = len(heading.group(1))
            text = heading.group(2)
            if level == 1:
                if not first_major:
                    doc.add_page_break()
                first_major = False
            p = doc.add_paragraph(style=f"Heading {level}")
            add_inline(p, text)
            idx += 1
            last_was_image = False
            continue

        if stripped in ("---", "***", "___"):
            idx += 1
            continue

        if not stripped:
            idx += 1
            continue

        quote = stripped.startswith(">")
        if quote:
            text = stripped.lstrip("> ")
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Inches(0.22)
            p.paragraph_format.right_indent = Inches(0.12)
            p.paragraph_format.space_before = Pt(4)
            p.paragraph_format.space_after = Pt(8)
            p_pr = p._p.get_or_add_pPr()
            shd = OxmlElement("w:shd")
            shd.set(qn("w:fill"), "F4F6F9")
            p_pr.append(shd)
            add_inline(p, text, color=DARK_BLUE)
            idx += 1
            last_was_image = False
            continue

        bullet = re.match(r"^[-*+]\s+(.*)$", stripped)
        number = re.match(r"^\d+\.\s+(.*)$", stripped)
        checklist = re.match(r"^[-*+]\s+\[([ xX])\]\s+(.*)$", stripped)
        if checklist:
            p = doc.add_paragraph(style="List Bullet")
            marker = "☑ " if checklist.group(1).lower() == "x" else "☐ "
            add_inline(p, marker + checklist.group(2))
        elif bullet:
            p = doc.add_paragraph(style="List Bullet")
            add_inline(p, bullet.group(1))
        elif number:
            p = doc.add_paragraph(style="List Number")
            add_inline(p, number.group(1))
        else:
            style = "Caption AquaMind" if last_was_image and stripped.startswith("**ภาพที่") else None
            p = doc.add_paragraph(style=style)
            add_inline(p, stripped)
        idx += 1
        last_was_image = False

    # Re-apply page tokens to any section created by Word internals.
    for section in doc.sections:
        configure_page(section)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc.save(OUTPUT)
    print(OUTPUT)


if __name__ == "__main__":
    build()
