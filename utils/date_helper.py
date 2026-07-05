from datetime import timedelta

# Nama bulan dalam Bahasa Indonesia
BULAN_INDO = [
    "Januari", "Februari", "Maret", "April", "Mei", "Juni",
    "Juli", "Agustus", "September", "Oktober", "November", "Desember",
]

HARI_INDO = [
    "Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu",
]


def format_date_indo(dt, with_day_name: bool = False) -> str:
    """
    Format tanggal saja (tanpa jam) dalam Bahasa Indonesia.
    dt diasumsikan tersimpan sebagai UTC (default SQLAlchemy datetime.utcnow),
    dikonversi dulu ke WIB (+7) supaya tanggalnya akurat untuk user Indonesia
    (menghindari kasus tanggal "mundur satu hari" kalau kejadian dekat tengah malam).

    Contoh hasil:
        format_date_indo(dt)              -> "05 Juli 2026"
        format_date_indo(dt, True)         -> "Minggu, 05 Juli 2026"
    """
    if not dt:
        return "-"
    try:
        local_dt = dt + timedelta(hours=7)  # UTC -> WIB, cukup untuk akurasi tanggal
        tanggal = f"{local_dt.day:02d} {BULAN_INDO[local_dt.month - 1]} {local_dt.year}"
        if with_day_name:
            nama_hari = HARI_INDO[local_dt.weekday()]
            return f"{nama_hari}, {tanggal}"
        return tanggal
    except Exception:
        return dt.strftime("%d/%m/%Y")