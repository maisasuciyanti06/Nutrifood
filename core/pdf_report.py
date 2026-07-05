from io import BytesIO
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from functools import partial

import requests

# ── Zona Waktu Indonesia ──────────────────────────────────────────────────────
# WIB  = Waktu Indonesia Barat  (UTC+7) → Asia/Jakarta
# WITA = Waktu Indonesia Tengah (UTC+8) → Asia/Makassar
# WIT  = Waktu Indonesia Timur  (UTC+9) → Asia/Jayapura
ZONA_MAP = {
    "WIB":  ZoneInfo("Asia/Jakarta"),
    "WITA": ZoneInfo("Asia/Makassar"),
    "WIT":  ZoneInfo("Asia/Jayapura"),
}
DEFAULT_ZONA = "WIB"


def _resolve_zona(zona: str) -> ZoneInfo:
    return ZONA_MAP.get((zona or DEFAULT_ZONA).upper(), ZONA_MAP[DEFAULT_ZONA])


def _now_zona(zona: str = DEFAULT_ZONA) -> datetime:
    """Waktu sekarang pada zona Indonesia yang dipilih (bukan waktu server)."""
    return datetime.now(_resolve_zona(zona))


HARI_ID = {
    "Monday":    "Senin",
    "Tuesday":   "Selasa",
    "Wednesday": "Rabu",
    "Thursday":  "Kamis",
    "Friday":    "Jumat",
    "Saturday":  "Sabtu",
    "Sunday":    "Minggu",
}

def _format_tanggal(dt: datetime, zona: str = DEFAULT_ZONA) -> str:
    zona = (zona or DEFAULT_ZONA).upper()
    tz = _resolve_zona(zona)
    # Pastikan dt selalu dikonversi ke zona yang diminta sebelum diformat
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=tz)
    else:
        dt = dt.astimezone(tz)
    hari_en = dt.strftime("%A")
    hari_id = HARI_ID.get(hari_en, hari_en)
    return f"{hari_id}, {dt.strftime('%d %B %Y, %H:%M')} {zona}"

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image as RLImage,
    Table, TableStyle, HRFlowable, PageBreak,
)
from reportlab.platypus.flowables import KeepTogether
from reportlab.lib.utils import ImageReader


LOGO_PATH = Path(__file__).parent.parent / "assets" / "logo.png"

# ── Color Palette ─────────────────────────────────────────────────────────────
PRIMARY       = colors.HexColor("#E91E63")
PRIMARY_DARK  = colors.HexColor("#C2185B")
PRIMARY_LIGHT = colors.HexColor("#FCE4EC")
TEXT          = colors.HexColor("#1F2937")
TEXT_LIGHT    = colors.HexColor("#6B7280")
BORDER        = colors.HexColor("#E5E7EB")
WHITE         = colors.white
BG_LIGHT      = colors.HexColor("#F8FAFC")
SUCCESS       = colors.HexColor("#16A34A")
ACCENT        = colors.HexColor("#FFF0F5")


def _fetch_image(url: str, max_w: float = 45 * mm, max_h: float = 45 * mm):
    try:
        resp = requests.get(url, timeout=8)
        resp.raise_for_status()
        img_buffer = BytesIO(resp.content)

        from PIL import Image as PILImage
        pil_img = PILImage.open(img_buffer)
        w, h = pil_img.size
        ratio = min(max_w / w, max_h / h)
        new_w, new_h = w * ratio, h * ratio

        img_buffer.seek(0)
        rl_img = RLImage(img_buffer, width=new_w, height=new_h)
        rl_img.hAlign = "CENTER"
        return rl_img
    except Exception:
        return None


def _styles():
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name="DocTitle",
        fontName="Helvetica-Bold",
        fontSize=22,
        textColor=TEXT,
        alignment=TA_CENTER,
        spaceAfter=4,
        leading=28,
    ))

    styles.add(ParagraphStyle(
        name="DocSubtitle",
        fontName="Helvetica",
        fontSize=11,
        textColor=TEXT_LIGHT,
        alignment=TA_CENTER,
        spaceAfter=2,
        leading=16,
    ))

    styles.add(ParagraphStyle(
        name="SectionHeader",
        fontName="Helvetica-Bold",
        fontSize=11,
        textColor=PRIMARY,
        spaceAfter=6,
        spaceBefore=4,
    ))

    styles.add(ParagraphStyle(
        name="MenuTitle",
        fontName="Helvetica-Bold",
        fontSize=12,
        textColor=TEXT,
        spaceAfter=5,
        leading=16,
    ))

    styles.add(ParagraphStyle(
        name="MenuInfo",
        fontName="Helvetica",
        fontSize=9.5,
        textColor=TEXT_LIGHT,
        leading=15,
        spaceAfter=3,
    ))

    styles.add(ParagraphStyle(
        name="MenuInfoBold",
        fontName="Helvetica-Bold",
        fontSize=9.5,
        textColor=TEXT,
        leading=15,
    ))

    styles.add(ParagraphStyle(
        name="MenuLink",
        fontName="Helvetica",
        fontSize=9,
        textColor=PRIMARY,
        leading=13,
    ))

    styles.add(ParagraphStyle(
        name="BadgeText",
        fontName="Helvetica-Bold",
        fontSize=9,
        textColor=WHITE,
        alignment=TA_CENTER,
        leading=12,
    ))

    styles.add(ParagraphStyle(
        name="StatValue",
        fontName="Helvetica-Bold",
        fontSize=16,
        textColor=PRIMARY,
        alignment=TA_CENTER,
        leading=20,
    ))

    styles.add(ParagraphStyle(
        name="StatLabel",
        fontName="Helvetica",
        fontSize=8.5,
        textColor=TEXT_LIGHT,
        alignment=TA_CENTER,
        leading=12,
    ))

    styles.add(ParagraphStyle(
        name="FooterText",
        fontName="Helvetica",
        fontSize=8,
        textColor=TEXT_LIGHT,
        alignment=TA_CENTER,
        leading=12,
    ))

    styles.add(ParagraphStyle(
        name="NoImageText",
        fontName="Helvetica",
        fontSize=8,
        textColor=TEXT_LIGHT,
        alignment=TA_CENTER,
        leading=12,
    ))

    return styles


def _draw_header_footer(canvas, doc, zona: str = DEFAULT_ZONA):
    """Gambar header dan footer di setiap halaman."""
    canvas.saveState()
    w, h = A4

    # Header bar tipis di atas
    canvas.setFillColor(PRIMARY)
    canvas.rect(0, h - 8 * mm, w, 8 * mm, fill=1, stroke=0)

    # Footer
    canvas.setFillColor(TEXT_LIGHT)
    canvas.setFont("Helvetica", 7.5)
    canvas.drawCentredString(
        w / 2,
        10 * mm,
        f"Nutri Food  |  Halaman {doc.page}  |  {_format_tanggal(_now_zona(zona), zona)}",
    )

    # Garis footer
    canvas.setStrokeColor(BORDER)
    canvas.setLineWidth(0.5)
    canvas.line(18 * mm, 14 * mm, w - 18 * mm, 14 * mm)

    canvas.restoreState()


def generate_meal_planner_pdf(
        plans,
        username: str = "",
        days=None,
        timezone: str = DEFAULT_ZONA,
) -> bytes:
    """
    timezone: "WIB" (Asia/Jakarta, UTC+7), "WITA" (Asia/Makassar, UTC+8),
              atau "WIT" (Asia/Jayapura, UTC+9). Default "WIB".
    """
    zona = (timezone or DEFAULT_ZONA).upper()
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=22 * mm,
        bottomMargin=22 * mm,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        title="Laporan Meal Planner - Nutri Food",
        author="Nutri Food",
    )

    styles = _styles()
    story  = []

    page_w = A4[0] - 36 * mm  # lebar konten

    # ── COVER HEADER ─────────────────────────────────────────────────────────
    # Logo + judul dalam satu tabel agar sejajar
    logo_cell = ""
    if LOGO_PATH.exists():
        logo = RLImage(str(LOGO_PATH), width=22 * mm, height=28 * mm)
        logo_cell = logo

    header_info = [
        Paragraph("Laporan Meal Planner", styles["DocTitle"]),
        Paragraph(
            f"Disusun untuk: <b>{username}</b>" if username else "Nutri Food",
            styles["DocSubtitle"],
        ),
        Paragraph(
            f"Dicetak pada {_format_tanggal(_now_zona(zona), zona)}",
            styles["DocSubtitle"],
        ),
    ]

    if logo_cell:
        cover_table = Table(
            [[logo_cell, header_info]],
            colWidths=[30 * mm, page_w - 30 * mm],
        )
        cover_table.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (0, 0), (0, 0), "CENTER"),
            ("LEFTPADDING", (1, 0), (1, 0), 14),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ]))
        story.append(cover_table)
    else:
        for p in header_info:
            story.append(p)

    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY))
    story.append(Spacer(1, 14))

    # ── RINGKASAN STATISTIK ───────────────────────────────────────────────────
    total_kal   = sum(float(p.calories or 0) for p in plans)
    total_prot  = sum(float(p.protein  or 0) for p in plans)
    total_porsi = sum(float(getattr(p, "servings", 0) or 0) for p in plans)
    avg_kal     = total_kal / len(plans) if plans else 0

    story.append(Paragraph("Ringkasan Nutrisi", styles["SectionHeader"]))

    stat_data = [[
        [
            Paragraph(f"{len(plans)}", styles["StatValue"]),
            Paragraph("Total Menu", styles["StatLabel"]),
        ],
        [
            Paragraph(f"{total_kal:.0f}", styles["StatValue"]),
            Paragraph("Total Kalori", styles["StatLabel"]),
        ],
        [
            Paragraph(f"{total_prot:.1f} g", styles["StatValue"]),
            Paragraph("Total Protein", styles["StatLabel"]),
        ],
        [
            Paragraph(f"{total_porsi:.0f}", styles["StatValue"]),
            Paragraph("Total Porsi", styles["StatLabel"]),
        ],
        [
            Paragraph(f"{avg_kal:.0f}", styles["StatValue"]),
            Paragraph("Rata-rata Kalori", styles["StatLabel"]),
        ],
    ]]

    col_w = page_w / 5
    stat_table = Table(stat_data, colWidths=[col_w] * 5)
    stat_table.setStyle(TableStyle([
        ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("BACKGROUND",    (0, 0), (-1, -1), ACCENT),
        ("BOX",           (0, 0), (-1, -1), 0.8, BORDER),
        ("INNERGRID",     (0, 0), (-1, -1), 0.5, BORDER),
        ("TOPPADDING",    (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("ROUNDEDCORNERS", [4, 4, 4, 4]),
    ]))

    story.append(stat_table)
    story.append(Spacer(1, 20))

    if days is None:
        days = [
            "Senin",
            "Selasa",
            "Rabu",
            "Kamis",
            "Jumat",
            "Sabtu",
            "Minggu"
        ]

    story.append(
    Paragraph(
        "Ringkasan Per Hari",
        styles["SectionHeader"]
        )
    )

    ringkasan_hari = []

    for day in days:

        day_plans = [
            p for p in plans
            if getattr(p, "hari", "") == day
        ]

        ringkasan_hari.append([
            day,
            str(len(day_plans)),
            f"{sum(float(p.calories or 0) for p in day_plans):.0f}",
            f"{sum(float(p.protein or 0) for p in day_plans):.1f}"
        ])

    summary_table = Table(
        [["Hari","Menu","Kalori","Protein"]] + ringkasan_hari,
        colWidths=[40*mm,30*mm,40*mm,40*mm]
    )

    summary_table.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),PRIMARY),
        ("TEXTCOLOR",(0,0),(-1,0),WHITE),
        ("GRID",(0,0),(-1,-1),0.5,BORDER),
        ("ALIGN",(0,0),(-1,-1),"CENTER"),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 20))

    # ── DAFTAR MENU ───────────────────────────────────────────────────────────
    story.append(Paragraph("Daftar Menu", styles["SectionHeader"]))
    story.append(Spacer(1, 6))

    counter = 1

    for day in days:

        day_plans = [
            p for p in plans
            if getattr(p, "hari", "") == day
        ]

        if not day_plans:
            continue

    # ==================================
    # HEADER HARI
    # ==================================
        story.append(
            Paragraph(
                f"{day}",
                styles["SectionHeader"]
            )
        )

        story.append(Spacer(1, 6))

        day_kal = sum(float(p.calories or 0) for p in day_plans)
        day_prot = sum(float(p.protein or 0) for p in day_plans)

        info_table = Table(
            [[
                f"Jumlah Menu : {len(day_plans)}",
                f"Kalori : {day_kal:.0f}",
                f"Protein : {day_prot:.1f} g"
            ]],
            colWidths=[50*mm, 50*mm, 50*mm]
        )

        info_table.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,-1), ACCENT),
            ("BOX", (0,0), (-1,-1), 0.5, BORDER),
            ("INNERGRID", (0,0), (-1,-1), 0.5, BORDER),
            ("ALIGN", (0,0), (-1,-1), "CENTER"),
            ("TOPPADDING", (0,0), (-1,-1), 6),
            ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ]))

        story.append(info_table)
        story.append(Spacer(1, 10))

        for plan in day_plans:

            # Gambar
            img_cell = None

            if getattr(plan, "image_url", None) and str(plan.image_url).startswith("http"):
                img_cell = _fetch_image(plan.image_url)

            if img_cell is None:
                img_cell = Paragraph(
                    "<br/>Tidak ada<br/>gambar",
                    styles["NoImageText"]
                )

            # Info nutrisi
            kalori  = float(plan.calories or 0)
            protein = float(plan.protein  or 0)
            porsi   = float(getattr(plan, "servings", 0) or 0)
            kal_per_porsi = kalori / max(porsi, 1)

            # Tabel nutrisi kecil
            nutrisi_data = [[
                Paragraph(f"<b>{kalori:.0f}</b><br/><font color='#6B7280' size='8'>Kalori</font>", styles["MenuInfo"]),
                Paragraph(f"<b>{protein:.1f} g</b><br/><font color='#6B7280' size='8'>Protein</font>", styles["MenuInfo"]),
                Paragraph(f"<b>{porsi:.0f}</b><br/><font color='#6B7280' size='8'>Porsi</font>", styles["MenuInfo"]),
                Paragraph(f"<b>{kal_per_porsi:.0f}</b><br/><font color='#6B7280' size='8'>Kal/Porsi</font>", styles["MenuInfo"]),
            ]]

            nutrisi_table = Table(nutrisi_data, colWidths=[25 * mm] * 4)
            nutrisi_table.setStyle(TableStyle([
                ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
                ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
                ("BACKGROUND",    (0, 0), (-1, -1), BG_LIGHT),
                ("BOX",           (0, 0), (-1, -1), 0.5, BORDER),
                ("INNERGRID",     (0, 0), (-1, -1), 0.5, BORDER),
                ("TOPPADDING",    (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]))

            # Info bagian kanan
            info_content = [
                Paragraph(
                    plan.recipe_name,
                    styles["MenuTitle"]
                ),
                Spacer(1, 6),
                nutrisi_table,
            ]

            if getattr(plan, "recipe_url", None) and plan.recipe_url:
                url_display = plan.recipe_url
                if len(url_display) > 65:
                    url_display = url_display[:62] + "..."
                info_content.append(Spacer(1, 4))
                info_content.append(Paragraph(
                    f'<link href="{plan.recipe_url}"><u>{url_display}</u></link>',
                    styles["MenuLink"],
                ))

            # Baris utama: gambar | info
            row_table = Table(
                [[img_cell, info_content]],
                colWidths=[48 * mm, page_w - 48 * mm],
            )
            row_table.setStyle(TableStyle([
                ("VALIGN",        (0, 0), (-1, -1), "TOP"),
                ("ALIGN",         (0, 0), (0, 0),   "CENTER"),
                ("LEFTPADDING",   (1, 0), (1, 0),   12),
                ("TOPPADDING",    (0, 0), (-1, -1),  8),
                ("BOTTOMPADDING", (0, 0), (-1, -1),  8),
                ("BACKGROUND",    (0, 0), (-1, -1),  WHITE),
                ("BOX",           (0, 0), (-1, -1),  0.5, BORDER),
            ]))

            story.append(KeepTogether([
                row_table,
                Spacer(1, 8),
            ]))

    # ── FOOTER NOTE ───────────────────────────────────────────────────────────
    story.append(Spacer(1, 16))
    story.append(HRFlowable(width="100%", thickness=0.8, color=BORDER))
    story.append(Spacer(1, 8))
    story.append(Paragraph(
        "Laporan ini dibuat secara otomatis oleh sistem <b>Nutri Food</b>. "
        "Informasi kalori dan protein merupakan perkiraan berdasarkan dataset resep.",
        styles["FooterText"],
    ))

    footer_fn = partial(_draw_header_footer, zona=zona)
    doc.build(story, onFirstPage=footer_fn, onLaterPages=footer_fn)
    buffer.seek(0)
    return buffer.getvalue()