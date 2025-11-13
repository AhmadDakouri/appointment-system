import streamlit as st
import datetime
import pandas as pd
from datetime import datetime as dt

# إعدادات الصفحة
st.set_page_config(
    page_title="نظام حجز المواعيد",
    page_icon="📅",
    layout="wide"
)

# عنوان الصفحة
st.title("📅 نظام حجز المواعيد")
st.markdown("---")

# تهيئة البيانات في حالة الجلسة
if 'appointments' not in st.session_state:
    st.session_state.appointments = {}

if 'appointments_df' not in st.session_state:
    st.session_state.appointments_df = pd.DataFrame(columns=[
        'اسم_العميل', 'الهاتف', 'التاريخ', 'الوقت', 'الخدمة', 'ملاحظات', 'حالة'
    ])

def حجز_موعد():
    st.subheader("📅 حجز موعد جديد")
    
    with st.form("حجز_موعد", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            اسم_العميل = st.text_input("👤 اسم العميل *")
            تاريخ = st.date_input("📅 التاريخ *", min_value=datetime.date.today())
            خدمة = st.selectbox("🛠️ نوع الخدمة *", ["استشارة", "فحص", "علاج", "متابعة", "أخرى"])
        
        with col2:
            هاتف = st.text_input("📞 رقم الهاتف *")
            وقت = st.time_input("⏰ الوقت *")
            ملاحظات = st.text_area("📝 ملاحظات إضافية")
        
        submitted = st.form_submit_button("✅ حجز الموعد")
        
        if submitted:
            if اسم_العميل and هاتف and وقت:
                مفتاح_الموعد = f"{تاريخ}_{وقت}"
                
                if مفتاح_الموعد in st.session_state.appointments:
                    st.error("⏰ هذا الموعد محجوز مسبقاً، يرجى اختيار وقت آخر.")
                else:
                    # حفظ في session state
                    st.session_state.appointments[مفتاح_الموعد] = {
                        "اسم_العميل": اسم_العميل,
                        "الهاتف": هاتف,
                        "التاريخ": str(تاريخ),
                        "الوقت": str(وقت),
                        "الخدمة": خدمة,
                        "ملاحظات": ملاحظات,
                        "حالة": "مؤكد"
                    }
                    
                    # حفظ في DataFrame
                    new_appointment = pd.DataFrame([{
                        'اسم_العميل': اسم_العميل,
                        'الهاتف': هاتف,
                        'التاريخ': str(تاريخ),
                        'الوقت': str(وقت),
                        'الخدمة': خدمة,
                        'ملاحظات': ملاحظات,
                        'حالة': 'مؤكد'
                    }])
                    
                    st.session_state.appointments_df = pd.concat(
                        [st.session_state.appointments_df, new_appointment], 
                        ignore_index=True
                    )
                    
                    st.success(f"✅ تم حجز الموعد بنجاح للعميل **{اسم_العميل}**")
                    st.balloons()
            else:
                st.warning("⚠️ يرجى ملء جميع الحقول المطلوبة")

def عرض_المواعيد():
    st.subheader("📋 المواعيد المحجوزة")
    
    if st.session_state.appointments_df.empty:
        st.info("📭 لا توجد مواعيد محجوزة حالياً.")
        return
    
    # عرض الجدول
    st.dataframe(
        st.session_state.appointments_df,
        use_container_width=True,
        hide_index=True
    )
    
    # خيارات الإدارة
    st.subheader("🛠️ إدارة المواعيد")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 تحديث القائمة"):
            st.rerun()
    
    with col2:
        if st.button("🗑️ مسح جميع المواعيد"):
            st.session_state.appointments = {}
            st.session_state.appointments_df = pd.DataFrame(columns=[
                'اسم_العميل', 'الهاتف', 'التاريخ', 'الوقت', 'الخدمة', 'ملاحظات', 'حالة'
            ])
            st.success("✅ تم مسح جميع المواعيد")
            st.rerun()

def البحث_عن_موعد():
    st.subheader("🔍 البحث عن موعد")
    
    بحث = st.text_input("أدخل اسم العميل أو رقم الهاتف للبحث")
    
    if بحث:
        نتائج = st.session_state.appointments_df[
            (st.session_state.appointments_df['اسم_العميل'].str.contains(بحث, case=False, na=False)) |
            (st.session_state.appointments_df['الهاتف'].str.contains(بحث, na=False))
        ]
        
        if not نتائج.empty:
            st.success(f"🎯 تم العثور على {len(نتائج)} موعد")
            st.dataframe(نتائج, use_container_width=True, hide_index=True)
        else:
            st.warning("❌ لم يتم العثور على أي موعد مطابق للبحث")

def عرض_الإحصائيات():
    st.subheader("📊 إحصائيات المواعيد")
    
    if st.session_state.appointments_df.empty:
        st.info("📊 لا توجد بيانات لعرض الإحصائيات")
        return
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total = len(st.session_state.appointments_df)
        st.metric("إجمالي المواعيد", total)
    
    with col2:
        # المواعيد القادمة
        today = datetime.date.today()
        upcoming = len(st.session_state.appointments_df[
            st.session_state.appointments_df['التاريخ'] >= str(today)
        ])
        st.metric("المواعيد القادمة", upcoming)
    
    with col3:
        # أكثر الخدمات طلباً
        if not st.session_state.appointments_df.empty:
            popular_service = st.session_state.appointments_df['الخدمة'].mode()
            if not popular_service.empty:
                st.metric("أكثر خدمة طلباً", popular_service.iloc[0])
    
    # مخطط توزيع الخدمات
    st.subheader("📈 توزيع الخدمات")
    if not st.session_state.appointments_df.empty:
        service_counts = st.session_state.appointments_df['الخدمة'].value_counts()
        st.bar_chart(service_counts)

# القائمة الجانبية
with st.sidebar:
    st.header("⚙️ الإعدادات")
    
    اختيار = st.radio(
        "اختر الخدمة:",
        ["🏠 الصفحة الرئيسية", "📅 حجز موعد جديد", "📋 عرض المواعيد", "🔍 البحث عن موعد", "📊 الإحصائيات"]
    )
    
    st.markdown("---")
    st.subheader("📞 معلومات الاتصال")
    st.write("📞 الهاتف: 0123456789")
    st.write("📧 البريد: email@example.com")
    st.write("🏠 العنوان: عنوان المكتب")
    
    st.markdown("---")
    st.subheader("ℹ️ حول التطبيق")
    st.write("نظام حجز المواعيد الإلكتروني")
    st.write("الإصدار 1.0")
    st.write("تم التطوير باستخدام Streamlit")

# عرض المحتوى حسب الاختيار
if اختيار == "🏠 الصفحة الرئيسية":
    st.subheader("🎯 مرحباً بك في نظام حجز المواعيد")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("""
        **المميزات:**
        - ✅ حجز مواعيد جديدة
        - 📋 إدارة المواعيد
        - 🔍 بحث متقدم
        - 📊 إحصائيات مفصلة
        """)
    
    with col2:
        st.success("""
        **التعليمات:**
        1. اختر الخدمة من القائمة
        2. اتبع التعليمات
        3. احفظ البيانات تلقائياً
        """)
    
    # عرض آخر المواعيد
    if not st.session_state.appointments_df.empty:
        st.subheader("🕐 آخر المواعيد")
        last_appointments = st.session_state.appointments_df.tail(3)
        st.dataframe(last_appointments, use_container_width=True, hide_index=True)

elif اختيار == "📅 حجز موعد جديد":
    حجز_موعد()

elif اختيار == "📋 عرض المواعيد":
    عرض_المواعيد()

elif اختيار == "🔍 البحث عن موعد":
    البحث_عن_موعد()

elif اختيار == "📊 الإحصائيات":
    عرض_الإحصائيات()

# تذييل الصفحة
st.markdown("---")
st.markdown("<div style='text-align: center; color: gray;'>نظام حجز المواعيد © 2024</div>", unsafe_allow_html=True)