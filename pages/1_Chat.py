"""
💬 صفحة المحادثة الذكية - SmartRetriever Auto Chat
تتيح للمستخدم التفاعل المباشر مع الذكاء الاصطناعي واسترجاع المستندات.
"""

import streamlit as st
import sys
import uuid
from pathlib import Path

# إضافة المجلد الرئيسي للتطبيق إلى المسار
sys.path.append(str(Path(__file__).parent.parent))

from components.sidebar import render_sidebar
from services.chat_service import ChatService
from components.chat_utils import render_sources, render_error
from core.config import settings
from utils.logger import logger

# ============================================================
# ⚙️ إعدادات الصفحة
# ============================================================
st.set_page_config(
    page_title="المساعد الذكي | SmartRetriever Auto",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# 🎨 تحميل التنسيقات المخصصة (Barbie Edition Fixes)
# ============================================================
def load_css():
    """تحميل تنسيقات الواجهة وإخفاء القائمة الجانبية الافتراضية مع تطبيق ثيم Barbie"""
    st.markdown("""
        <style>
        /* 🚫 إخفاء قائمة التنقل الافتراضية التي يولدها Streamlit */
        [data-testid="stSidebarNav"] {
            display: none !important;
        }

        /* 🌸 تحسين هيدر المحادثة ليتوافق مع ثيم Barbie */
        .chat-header {
            background: linear-gradient(135deg, #FFFFFF 0%, #FCE4EC 100%) !important;
            border: 2px solid #F48FB1 !important;
            border-radius: 16px !important;
            padding: 1.2rem 1.5rem !important;
            margin-bottom: 1.5rem !important;
            box-shadow: 0 4px 15px rgba(224, 33, 138, 0.1) !important;
        }

        .chat-header h2 {
            color: #E0218A !important;
            font-weight: 800 !important;
            margin: 0 0 6px 0 !important;
        }

        .chat-header p {
            color: #4A0E2E !important;
            font-size: 0.95rem !important;
            margin: 0 !important;
        }

        /* 📌 أزرار الأسئلة المقترحة (Barbie Style) */
        div[data-testid="stColumn"] div.stButton > button {
            background: #FFFFFF !important;
            border: 2px solid #F48FB1 !important;
            color: #4A0E2E !important;
            border-radius: 12px !important;
            padding: 0.6rem 0.8rem !important;
            font-size: 0.9rem !important;
            font-weight: 600 !important;
            text-align: right !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 2px 8px rgba(224, 33, 138, 0.05) !important;
        }
        
        div[data-testid="stColumn"] div.stButton > button:hover {
            border-color: #E0218A !important;
            color: #E0218A !important;
            background: #FCE4EC !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 4px 12px rgba(224, 33, 138, 0.2) !important;
        }
        </style>
    """, unsafe_allow_html=True)

    css_file = Path(__file__).parent.parent / "styles" / "custom.css"
    if css_file.exists():
        with open(css_file, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# ============================================================
# 1. تهيئة خدمة المحادثة
# ============================================================
@st.cache_resource
def get_chat_service():
    """تهيئة خدمة المحادثة (مرة واحدة)"""
    return ChatService()

chat_service = get_chat_service()


# ============================================================
# 2. تهيئة حالة الجلسة (Session State)
# ============================================================
def init_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    if "pending_question" not in st.session_state:
        st.session_state.pending_question = None
    if "current_page" not in st.session_state:
        st.session_state.current_page = "المساعد الذكي"


# ============================================================
# 🔀 التوجيه بين الصفحات
# ============================================================
def handle_routing(selected_page: str):
    """ربط التنقل بين الصفحات"""
    page_routes = {
        "HOME": "app.py",
        "المستندات": "pages/2_Documents.py",
        "التحليلات": "pages/3_Analytics.py",
    }
    if selected_page in page_routes:
        target_file = page_routes[selected_page]
        if Path(target_file).exists():
            st.switch_page(target_file)


# ============================================================
# 3. عرض سوابق المحادثة
# ============================================================
def display_messages():
    """عرض كافة الرسائل السابقة والمصادر"""
    for message in st.session_state.messages:
        role = message.get("role", "user")
        content = message.get("content", "")
        sources = message.get("sources", [])
        
        with st.chat_message(role):
            st.markdown(content)
            
            # عرض المصادر لردود المساعد
            if sources and role == "assistant":
                render_sources(sources)


# ============================================================
# 4. معالجة سؤال المستخدم
# ============================================================
def process_question(question: str):
    """معالجة السؤال واستدعاء الخدمة مع حفظ النتيجة"""
    if not question.strip():
        return

    # 1. إضافة وعرض سؤال المستخدم
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    # 2. توليد وعرض رد المساعد الذكي
    with st.chat_message("assistant"):
        with st.spinner("🤔 جاري البحث في المستندات واستخلاص الإجابة..."):
            try:
                response = chat_service.process_question_sync(
                    question=question,
                    session_id=st.session_state.session_id
                )
                
                # تحديث معرف الجلسة إن وجد
                if response.get("session_id"):
                    st.session_state.session_id = response["session_id"]
                
                answer = response.get("answer", "لم أتمكن من الحصول على إجابة.")
                sources = response.get("sources", [])
                
                # عرض الإجابة والمصادر
                st.markdown(answer)
                if sources:
                    render_sources(sources)
                
                # حفظ الرد في حالة الجلسة
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "sources": sources
                })
                
            except Exception as e:
                error_msg = f"❌ حدث خطأ أثناء معالجة الطلب: {str(e)}"
                st.error(error_msg)
                logger.error(f"Chat error: {str(e)}")
                
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg,
                    "sources": []
                })


# ============================================================
# 5. عرض الأسئلة المقترحة
# ============================================================
def display_suggested_questions():
    """عرض اقتراحات الأسئلة فقط عند بداية المحادثة"""
    if len(st.session_state.messages) > 0:
        return

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<h5 style='color: #4A0E2E; font-weight: 700;'>💡 أسئلة مقترحة للبدء:</h5>", unsafe_allow_html=True)

    suggestions = [
        "ما هي شروط عقد Alpha Inc؟",
        "مين أفضل مورد حسب تقارير الجودة؟",
        "إيه سياسة تقييم الموردين المعتمدة؟",
        "قارن بين عروض أسعار Alpha Inc و Beta Supplies",
        "ما هي تفاصيل وقيمة عقد Gamma Co؟",
        "ملخص تقرير جودة Delta Logistics"
    ]

    cols = st.columns(2)
    for i, suggestion in enumerate(suggestions):
        with cols[i % 2]:
            if st.button(f"📌 {suggestion}", use_container_width=True, key=f"suggest_{i}"):
                st.session_state.pending_question = suggestion
                st.rerun()


# ============================================================
# 6. الصفحة الرئيسية للمحادثة
# ============================================================
def show():
    """عرض الواجهة الكلية لصفحة المحادثة"""
    load_css()
    init_session_state()

    # ✅ 1. عرض السايدبار والتنقل
    st.session_state.current_page = "المساعد الذكي"
    selected_page = render_sidebar(
        show_theme_toggle=True,
        show_stats=False,
        show_navigation=True
    )
    
    # تحويل الصفحة في حال اضغط المستخدم على زر آخر بالسايدبار
    if selected_page != "المساعد الذكي":
        handle_routing(selected_page)

    # ✅ 2. الهيدر والتحكم
    col_title, col_actions = st.columns([3, 1.5])
    
    with col_title:
        st.markdown("""
        <div class="chat-header">
            <h2>💬 المساعد الذكي (SmartRetriever)</h2>
            <p>طرح الأسئلة والبحث التفاعلي في العقود، السياسات، والمستندات المخزنة.</p>
        </div>
        """, unsafe_allow_html=True)

    with col_actions:
        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        ac1, ac2 = st.columns(2)
        with ac1:
            if st.button("🗑️ مسح", use_container_width=True, help="مسح سجل المحادثة الحالي"):
                st.session_state.messages = []
                st.session_state.session_id = str(uuid.uuid4())
                st.rerun()
        with ac2:
            if st.button("🔄 تحديث", use_container_width=True, help="تحديث الصفحة"):
                st.rerun()

    st.markdown("---")

    # ✅ 3. عرض سجل الرسائل
    display_messages()

    # ✅ 4. معالجة الأسئلة المجهزة أو المدخلة من مربع النص
    query_to_process = None

    # إذا كان هناك سؤال معلق من الأزرار المقترحة
    if st.session_state.pending_question:
        query_to_process = st.session_state.pending_question
        st.session_state.pending_question = None

    # مدخل النص الأساسي
    elif prompt := st.chat_input("اكتب سؤالك هنا عن المستندات أو العقود..."):
        query_to_process = prompt

    # معالجة السؤال إذا وجد
    if query_to_process:
        process_question(query_to_process)
        st.rerun()

    # ✅ 5. عرض الأسئلة المقترحة (في حال لا توجد رسائل بعد)
    display_suggested_questions()


# ============================================================
# 🚀 تشغيل الصفحة
# ============================================================
if __name__ == "__main__":
    show()
