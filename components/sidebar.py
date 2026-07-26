# components/sidebar.py
"""
🎨 المكون الموحد للقائمة الجانبية - Sidebar Component
يدير الثيمات (Dark/Light)، اللغات (Ar/En)، والتنقل بين صفحات المنصة
"""

import streamlit as st
from pathlib import Path

# ============================================================
# 🌐 قاموس اللغات (Translations Dictionary)
# ============================================================
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


# ============================================================
# 🎨 تطبيق التنسيق الديناميكي للثيم والاتجاه (RTL / LTR)
# ============================================================
def apply_dynamic_theme():
    """تطبيق الثيم (فاتح/داكن) مع ضبط الاتجاه (RTL/LTR) وتباين الألوان لكافة العناصر"""
    
    is_dark = st.session_state.get("dark_mode", True)
    lang = st.session_state.get("lang", "ar")
    is_rtl = (lang == "ar")

    # قاعدة اتجاه النص والواجهة
    direction_css = """
        .stApp, [data-testid="stSidebar"] {
            direction: rtl !important;
            text-align: right !important;
        }
    """ if is_rtl else """
        .stApp, [data-testid="stSidebar"] {
            direction: ltr !important;
            text-align: left !important;
        }
    """

    if is_dark:
        # 🌙 الوضع الداكن (Dark Mode)
        theme_css = """
            /* خلفية التطبيق والسايدبار */
            .stApp { background-color: #0B0F19 !important; color: #F8FAFC !important; }
            [data-testid="stSidebar"] { background-color: #111827 !important; border-right: 1px solid rgba(255, 255, 255, 0.08) !important; }
            [data-testid="stSidebar"] * { color: #CBD5E1 !important; }
            
            /* الهيدر والبانر الرئيسي */
            .doc-header, .chat-header, .hero-banner {
                background: linear-gradient(135deg, #1E1B4B 0%, #0F172A 100%) !important;
                border: 1px solid rgba(99, 102, 241, 0.3) !important;
                color: #FFFFFF !important;
            }
            .doc-header h2, .doc-header p, .chat-header h2, .chat-header p, .hero-banner h1, .hero-banner p { 
                color: #FFFFFF !important; 
            }

            /* بطاقات الإحصائيات والكروت */
            .metric-card, .doc-card, div[data-testid="stMetric"] {
                background-color: #1E293B !important;
                border: 1px solid rgba(255, 255, 255, 0.08) !important;
                border-radius: 12px !important;
                padding: 12px !important;
            }
            div[data-testid="stMetricValue"] { color: #38BDF8 !important; }
            div[data-testid="stMetricLabel"] { color: #94A3B8 !important; }

            /* المدخلات والقوائم المنسدلة */
            .stTextInput input, div[data-baseweb="select"] > div {
                background-color: #182232 !important;
                color: #FFFFFF !important;
                border-color: rgba(255, 255, 255, 0.1) !important;
            }
            
            /* الأزرار العامة */
            .stButton > button {
                background-color: #1E293B !important;
                color: #F8FAFC !important;
                border: 1px solid rgba(255, 255, 255, 0.15) !important;
            }
            .stButton > button:hover {
                border-color: #38BDF8 !important;
                color: #38BDF8 !important;
            }
        """
    else:
        # ☀️ الوضع الفاتح (Light Mode)
        theme_css = """
            /* خلفية التطبيق والسايدبار */
            .stApp { background-color: #F8FAFC !important; color: #0F172A !important; }
            [data-testid="stSidebar"] { background-color: #FFFFFF !important; border-right: 1px solid #E2E8F0 !important; }
            [data-testid="stSidebar"] * { color: #334155 !important; }

            /* الهيدر والبانر الرئيسي */
            .doc-header, .chat-header, .hero-banner {
                background: linear-gradient(135deg, #EEF2FF 0%, #E0E7FF 100%) !important;
                border: 1px solid #C7D2FE !important;
                color: #1E1B4B !important;
            }
            .doc-header h2, .chat-header h2, .hero-banner h1 { color: #1E1B4B !important; }
            .doc-header p, .chat-header p, .hero-banner p { color: #3730A3 !important; }

            /* بطاقات الإحصائيات والكروت */
            .metric-card, .doc-card, div[data-testid="stMetric"] {
                background-color: #FFFFFF !important;
                border: 1px solid #E2E8F0 !important;
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.03) !important;
                border-radius: 12px !important;
                padding: 12px !important;
            }
            div[data-testid="stMetricValue"] { color: #0284C7 !important; }
            div[data-testid="stMetricLabel"] { color: #64748B !important; }

            /* المدخلات والقوائم المنسدلة */
            .stTextInput input, div[data-baseweb="select"] > div {
                background-color: #FFFFFF !important;
                color: #0F172A !important;
                border-color: #CBD5E1 !important;
            }

            /* الأزرار العامة */
            .stButton > button {
                background-color: #FFFFFF !important;
                color: #1E293B !important;
                border: 1px solid #CBD5E1 !important;
            }
            .stButton > button:hover {
                background-color: #F1F5F9 !important;
                border-color: #0284C7 !important;
                color: #0284C7 !important;
            }

            /* استهداف محدد ومريح للعناوين والنصوص */
            .stMarkdown, .stMarkdown p, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4 {
                color: #0F172A !important;
            }
        """

    # دمج التنسيقات وحقنها
    st.markdown(f"<style>{direction_css}\n{theme_css}</style>", unsafe_allow_html=True)


# ============================================================
# 🖥️ المكون الرئيسي للسايدبار (Render Sidebar)
# ============================================================
def render_sidebar(stats=None, show_theme_toggle=True, show_stats=True, show_navigation=True):
    """عرض القائمة الجانبية الموحدة للتطبيق وترجيع رمز اللغة الحالي"""
    
    # 1. تهيئة حالة الجلسة للثيم واللغة
    if "dark_mode" not in st.session_state:
        st.session_state.dark_mode = True
    if "lang" not in st.session_state:
        st.session_state.lang = "ar"

    # 2. تطبيق الثيم والاتجاه الديناميكي
    apply_dynamic_theme()
    
    # 3. جلب النصوص المترجمة
    lang_code = st.session_state.lang
    T = TRANSLATIONS.get(lang_code, TRANSLATIONS["ar"])

    with st.sidebar:
        # 🏷️ الهوية واللوجو
        st.markdown(f"""
        <div style="text-align: center; padding: 10px 0 15px 0;">
            <h2 style="margin: 0; font-weight: 800; font-size: 1.4rem;">🧠 SmartRetriever</h2>
            <span style="font-size: 0.75rem; opacity: 0.75;">{T['brand_subtitle']}</span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # 🔀 التنقل الفوري بين الصفحات
        if show_navigation:
            st.page_link("app.py", label=T["home"], icon="🏠")
            st.page_link("pages/1_Chat.py", label=T["chat"], icon="💬")
            st.page_link("pages/2_Documents.py", label=T["docs"], icon="📁")
            st.page_link("pages/3_Analytics.py", label=T["analytics"], icon="📊")
            st.markdown("---")

        # 📊 عرض الإحصائيات (إن وجدت)
        if show_stats and stats:
            st.markdown(f"##### {T['stats_title']}")
            st.caption(f"📄 {T['docs_count']}: {stats.get('documents', 0)}")
            st.caption(f"🏢 {T['suppliers_count']}: {stats.get('suppliers', 0)}")
            st.caption(f"📝 {T['contracts_count']}: {stats.get('contracts', 0)}")
            st.caption(f"⭐ {T['quality_rate']}: {stats.get('quality', 0)}%")
            st.markdown("---")

        # ⚙️ أزرار التحكم بالثيم واللغة
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

        # 🔗 روابط التواصل والتوثيق السفليّة
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div style="font-size: 0.75rem; text-align: center; opacity: 0.7;">
            📦 SmartRetriever · 2026<br>
            <a href="https://github.com" target="_blank" style="color: #38BDF8; text-decoration: none;">GitHub</a> | 
            <a href="https://linkedin.com" target="_blank" style="color: #38BDF8; text-decoration: none;">LinkedIn</a>
        </div>
        """, unsafe_allow_html=True)

    return st.session_state.lang
