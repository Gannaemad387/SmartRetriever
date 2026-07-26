"""
📊 صفحة التحليلات والإحصائيات - Analytics Page

تعرض إحصائيات وتحليلات النظام والمستندات والموردين مع دعم الثيمين الفاتح والداكن
"""

import streamlit as st
import sys
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime
import re

# إضافة المجلد الرئيسي إلى مسار النظام
sys.path.append(str(Path(__file__).parent.parent))

from core.config import settings
from database.faiss_loader import FAISSLoader
from utils.logger import logger
from components.sidebar import render_sidebar


# ============================================================
# 🌐 قاموس اللغات لصفحة التحليلات
# ============================================================
TRANSLATIONS = {
    "ar": {
        "title": "📊 التحليلات والإحصائيات",
        "subtitle": "نظرة عامة شاملة على المستندات، الموردين، العقود وجودة البيانات",
        "docs_total": "📄 إجمالي المستندات",
        "categories_cnt": "📁 التصنيفات",
        "total_size": "💾 الحجم الإجمالي",
        "suppliers_cnt": "🏢 الموردين",
        "cat_dist": "📊 توزيع المستندات حسب التصنيف",
        "file_types": "📂 أنواع الملفات",
        "size_dist": "📊 توزيع أحجام الملفات (KB)",
        "supplier_analysis": "🏢 تحليل الموردين",
        "docs_per_supplier": "📊 عدد المستندات لكل مورد",
        "quality_analysis": "⭐ تحليل الجودة",
        "avg_quality": "📊 متوسط درجة الجودة",
        "best_supplier": "🏆 أفضل مورد",
        "quality_scores_title": "⭐ درجات الجودة لكل مورد",
        "contract_analysis": "💰 تحليل العقود",
        "contract_values_title": "💰 قيم العقود لكل مورد",
        "system_info": "⚙️ معلومات النظام",
        "paths": "📁 المسارات",
        "settings": "🔧 الإعدادات",
        "index_status": "📊 حالة الفهرس",
        "no_docs": "📭 لا توجد مستندات متاحة للتحليل حالياً"
    },
    "en": {
        "title": "📊 Analytics & Statistics",
        "subtitle": "Comprehensive overview of documents, suppliers, contracts, and data quality",
        "docs_total": "📄 Total Documents",
        "categories_cnt": "📁 Categories",
        "total_size": "💾 Total Size",
        "suppliers_cnt": "🏢 Suppliers",
        "cat_dist": "📊 Document Distribution by Category",
        "file_types": "📂 File Types",
        "size_dist": "📊 File Size Distribution (KB)",
        "supplier_analysis": "🏢 Supplier Analysis",
        "docs_per_supplier": "📊 Documents Count per Supplier",
        "quality_analysis": "⭐ Quality Analysis",
        "avg_quality": "📊 Average Quality Score",
        "best_supplier": "🏆 Top Supplier",
        "quality_scores_title": "⭐ Quality Scores by Supplier",
        "contract_analysis": "💰 Contract Analysis",
        "contract_values_title": "💰 Contract Values by Supplier",
        "system_info": "⚙️ System Information",
        "paths": "📁 Paths",
        "settings": "🔧 Settings",
        "index_status": "📊 Index Status",
        "no_docs": "📭 No documents available for analysis"
    }
}


# ============================================================
# 🎨 دالة ضبط ثيم الرسوم البيانية (Plotly Theme Adaptability)
# ============================================================
def update_chart_theme(fig, is_dark: bool):
    """تعديل ألوان الرسم البياني من Plotly ليتناسب تلقائياً مع الثيم الحالي"""
    font_color = "#FCE4EC" if is_dark else "#4A0E2E"
    grid_color = "rgba(224, 33, 138, 0.2)" if is_dark else "rgba(194, 24, 91, 0.15)"
    
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=font_color, family="Inter, system-ui, sans-serif"),
        xaxis=dict(gridcolor=grid_color, zerolinecolor=grid_color, title_font=dict(color=font_color)),
        yaxis=dict(gridcolor=grid_color, zerolinecolor=grid_color, title_font=dict(color=font_color)),
        legend=dict(font=dict(color=font_color)),
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig


# ============================================================
# 1. دوال استخراج واستعلام البيانات
# ============================================================

def get_documents_stats():
    """الحصول على إحصائيات المستندات والمجلدات"""
    kb_path = settings.KNOWLEDGE_BASE_PATH
    stats = {
        "total": 0,
        "by_category": {},
        "file_types": {},
        "total_size": 0,
        "documents": []
    }
    
    if not kb_path.exists():
        return stats
    
    for category_dir in kb_path.iterdir():
        if category_dir.is_dir():
            count = 0
            for file_path in category_dir.glob("*"):
                if file_path.is_file():
                    count += 1
                    ext = file_path.suffix.lower()
                    stats["file_types"][ext] = stats["file_types"].get(ext, 0) + 1
                    stats["total_size"] += file_path.stat().st_size
                    stats["documents"].append({
                        "filename": file_path.name,
                        "category": category_dir.name,
                        "size": file_path.stat().st_size,
                        "modified": datetime.fromtimestamp(file_path.stat().st_mtime)
                    })
            stats["by_category"][category_dir.name] = count
            stats["total"] += count
    
    return stats


def get_suppliers_from_filenames(documents):
    """استخراج أسماء الموردين والإحصائيات المرتبطة بهم"""
    suppliers = {}
    patterns = [
        r'Supplier_([A-Za-z]+)',
        r'Supplier_([A-Za-z]+_[A-Za-z]+)',
        r'([A-Za-z]+_Inc)',
        r'([A-Za-z]+_Supplies)',
        r'([A-Za-z]+_Logistics)',
        r'([A-Za-z]+_Group)',
        r'([A-Za-z]+_Co)',
    ]
    
    for doc in documents:
        filename = doc["filename"]
        for pattern in patterns:
            match = re.search(pattern, filename)
            if match:
                supplier = match.group(1).replace('_', ' ')
                if supplier not in suppliers:
                    suppliers[supplier] = {
                        "name": supplier,
                        "documents": 0,
                        "categories": set(),
                        "total_size": 0
                    }
                suppliers[supplier]["documents"] += 1
                suppliers[supplier]["categories"].add(doc["category"])
                suppliers[supplier]["total_size"] += doc["size"]
                break
    
    return [{"name": k, **v} for k, v in suppliers.items()]


def get_quality_scores(documents):
    """استخراج تقييمات الجودة المتاحة من أسماء الملفات"""
    scores = []
    for doc in documents:
        if "quality" in doc["category"].lower() or "quality" in doc["filename"].lower():
            match = re.search(r'(\d+)', doc["filename"])
            if match:
                score = int(match.group(1))
                if score <= 100:
                    supplier_name = doc["filename"].replace('_Quality_Report_', '').replace('.docx', '')
                    supplier_name = re.sub(r'^\d+_', '', supplier_name)
                    scores.append({
                        "supplier": supplier_name,
                        "score": score,
                        "category": doc["category"]
                    })
    return scores


def get_contract_values(documents):
    """استخراج قيم العقود المالية المتاحة"""
    contracts = []
    for doc in documents:
        if "contract" in doc["category"].lower() or "contract" in doc["filename"].lower():
            match = re.search(r'(\d+[,\d]*\.?\d*)', doc["filename"])
            if match:
                try:
                    value_str = match.group(1).replace(',', '')
                    value = float(value_str)
                    if value > 1000:
                        supplier_name = doc["filename"].replace('_Supplier_Contract_', '').replace('.docx', '')
                        supplier_name = re.sub(r'^\d+_', '', supplier_name)
                        contracts.append({
                            "supplier": supplier_name,
                            "value": value,
                            "category": doc["category"]
                        })
                except Exception:
                    pass
    return contracts


# ============================================================
# 🎨 CSS مخصص لصفحة التحليلات (Barbie Colors)
# ============================================================
def load_analytics_css():
    """تحميل تنسيقات Barbie Colors لصفحة التحليلات"""
    st.markdown("""
        <style>
        /* 🚫 إخفاء قائمة التنقل الافتراضية */
        [data-testid="stSidebarNav"] {
            display: none !important;
        }

        /* 🎨 Barbie Colors */
        :root {
            --bg-primary: #FCE4EC;
            --bg-secondary: #FFFFFF;
            --primary: #E0218A;
            --primary-dark: #C2185B;
            --text-primary: #4A0E2E;
            --text-secondary: #C2185B;
            --shadow: rgba(224, 33, 138, 0.2);
        }

        /* خلفية التطبيق */
        .stApp {
            background-color: #FCE4EC !important;
        }

        /* الهيدر */
        .doc-header {
            background: linear-gradient(135deg, #FCE4EC 0%, #E0218A 100%) !important;
            border: 2px solid #C2185B !important;
            border-radius: 14px;
            padding: 18px 24px;
            margin-bottom: 20px;
            box-shadow: 0 4px 20px rgba(224, 33, 138, 0.2);
        }
        .doc-header h2 {
            color: #FFFFFF !important;
            font-weight: 800;
            font-size: 1.6rem;
            margin: 0 0 6px 0;
        }
        .doc-header p {
            color: #FFFFFF !important;
            font-size: 0.9rem;
            margin: 0;
            opacity: 0.9;
        }

        /* بطاقات الإحصائيات */
        div[data-testid="stMetric"] {
            background: #FFFFFF !important;
            border: 2px solid #E0218A !important;
            border-radius: 12px !important;
            padding: 12px !important;
            box-shadow: 0 2px 10px rgba(224, 33, 138, 0.08);
        }
        div[data-testid="stMetricValue"] {
            color: #E0218A !important;
        }
        div[data-testid="stMetricLabel"] {
            color: #4A0E2E !important;
        }

        /* النصوص */
        h1, h2, h3, h4, h5, h6, p, span, label, div {
            color: #4A0E2E !important;
        }
        .stSubheader {
            color: #E0218A !important;
        }

        /* DataFrames */
        .stDataFrame {
            border: 2px solid #E0218A !important;
            border-radius: 12px !important;
            overflow: hidden;
        }
        .stDataFrame thead {
            background: #E0218A !important;
            color: #FFFFFF !important;
        }

        /* التوسعات */
        .stExpander {
            background: #FFFFFF !important;
            border: 2px solid #E0218A !important;
            border-radius: 12px !important;
            box-shadow: 0 2px 10px rgba(224, 33, 138, 0.08);
        }

        /* المقسّم */
        hr {
            border-color: #E0218A !important;
            opacity: 0.3;
        }

        /* صناديق المعلومات */
        .stAlert {
            border-radius: 12px !important;
            border: 2px solid #E0218A !important;
        }

        /* الكود */
        .stCodeBlock {
            border: 2px solid #E0218A !important;
            border-radius: 8px !important;
        }
        </style>
    """, unsafe_allow_html=True)


# ============================================================
# 2. عرض واجهة الصفحة (Show Page)
# ============================================================

def show():
    """عرض صفحة التحليلات مع التوافق التام مع الثيم الفاتح والداكن"""
    
    # تحميل CSS الخاص بالصفحة
    load_analytics_css()
    
    # 1. جلب البيانات الأساسية أولاً
    stats = get_documents_stats()
    documents = stats["documents"]
    suppliers = get_suppliers_from_filenames(documents)
    quality_scores = get_quality_scores(documents)
    
    avg_quality_val = round(sum(s["score"] for s in quality_scores) / len(quality_scores), 1) if quality_scores else 0

    # 2. عرض الشريط الجانبي وجلب اللغة الثابتة
    sidebar_stats = {
        "documents": stats["total"],
        "suppliers": len(suppliers),
        "contracts": len(get_contract_values(documents)),
        "quality": avg_quality_val
    }
    lang_code = render_sidebar(stats=sidebar_stats)
    T = TRANSLATIONS.get(lang_code, TRANSLATIONS["ar"])
    
    # 3. تحديد هل التطبيق في الوضع الداكن؟
    is_dark = st.session_state.get("dark_mode", False)

    # 4. الترويسة الرئيسية
    st.markdown(f"""
    <div class="doc-header">
        <h2>{T['title']}</h2>
        <p>{T['subtitle']}</p>
    </div>
    """, unsafe_allow_html=True)

    # ============================================================
    # 5. كروت الإحصائيات الرئيسية (Metrics Cards)
    # ============================================================
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(T["docs_total"], stats["total"], delta="+2" if stats["total"] > 0 else "0")
    with col2:
        st.metric(T["categories_cnt"], len(stats["by_category"]))
    with col3:
        total_size_mb = stats["total_size"] / (1024 * 1024)
        st.metric(T["total_size"], f"{total_size_mb:.1f} MB")
    with col4:
        st.metric(T["suppliers_cnt"], len(suppliers))

    st.markdown("---")

    # ============================================================
    # 6. الرسوم البيانية المتوافقة مع الثيم
    # ============================================================
    
    # 6.1 توزيع المستندات حسب التصنيف
    if stats["by_category"]:
        df_categories = pd.DataFrame({
            "التصنيف": list(stats["by_category"].keys()),
            "العدد": list(stats["by_category"].values())
        })
        
        fig1 = px.pie(
            df_categories,
            names="التصنيف",
            values="العدد",
            title=f"<b>{T['cat_dist']}</b>",
            color_discrete_sequence=["#E0218A", "#C2185B", "#F8BBD0", "#4A0E2E", "#FCE4EC"],
            hole=0.4
        )
        fig1 = update_chart_theme(fig1, is_dark)
        fig1.update_layout(height=380, showlegend=True, legend=dict(orientation="h", y=-0.1))
        st.plotly_chart(fig1, use_container_width=True)
    else:
        st.info(T["no_docs"])

    # 6.2 أنواع الملفات وتوزيع الأحجام
    if stats["file_types"]:
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            df_filetypes = pd.DataFrame({
                "نوع الملف": list(stats["file_types"].keys()),
                "العدد": list(stats["file_types"].values())
            })
            fig2 = px.bar(
                df_filetypes,
                x="نوع الملف",
                y="العدد",
                title=f"<b>{T['file_types']}</b>",
                color_discrete_sequence=["#E0218A"]
            )
            fig2 = update_chart_theme(fig2, is_dark)
            fig2.update_layout(height=320)
            st.plotly_chart(fig2, use_container_width=True)
        
        with col_chart2:
            if documents:
                sizes = [doc["size"] / 1024 for doc in documents]
                df_sizes = pd.DataFrame({"الحجم (KB)": sizes})
                fig3 = px.histogram(
                    df_sizes,
                    x="الحجم (KB)",
                    title=f"<b>{T['size_dist']}</b>",
                    nbins=10,
                    color_discrete_sequence=["#C2185B"]
                )
                fig3 = update_chart_theme(fig3, is_dark)
                fig3.update_layout(height=320)
                st.plotly_chart(fig3, use_container_width=True)

    st.markdown("---")

    # ============================================================
    # 7. قسم الموردين (Suppliers Section)
    # ============================================================
    if suppliers:
        st.subheader(T["supplier_analysis"])
        
        suppliers_df = pd.DataFrame([
            {
                "المورد": s["name"],
                "المستندات": s["documents"],
                "التصنيفات": ", ".join(s["categories"]),
                "الحجم (KB)": f"{s['total_size'] / 1024:.1f}"
            }
            for s in suppliers
        ])
        
        st.dataframe(
            suppliers_df,
            use_container_width=True,
            hide_index=True
        )
        
        fig4 = px.bar(
            suppliers_df,
            x="المورد",
            y="المستندات",
            title=f"<b>{T['docs_per_supplier']}</b>",
            color_discrete_sequence=["#E0218A"]
        )
        fig4 = update_chart_theme(fig4, is_dark)
        fig4.update_layout(height=340)
        st.plotly_chart(fig4, use_container_width=True)

    # ============================================================
    # 8. قسم الجودة (Quality Metrics)
    # ============================================================
    if quality_scores:
        st.markdown("---")
        st.subheader(T["quality_analysis"])
        
        scores_df = pd.DataFrame(quality_scores)
        col_q1, col_q2 = st.columns(2)
        
        with col_q1:
            st.metric(
                T["avg_quality"],
                f"{avg_quality_val}%",
                delta="+5%" if avg_quality_val > 80 else "0%"
            )
        
        with col_q2:
            best = max(quality_scores, key=lambda x: x["score"])
            st.metric(
                T["best_supplier"],
                best["supplier"],
                delta=f"{best['score']}%"
            )
        
        fig5 = px.bar(
            scores_df,
            x="supplier",
            y="score",
            title=f"<b>{T['quality_scores_title']}</b>",
            labels={"supplier": "المورد", "score": "درجة الجودة (%)"},
            color="score",
            color_continuous_scale=["#FCE4EC", "#E0218A", "#C2185B"],
            range_color=[0, 100]
        )
        fig5 = update_chart_theme(fig5, is_dark)
        fig5.update_layout(height=340)
        st.plotly_chart(fig5, use_container_width=True)

    # ============================================================
    # 9. قسم العقود (Contracts Section)
    # ============================================================
    contracts = get_contract_values(documents)
    if contracts:
        st.markdown("---")
        st.subheader(T["contract_analysis"])
        
        contracts_df = pd.DataFrame([
            {
                "المورد": c["supplier"],
                "القيمة (SAR)": c["value"],
                "التصنيف": c["category"]
            }
            for c in contracts
        ]).sort_values("القيمة (SAR)", ascending=False)
        
        st.dataframe(contracts_df, use_container_width=True, hide_index=True)
        
        fig6 = px.bar(
            contracts_df,
            x="المورد",
            y="القيمة (SAR)",
            title=f"<b>{T['contract_values_title']}</b>",
            color_discrete_sequence=["#E0218A"]
        )
        fig6 = update_chart_theme(fig6, is_dark)
        fig6.update_layout(height=340)
        st.plotly_chart(fig6, use_container_width=True)

    # ============================================================
    # 10. معلومات وإعدادات النظام
    # ============================================================
    st.markdown("---")
    with st.expander(T["system_info"], expanded=False):
        col_sys1, col_sys2 = st.columns(2)
        
        with col_sys1:
            st.markdown(f"**{T['paths']}:**")
            st.code(f"KNOWLEDGE_BASE: {settings.KNOWLEDGE_BASE_PATH}")
            st.code(f"FAISS_INDEX: {settings.FAISS_INDEX_PATH}")
            st.code(f"DATA_PATH: {settings.DATA_PATH}")
        
        with col_sys2:
            st.markdown(f"**{T['settings']}:**")
            st.code(f"MODEL: {settings.EMBEDDING_MODEL}")
            st.code(f"DEVICE: {settings.EMBEDDING_DEVICE}")
            st.code(f"DIMENSION: {settings.EMBEDDING_DIMENSION}")
        
        st.markdown(f"**{T['index_status']}:**")
        try:
            loader = FAISSLoader()
            index_info = loader.get_index_info()
            st.code(f"Status: {index_info.get('status', 'Unknown')} | Total Vectors: {index_info.get('total_vectors', 0)}")
        except Exception as e:
            st.warning(f"⚠️ Index Loader Warning: {str(e)}")


# ============================================================
# 3. تشغيل الصفحة عند الاستدعاء المباشر
# ============================================================
if __name__ == "__main__":
    show()
