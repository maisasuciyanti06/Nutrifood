import streamlit as st

FONT_IMPORT = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
"""

PRIMARY       = "#E91E63"
PRIMARY_DARK  = "#C2185B"
PRIMARY_LIGHT = "#FCE4EC"
TEXT          = "#1F2937"
TEXT_LIGHT    = "#6B7280"
BACKGROUND    = "#F8FAFC"
BORDER        = "#E5E7EB"
CARD          = "#FFFFFF"
SUCCESS       = "#16A34A"
ERROR         = "#DC2626"
WARNING       = "#D97706"

HIDE_NAV_CSS = f"""
<style>

{FONT_IMPORT}

/* =====================================================
   HIDE STREAMLIT DEFAULT
===================================================== */

header[data-testid="stHeader"],
footer,
[data-testid="stDecoration"],
[data-testid="stSidebarNav"],
[data-testid="stSidebarNavItems"],
[data-testid="stSidebarNavSeparator"] {{
    display: none !important;
}}

/* =====================================================
   APP — LEBAR PENUH
===================================================== */

.stApp {{
    background: {BACKGROUND};
}}

.main .block-container {{
    max-width: 100% !important;
    width: 100% !important;
    padding-top: 1.5rem !important;
    padding-bottom: 2rem !important;
    padding-left: 1.5rem !important;
    padding-right: 1.5rem !important;
}}

/* Konten utama mengisi sisa ruang setelah sidebar */
.main {{
    flex: 1 1 auto !important;
    min-width: 0 !important;
}}

html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif;
}}

/* =====================================================
   SIDEBAR — ramping & minimalis (DESKTOP)
===================================================== */

section[data-testid="stSidebar"] {{
    width: 200px !important;
    min-width: 200px !important;
    max-width: 200px !important;
    background: white !important;
    border-right: 1px solid {BORDER} !important;
}}

section[data-testid="stSidebar"] > div:first-child {{
    width: 200px !important;
    padding: 0 !important;
}}

.sidebar-profile {{
    background: transparent !important;
    padding: 0 !important;
}}

/* Sidebar nav link */
section[data-testid="stSidebar"] [data-testid="stPageLink"] {{
    font-size: 13px !important;
    padding: 6px 12px !important;
}}

/* =====================================================
   SIDEBAR MOBILE — DRAWER (hide/show)
   Sidebar disembunyikan di luar layar secara default, lalu
   ditampilkan lewat tombol hamburger custom. Toggle dikontrol
   murni via CSS + onclick (class "nf-sidebar-open" di <body>),
   TANPA rerun Streamlit, supaya buka/tutup selalu konsisten.
===================================================== */

@media (max-width: 768px) {{
    /* Matikan kontrol collapse/expand bawaan Streamlit supaya tidak
       bentrok dengan toggle custom kita */
    [data-testid="stSidebarCollapsedControl"],
    [data-testid="stSidebarCollapseButton"] {{
        display: none !important;
    }}

    section[data-testid="stSidebar"] {{
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        height: 100vh !important;
        width: 250px !important;
        min-width: 250px !important;
        max-width: 250px !important;
        z-index: 999999 !important;
        box-shadow: 4px 0 24px rgba(0,0,0,.18) !important;
        transition: transform .25s ease-in-out !important;
        transform: translateX(-100%) !important;
        visibility: visible !important;
    }}

    body.nf-sidebar-open section[data-testid="stSidebar"] {{
        transform: translateX(0) !important;
    }}

    .main .block-container {{
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        padding-top: 4.5rem !important; /* ruang untuk tombol hamburger */
    }}

    /* Tombol hamburger custom */
    #nf-hamburger-btn {{
        position: fixed;
        top: 14px;
        left: 14px;
        z-index: 1000000;
        width: 44px;
        height: 44px;
        border-radius: 10px;
        background: white;
        color: {PRIMARY};
        border: 1px solid {BORDER};
        box-shadow: 0 2px 10px rgba(0,0,0,.10);
        font-size: 20px;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
    }}

    .nf-icon-close {{ display: none; }}
    body.nf-sidebar-open .nf-icon-open  {{ display: none; }}
    body.nf-sidebar-open .nf-icon-close {{ display: inline; }}

    /* Overlay gelap di belakang sidebar saat terbuka */
    #nf-overlay {{
        display: none;
        position: fixed;
        inset: 0;
        background: rgba(0,0,0,.4);
        z-index: 999998;
    }}
    body.nf-sidebar-open #nf-overlay {{
        display: block;
    }}
}}

@media (min-width: 769px) {{
    #nf-hamburger-btn, #nf-overlay {{
        display: none !important;
    }}
}}

/* Iframe kosong (dari components.html) yang cuma dipakai untuk
   menyuntikkan script toggle hamburger — sembunyikan visualnya */
iframe[title="st.iframe"] {{
    display: none !important;
}}

/* =====================================================
   BUTTON
===================================================== */

div[data-testid="stButton"] button {{
    border-radius: 10px !important;
    border: none !important;
    background: {PRIMARY} !important;
    color: white !important;
    font-weight: 600 !important;
    transition: .2s;
}}

div[data-testid="stButton"] button:hover {{
    background: {PRIMARY_DARK} !important;
}}

div[data-testid="stButton"] button[kind="secondary"] {{
    background: white !important;
    color: {PRIMARY} !important;
    border: 1px solid {PRIMARY} !important;
}}

div[data-testid="stButton"] button[kind="secondary"]:hover {{
    background: {PRIMARY_LIGHT} !important;
}}

/* =====================================================
   DOWNLOAD BUTTON
===================================================== */

div[data-testid="stDownloadButton"] button {{
    border-radius: 10px !important;
    border: none !important;
    background: {PRIMARY} !important;
    color: white !important;
    font-weight: 600 !important;
    transition: .2s;
}}

div[data-testid="stDownloadButton"] button:hover {{
    background: {PRIMARY_DARK} !important;
}}

/* =====================================================
   INPUT
===================================================== */

.stTextInput input,
.stTextArea textarea {{
    border-radius: 10px !important;
    border: 1px solid {BORDER} !important;
    background: white !important;
    color: {TEXT} !important;
    padding: 12px 14px !important;
}}

.stTextInput input:focus,
.stTextArea textarea:focus {{
    border: 1px solid {PRIMARY} !important;
    box-shadow: 0 0 0 3px rgba(233,30,99,.12) !important;
}}

/* =====================================================
   SELECT
===================================================== */

.stSelectbox > div > div {{
    border-radius: 10px !important;
    border: 1px solid {BORDER} !important;
}}

/* =====================================================
   METRIC
===================================================== */

div[data-testid="stMetric"] {{
    background: white;
    border: 1px solid {BORDER};
    border-radius: 14px;
    padding: 16px;
    box-shadow: 0 2px 10px rgba(0,0,0,.04);
}}

div[data-testid="stMetric"] label {{
    color: {TEXT_LIGHT};
    font-size: 12px !important;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}}

div[data-testid="stMetric"] [data-testid="stMetricValue"] {{
    color: {TEXT};
    font-weight: 700;
    font-size: 1.2rem !important;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}}

/* =====================================================
   HERO
===================================================== */

.hero {{
    background: linear-gradient(135deg, #fff0f5 0%, #ffffff 100%);
    border-radius: 18px;
    border: 1px solid {BORDER};
    padding: 30px;
    margin-bottom: 20px;
    box-shadow: 0 4px 16px rgba(0,0,0,.04);
}}

.hero h1 {{
    font-family: 'Inter', sans-serif;
    font-size: 32px;
    font-weight: 700;
    color: {TEXT};
    margin: 0 0 6px 0;
}}

.hero p {{
    color: {TEXT_LIGHT};
    margin: 0;
}}

@media (max-width: 768px) {{
    .hero {{
        padding: 20px;
    }}
    .hero h1 {{
        font-size: 24px;
    }}
}}

/* =====================================================
   CARD
===================================================== */

.dash-card,
.fav-card,
.tips-card {{
    background: white;
    border: 1px solid {BORDER};
    border-radius: 16px;
    box-shadow: 0 2px 12px rgba(0,0,0,.04);
}}

.dash-card  {{ padding: 22px; }}
.fav-card   {{ padding: 18px; }}
.tips-card  {{ padding: 18px; }}

.dash-value {{
    font-size: 36px;
    font-weight: 700;
    color: {PRIMARY};
}}

.dash-label  {{ color: {TEXT_LIGHT}; }}

.fav-title {{
    font-size: 18px;
    font-weight: 700;
    color: {TEXT};
}}

.section-title {{
    font-size: 18px;
    font-weight: 700;
    color: {TEXT};
    margin-bottom: 12px;
}}

/* =====================================================
   ALERT
===================================================== */

div[data-testid="stAlert"] {{
    border-radius: 10px;
}}

/* =====================================================
   SCROLLBAR
===================================================== */

::-webkit-scrollbar       {{ width: 6px; }}
::-webkit-scrollbar-thumb {{ background: #d1d5db; border-radius: 99px; }}
::-webkit-scrollbar-thumb:hover {{ background: #9ca3af; }}

</style>
"""

LOGIN_REGISTER_CSS = f"""
<style>

{FONT_IMPORT}

header[data-testid="stHeader"],
footer,
[data-testid="stDecoration"],
section[data-testid="stSidebar"],
[data-testid="stSidebarNav"] {{
    display: none !important;
}}

html, body, [data-testid="stAppViewContainer"], .stApp {{
    background: {BACKGROUND} !important;
    font-family: 'Inter', sans-serif;
}}

.main .block-container {{
    max-width: 440px !important;
    padding-top: 64px !important;
    padding-bottom: 40px !important;
}}

.auth-logo-wrap {{
    display: flex;
    justify-content: center;
    margin-bottom: 14px;
}}

.auth-logo-wrap img {{
    width: 88px;
    height: auto;
}}

div[data-testid="stForm"] {{
    background: {CARD};
    border: 1px solid {BORDER};
    border-radius: 16px;
    padding: 36px 34px !important;
    box-shadow: 0 8px 28px rgba(0,0,0,.06);
    animation: fadeIn .35s ease;
    margin-bottom: 0 !important;
}}

@keyframes fadeIn {{
    from {{ opacity: 0; transform: translateY(14px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
}}

.auth-title {{
    font-family: 'Inter', sans-serif;
    font-size: 26px;
    font-weight: 700;
    color: {TEXT};
    text-align: center;
    margin-bottom: 6px;
}}

.auth-subtitle {{
    font-family: 'Inter', sans-serif;
    font-size: 14px;
    color: {TEXT_LIGHT};
    text-align: center;
    line-height: 1.6;
    margin-bottom: 0;
}}

label {{
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    color: {TEXT} !important;
    font-size: 13.5px !important;
}}

.stTextInput {{ margin-bottom: 4px; }}

.stTextInput input {{
    background: white !important;
    border: 1px solid {BORDER} !important;
    border-radius: 10px !important;
    color: {TEXT} !important;
    font-size: 14.5px !important;
    padding: 11px 14px !important;
    transition: .15s;
}}

.stTextInput input:hover  {{ border-color: #d1d5db !important; }}
.stTextInput input:focus  {{ border-color: {PRIMARY} !important; box-shadow: 0 0 0 3px rgba(233,30,99,.10) !important; }}
input[type=password]      {{ letter-spacing: .03em; }}

.stCheckbox {{ margin-top: 4px; }}
.stCheckbox label {{
    color: {TEXT_LIGHT} !important;
    font-size: 13.5px !important;
    font-weight: 500 !important;
}}

div[data-testid="stFormSubmitButton"] button {{
    width: 100% !important;
    height: 44px !important;
    border-radius: 10px !important;
    border: none !important;
    background: {PRIMARY} !important;
    color: white !important;
    font-size: 14.5px !important;
    font-weight: 600 !important;
    transition: .15s;
}}

div[data-testid="stFormSubmitButton"] button:hover {{ background: {PRIMARY_DARK} !important; }}

div[data-testid="stFormSubmitButton"] button[kind="secondary"] {{
    background: transparent !important;
    color: {PRIMARY} !important;
    border: none !important;
    font-weight: 500 !important;
    height: auto !important;
    padding: 0 !important;
}}

div[data-testid="stFormSubmitButton"] button[kind="secondary"]:hover {{
    text-decoration: underline;
    background: transparent !important;
}}

div[data-testid="stButton"] button {{
    width: 100%;
    height: 42px;
    border-radius: 10px;
    font-weight: 600;
    font-size: 14px;
    transition: .15s;
}}

div[data-testid="stButton"] button[kind="secondary"] {{
    background: white !important;
    color: {PRIMARY} !important;
    border: 1px solid {BORDER} !important;
}}

div[data-testid="stButton"] button[kind="secondary"]:hover {{
    background: {PRIMARY_LIGHT} !important;
    border-color: {PRIMARY} !important;
}}

div[data-testid="stButton"] button:not([kind="secondary"]) {{
    background: {PRIMARY};
    color: white;
    border: none;
}}

div[data-testid="stButton"] button:not([kind="secondary"]):hover {{ background: {PRIMARY_DARK}; }}

.auth-divider {{
    height: 1px;
    background: {BORDER};
    margin: 22px 0;
}}

.auth-footer-text {{
    text-align: center;
    color: {TEXT_LIGHT};
    font-size: 13.5px;
    margin: 4px 0 12px 0;
}}

div[data-testid="stAlert"] {{
    border-radius: 10px !important;
    margin-bottom: 12px !important;
    font-size: 13.5px !important;
}}

div[data-testid="stSpinner"] {{ color: {PRIMARY}; }}
::placeholder {{ color: #9ca3af !important; }}

@media (max-width: 768px) {{
    .main .block-container {{ padding: 32px 16px !important; }}
    div[data-testid="stForm"] {{ padding: 26px 22px !important; }}
    .auth-title {{ font-size: 22px; }}
}}

</style>
"""

def load_css():
    st.markdown(HIDE_NAV_CSS, unsafe_allow_html=True)

def load_auth_css():
    st.markdown(LOGIN_REGISTER_CSS, unsafe_allow_html=True)

def load_background_css(bg_url):
    st.markdown(
        f"""
        <style>
        .stApp {{
            background: linear-gradient(135deg, rgba(26,5,16,0.82), rgba(107,10,42,0.75)),
                        {bg_url} !important;
            background-size: cover !important;
            background-position: center !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )