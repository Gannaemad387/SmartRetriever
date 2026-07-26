# components/sidebar.py
"""
🎨 المكون الموحد للقائمة الجانبية - Sidebar Component
يدير الثيمات (Dark/Light)، اللغات (Ar/En)، وتنسيقات الهيكل العام
"""

import streamlit as st

TRANSLATIONS = {
    "ar": {
        "home": "الصفحة الرئيسية",
        "chat": "المساعد الذكي",
        "docs": "المستندات",
        "analytics": "التحليلات",
        "theme_light": "☀️ وضع فاتح",
        "theme_dark": "🌙 وضع داكن",
        "lang_btn": "🌐 English",
        "brand_subtitle": "منصة التحليل والذكاء الاصطناعي",
        "stats_title": "📊 الإحصائيات",
        "docs_count": "المستندات",
        "suppliers_count": "الموردين",
        "contracts_count": "العقود",
        "quality_rate": "الجودة"
    },
    "en": {
        "home": "Home",
        "chat": "AI Assistant",
        "docs": "Documents",
        "analytics": "Analytics",
        "theme_light": "☀️ Light Mode",
        "theme_dark": "🌙 Dark Mode",
        "lang_btn": "🌐 العربية",
        "brand_subtitle": "AI Analytics Platform",
        "stats_title": "📊 Statistics",
        "docs_count": "Documents",
        "suppliers_count": "Suppliers",
        "contracts_count": "Contracts",
        "quality_rate": "Quality"
    }
}

def apply_dynamic_theme():
    """تطبيق الثيم وإصلاح مشاكل الـ Expander، اتجاه النصوص، والألوان"""
    is_dark = st.session_state.get("dark_mode", True)
    lang = st.session_state.get("lang", "ar")
    is_rtl = (lang == "ar")

    # 🌐 ضبط اتجاه المحاذاة حسب اللغة
    direction_css = f"""
        .stApp, [data-testid="stSidebar"], .stMarkdown, p, h1, h2, h3, h4, h5, h6 {{
            direction: {'rtl' if is_rtl else 'ltr'} !important;
            text-align: {'right' if is_rtl else 'left'} !important;
        }}
    """

    if is_dark:
        theme_css = """
            /* 1. خلفيات التطبيق والسايدبار */
            .stApp { background-color: #0B0F19 !important; color: #F8FAFC !important; }
            [data-testid="stSidebar"] { background-color: #111827 !important; border-right: 1px solid rgba(255, 255, 255, 0.08) !important; }
            [data-testid="stSidebar"] * { color: #CBD5E1 !important; }

            /* 2. الهيدر والبانر الرئيسي */
            .hero-banner {
                background: linear-gradient(135deg, #1E1B4B 0%, #0F172A 100%) !important;
                border: 1px solid rgba(56, 189, 248, 0.25) !important;
                border-radius: 16px !important;
                padding: 1.8rem !important;
                margin-bottom: 1.5rem !important;
            }
            .hero-banner h1, .hero-banner p { color: #FFFFFF !important; }

            /* 3. بطاقات الإحصائيات (Metrics Cards) */
            .metric-card {
                background: #1E293B !important;
                border: 1px solid rgba(255, 255, 255, 0.08) !important;
                border-radius: 12px !important;
                padding: 1rem !important;
                text-align: center !important;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2) !important;
            }
            .metric-value { color: #38BDF8 !important; font-size: 1.8rem !important; font-weight: 800 !important; }
            .metric-label { color: #94A3B8 !important; font-size: 0.85rem !important; font-weight: 600 !important; }

            /* 4. إصلاح مشكلة الـ Expander الأبيض في الأسفل */
            div[data-testid="stExpander"] {
                background-color: #111827 !important;
                border: 1px solid rgba(255, 255, 255, 0.1) !important;
                border-radius: 12px !important;
            }
            div[data-testid="stExpander"] details {
                background-color: #111827 !important;
                color: #F8FAFC !important;
                border-radius: 12px !important;
            }
            div[data-testid="stExpander"] summary {
                background-color: #1E293B !important;
                color: #F8FAFC !important;
                border-radius: 12px !important;
            }
            div[data-testid="stExpander"] summary:hover {
                color: #38BDF8 !important;
            }

            /* 5. الأزرار الموحدة (توحيد الأزرق/السماوي وتغطية الوردي) */
            .stButton > button[kind="primary"] {
                background: linear-gradient(90deg, #0284C7 0%, #38BDF8 100%) !important;
                color: #FFFFFF !important;
                border: none !important;
                font-weight: 700 !important;
                border-radius: 10px !important;
            }
            .stButton > button {
                background-color: #1E293B !important;
                color: #F8FAFC !important;
                border: 1px solid rgba(255, 255, 255, 0.15) !important;
                border-radius: 10px !important;
            }
        """
    else:
        theme_css = """
            .stApp { background-color: #F8FAFC !important; color: #0F172A !important; }
            [data-testid="stSidebar"] { background-color: #FFFFFF !important; border-right: 1px solid #E2E8F0 !important; }
            
            .hero-banner {
                background: linear-gradient(135deg, #EEF2FF 0%, #E0E7FF 100%) !important;
                border: 1px solid #C7D2FE !important;
                border-radius: 16px !important;
                padding: 1.8rem !important;
            }

            .metric-card {
                background-color: #FFFFFF !important;
                border: 1px solid #E2E8F0 !important;
                border-radius: 12px !important;
                padding: 1rem !important;
                text-align: center !important;
            }
            .metric-value { color: #0284C7 !important; font-size: 1.8rem !important; font-weight: 800 !important; }
            .metric-label { color: #64748B !important; font-size: 0.85rem !important; }

            div[data-testid="stExpander"] {
                background-color: #FFFFFF !important;
                border: 1px solid #E2E8F0 !important;
                border-radius: 12px !important;
            }
            div[data-testid="stExpander"] summary {
                background-color: #F1F5F9 !important;
                color: #0F172A !important;
            }
        """

    # 🛠️ إصلاح نصوص الأيقونات التي تسربت أعلى وأسفل الصفحة
    icon_fix_css = """
        /* إخفاء نصوص الأيقونات التالفة */
        header [data-testid="stHeader"] { background: transparent !important; }
    """

    st.markdown(f"<style>{direction_css}\n{theme_css}\n{icon_fix_css}</style>", unsafe_allow_html=True)

def render_sidebar(stats=None, show_theme_toggle=True, show_stats=True, show_navigation=True):
    if "dark_mode" not in st.session_state:
        st.session_state.dark_mode = True
    if "lang" not in st.session_state:
        st.session_state.lang = "ar"

    apply_dynamic_theme()
    
    lang_code = st.session_state.lang
    T = TRANSLATIONS.get(lang_code, TRANSLATIONS["ar"])

    with st.sidebar:
        st.markdown(f"""
        <div style="text-align: center; padding: 10px 0;">
            <h2 style="margin: 0; font-weight: 800; font-size: 1.4rem; color: #38BDF8;">🧠 SmartRetriever</h2>
            <span style="font-size: 0.75rem; opacity: 0.75;">{T['brand_subtitle']}</span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        if show_navigation:
            st.page_link("app.py", label=T["home"], icon="🏠")
            st.page_link("pages/1_Chat.py", label=T["chat"], icon="💬")
            st.page_link("pages/2_Documents.py", label=T["docs"], icon="📁")
            st.page_link("pages/3_Analytics.py", label=T["analytics"], icon="📊")
            st.markdown("---")

        if show_stats and stats:
            st.markdown(f"##### {T['stats_title']}")
            st.caption(f"📄 {T['docs_count']}: {stats.get('documents', 0)}")
            st.caption(f"🏢 {T['suppliers_count']}: {stats.get('suppliers', 0)}")
            st.caption(f"📝 {T['contracts_count']}: {stats.get('contracts', 0)}")
            st.caption(f"⭐ {T['quality_rate']}: {stats.get('quality', 0)}%")
            st.markdown("---")

        col_theme, col_lang = st.columns(2)

        with col_theme:
            if show_theme_toggle:
                theme_btn_label = T["theme_light"] if st.session_state.dark_mode else T["theme_dark"]
                if st.button(theme_btn_label, key="toggle_theme_btn", use_container_width=True):
                    st.session_state.dark_mode = not st.session_state.dark_mode
                    st.rerun()

        with col_lang:
            if st.button(T["lang_btn"], key="toggle_lang_btn", use_container_width=True):
                st.session_state.lang = "en" if st.session_state.lang == "ar" else "ar"
                st.rerun()

    return st.session_state.lang
