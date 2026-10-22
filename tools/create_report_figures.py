from pathlib import Path
from textwrap import wrap

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "diagrams"
OUT.mkdir(parents=True, exist_ok=True)

W, H = 1600, 900
FONT = Path(r"C:\Windows\Fonts\tahoma.ttf")
BOLD = Path(r"C:\Windows\Fonts\tahomabd.ttf")

INK = "#0f172a"
MUTED = "#475569"
BLUE = "#0284c7"
BLUE_BG = "#e0f2fe"
TEAL = "#0f766e"
TEAL_BG = "#ccfbf1"
GREEN = "#15803d"
GREEN_BG = "#dcfce7"
AMBER = "#b45309"
AMBER_BG = "#fef3c7"
RED = "#b91c1c"
RED_BG = "#fee2e2"
SLATE_BG = "#f1f5f9"
WHITE = "#ffffff"
BORDER = "#cbd5e1"


def font(size, bold=False):
    return ImageFont.truetype(str(BOLD if bold else FONT), size)


def rounded(draw, xy, fill=WHITE, outline=BORDER, radius=22, width=3):
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


def center_text(draw, xy, text, size=24, color=INK, bold=False, gap=8):
    x1, y1, x2, y2 = xy
    f = font(size, bold)
    max_chars = max(8, int((x2 - x1) / (size * 0.65)))
    lines = []
    for part in text.split("\n"):
        lines.extend(wrap(part, width=max_chars, break_long_words=False) or [""])
    boxes = [draw.textbbox((0, 0), line, font=f) for line in lines]
    total_h = sum(b[3] - b[1] for b in boxes) + gap * (len(lines) - 1)
    y = (y1 + y2 - total_h) / 2
    for line, box in zip(lines, boxes):
        tw = box[2] - box[0]
        th = box[3] - box[1]
        draw.text(((x1 + x2 - tw) / 2, y), line, font=f, fill=color)
        y += th + gap


def left_text(draw, x, y, text, size=22, color=INK, bold=False, max_chars=48, gap=8):
    f = font(size, bold)
    lines = wrap(text, width=max_chars, break_long_words=False)
    for line in lines:
        draw.text((x, y), line, font=f, fill=color)
        y += size + gap
    return y


def arrow(draw, start, end, color=MUTED, width=5):
    draw.line([start, end], fill=color, width=width)
    x2, y2 = end
    x1, y1 = start
    dx, dy = x2 - x1, y2 - y1
    length = max((dx * dx + dy * dy) ** 0.5, 1)
    ux, uy = dx / length, dy / length
    px, py = -uy, ux
    head = 15
    wing = 8
    points = [
        (x2, y2),
        (x2 - ux * head + px * wing, y2 - uy * head + py * wing),
        (x2 - ux * head - px * wing, y2 - uy * head - py * wing),
    ]
    draw.polygon(points, fill=color)


def label(draw, x, y, text, color):
    f = font(18, True)
    box = draw.textbbox((0, 0), text, font=f)
    w = box[2] - box[0] + 22
    h = box[3] - box[1] + 14
    draw.rounded_rectangle((x, y, x + w, y + h), radius=12, fill=WHITE, outline=color, width=2)
    draw.text((x + 11, y + 5), text, font=f, fill=color)


def base_canvas(title, subtitle):
    img = Image.new("RGB", (W, H), "#f8fafc")
    d = ImageDraw.Draw(img)
    d.text((65, 40), title, font=font(36, True), fill=INK)
    d.text((65, 92), subtitle, font=font(20), fill=MUTED)
    return img, d


def make_no_image_flow():
    img, d = base_canvas(
        "เส้นทางใช้งานเมื่อไม่มีภาพและเมื่อระบบขัดข้อง",
        "Operational path หลังผ่าน Validation gate · MVP ปัจจุบันยังแสดง Environmental Watch index จาก Weather/Ocean",
    )

    diamond = [(800, 145), (965, 225), (800, 305), (635, 225)]
    d.polygon(diamond, fill=BLUE_BG, outline=BLUE)
    d.line(diamond + [diamond[0]], fill=BLUE, width=4)
    center_text(d, (655, 170, 945, 280), "มีภาพใหม่\nและผ่าน QC?", 25, INK, True)

    arrow(d, (635, 225), (430, 225), GREEN)
    label(d, 505, 180, "ใช่", GREEN)
    rounded(d, (85, 150, 430, 300), GREEN_BG, GREEN)
    center_text(d, (105, 165, 410, 285), "Full model\nFresh-mode calibration\nแสดงผลพร้อม Data age", 23, INK, True)

    arrow(d, (965, 225), (1120, 225), AMBER)
    label(d, 995, 180, "ไม่ใช่", AMBER)
    diamond2 = [(1280, 145), (1510, 225), (1280, 305), (1050, 225)]
    d.polygon(diamond2, fill=AMBER_BG, outline=AMBER)
    d.line(diamond2 + [diamond2[0]], fill=AMBER, width=4)
    center_text(d, (1090, 170, 1470, 280), "No-image model ผ่านเกณฑ์\nของ Data-age bucket นี้?", 21, INK, True)

    arrow(d, (1185, 285), (1030, 405), GREEN)
    label(d, 1050, 315, "ผ่าน", GREEN)
    rounded(d, (760, 405, 1120, 565), TEAL_BG, TEAL)
    center_text(d, (785, 425, 1095, 545), "Forecast-assisted\nติดป้ายว่าไม่ใช่\nการสังเกตล่าสุด", 23, INK, True)

    arrow(d, (1375, 285), (1430, 405), RED)
    label(d, 1360, 315, "ไม่ผ่าน", RED)
    rounded(d, (1190, 405, 1550, 565), RED_BG, RED)
    center_text(d, (1215, 425, 1525, 545), "Suppress probability\n“ไม่สามารถประเมิน\nระดับฟาร์มได้”", 23, INK, True)

    arrow(d, (940, 565), (940, 650), TEAL)
    arrow(d, (1370, 565), (1370, 650), RED)
    rounded(d, (760, 650, 1550, 760), WHITE, TEAL)
    center_text(d, (790, 665, 1520, 745), "Local confirmation: วัด DO · ตรวจสี/กลิ่นน้ำ · สังเกตสัตว์ · ติดตามเจ้าหน้าที่", 23, INK, True)

    rounded(d, (85, 365, 650, 760), SLATE_BG, MUTED)
    d.text((120, 395), "เมื่อ Data provider หรือระบบล่ม", font=font(27, True), fill=INK)
    y = 455
    items = [
        ("1", "แสดง Degraded / Unavailable"),
        ("2", "บอกเวลาที่ข้อมูลดีครั้งสุดท้าย"),
        ("3", "งดข้อความที่ตีความเป็น All clear"),
        ("4", "แนะนำช่องทางสำรองและการตรวจภาคสนาม"),
    ]
    for n, text in items:
        d.ellipse((120, y - 2, 160, y + 38), fill=BLUE_BG, outline=BLUE, width=2)
        center_text(d, (120, y - 2, 160, y + 38), n, 18, BLUE, True)
        d.text((180, y), text, font=font(21), fill=INK)
        y += 66

    rounded(d, (85, 805, 1550, 865), WHITE, BORDER, radius=16, width=2)
    center_text(d, (105, 810, 1530, 858), "หลักความปลอดภัย: ข้อมูลไม่เพียงพอ ≠ สถานการณ์ปกติ และต้องไม่ใช้สีเขียวแทนการมองไม่เห็นข้อมูล", 20, RED, True)
    path = OUT / "figure_5_2a_no_image_failure_flow.png"
    img.save(path, optimize=True)
    return path


def make_cost_model():
    img, d = base_canvas(
        "แบบจำลองต้นทุนและ Unit economics ของ AquaMind",
        "โครงสร้างสำหรับกรอกข้อมูลจริงจาก Pilot · ไม่ใช้ตัวเลขสมมติเป็นหลักฐานทางธุรกิจ",
    )

    rounded(d, (65, 145, 500, 410), BLUE_BG, BLUE)
    d.text((95, 175), "ต้นทุนคงที่ต่อเดือน", font=font(28, True), fill=INK)
    y = 235
    for item in ["วิศวกรรมและบำรุงรักษา", "Data validation / ภาคสนาม", "Security และ Compliance", "Monitoring / On-call", "บริหารโครงการ"]:
        d.ellipse((100, y + 6, 112, y + 18), fill=BLUE)
        d.text((130, y), item, font=font(20), fill=INK)
        y += 36

    rounded(d, (565, 145, 1035, 410), AMBER_BG, AMBER)
    d.text((595, 175), "ต้นทุนผันแปรต่อฟาร์ม", font=font(28, True), fill=INK)
    y = 235
    for item in ["Compute และ Model inference", "Storage / Egress", "Map และ External API", "Notification และ Support", "Field / Lab ที่ปันส่วน"]:
        d.ellipse((600, y + 6, 612, y + 18), fill=AMBER)
        d.text((630, y), item, font=font(20), fill=INK)
        y += 36

    rounded(d, (1100, 145, 1535, 410), GREEN_BG, GREEN)
    d.text((1130, 175), "รายได้ที่เกิดขึ้นจริง", font=font(28, True), fill=INK)
    y = 245
    for item in ["จำนวนฟาร์มที่จ่าย", "รายได้ต่อฟาร์ม/เดือน", "ส่วนลดและ Churn", "เก็บจาก Invoice / Contract"]:
        d.ellipse((1135, y + 6, 1147, y + 18), fill=GREEN)
        d.text((1165, y), item, font=font(20), fill=INK)
        y += 42

    arrow(d, (280, 410), (465, 500), BLUE)
    arrow(d, (800, 410), (800, 500), AMBER)
    arrow(d, (1315, 410), (1135, 500), GREEN)

    rounded(d, (230, 500, 1370, 665), WHITE, TEAL, radius=26, width=4)
    d.text((270, 530), "สมการหลัก", font=font(25, True), fill=TEAL)
    d.text((475, 525), "ต้นทุนรวม/เดือน = ต้นทุนคงที่ + (จำนวนฟาร์ม × ต้นทุนผันแปร/ฟาร์ม)", font=font(22, True), fill=INK)
    d.text((475, 570), "Contribution margin/ฟาร์ม = รายได้จริง/ฟาร์ม − ต้นทุนผันแปร/ฟาร์ม", font=font(22, True), fill=INK)
    d.text((475, 615), "Break-even farms = ต้นทุนคงที่ ÷ Contribution margin/ฟาร์ม", font=font(22, True), fill=INK)

    arrow(d, (800, 665), (800, 720), TEAL)
    rounded(d, (65, 720, 500, 840), GREEN_BG, GREEN)
    center_text(d, (85, 735, 480, 825), "Best\nใช้ค่าดีที่สุดที่มีหลักฐานรองรับ", 21, INK, True)
    rounded(d, (565, 720, 1035, 840), BLUE_BG, BLUE)
    center_text(d, (585, 735, 1015, 825), "Base\nใช้ค่ากลางจาก Pilot เป็นกรณีหลัก", 21, INK, True)
    rounded(d, (1100, 720, 1535, 840), RED_BG, RED)
    center_text(d, (1120, 735, 1515, 825), "Worst\nรวม Churn, Support และต้นทุนภาคสนาม", 21, INK, True)

    path = OUT / "appendix_f_1_cost_model.png"
    img.save(path, optimize=True)
    return path


if __name__ == "__main__":
    print(make_no_image_flow())
    print(make_cost_model())
