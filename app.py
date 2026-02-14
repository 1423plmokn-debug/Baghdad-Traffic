"""
نظام زحامات بغداد الذكي 🚕
نظام at the top. متقدم للتنبؤ بحركة المرور والتوصيل في بغداد
"""

import streamlit as st
import pandas as pd
import random
from datetime import datetime

# ============================================
# دالة محلل الاستجابة الذكية (Analysis Engine)
# يجب أن تكون معرفة قبل أي استدعاء لها
# ============================================
def generate_response(question, area, event, hour, multiplier, area_info):
    """محلل ذكي يقرأ الحالة المختارة ويجيب بناءً عليها فقط - بدون هلوسة"""
    
    question_lower = question.lower()
    area_data = area_info.get(area, {})
    area_type = area_data.get('type', 'غير معروف')
    typical_demand = area_data.get('typical_demand', 'متوسط')
    
    # حساب نسبة الزيادة
    increase_pct = int((multiplier - 1) * 100)
    
    # ========== سؤال: كيف الوضع ==========
    if any(word in question_lower for word in ['كيف', 'وضع', 'شو', 'حالة']):
        if multiplier >= 2.5:
            return (f"📊 **تحليل الوضع الحالي:**\n\n"
                   f"• المنطقة: {area} ({area_type})\n"
                   f"• الساعة: {hour}:00\n"
                   f"• الحالة: {event}\n"
                   f"• مستوى الطلب: {typical_demand}\n"
                   f"• معامل السعر: {multiplier}x (+{increase_pct}%)\n\n"
                   f"⚠️ **النتيجة:** الوضع حرج! الزحام شديد جداً في هذه المنطقة. "
                   f"بناءً على اختيارك لـ {area} و{event}، السعر ارتفع بنسبة {increase_pct}%.")
        elif multiplier >= 1.8:
            return (f"📊 **تحليل الوضع الحالي:**\n\n"
                   f"• المنطقة: {area} ({area_type})\n"
                   f"• الساعة: {hour}:00\n"
                   f"• الحالة: {event}\n"
                   f"• معامل السعر: {multiplier}x (+{increase_pct}%)\n\n"
                   f"⚠️ **النتيجة:** ازدحام ملحوظ. بناءً على اختيارك، "
                   f"السعر ارتفع بنسبة {increase_pct}% عن السعر الأساسي.")
        else:
            return (f"📊 **تحليل الوضع الحالي:**\n\n"
                   f"• المنطقة: {area} ({area_type})\n"
                   f"• الساعة: {hour}:00\n"
                   f"• الحالة: {event}\n"
                   f"• معامل السعر: {multiplier}x\n\n"
                   f"✅ **النتيجة:** الوضع طبيعي. حركة المرور طبيعية "
                   f"في {area} حالياً. السعر بدون ارتفاع.")
    
    # ========== سؤال: لماذا السعر مرتفع ==========
    if any(word in question_lower for word in ['لماذا', 'ليش', 'سعر', 'غالي', 'مرتفع']):
        if multiplier > 1.0:
            return (f"💰 **تحليل السعر:**\n\n"
                   f"السعر مرتفع بسبب:\n"
                   f"1. المنطقة: {area} - منطقة {typical_demand} الطلب\n"
                   f"2. الوقت: الساعة {hour}:00\n"
                   f"3. الحالة: {event}\n\n"
                   f"📈 **التفاصيل:**\n"
                   f"• السعر الأساسي: 3,000 IQD\n"
                   f"• معامل الزيادة: {multiplier}x\n"
                   f"• نسبة الارتفاع: +{increase_pct}%\n"
                   f"• السعر النهائي: {int(3000 * multiplier):,} IQD\n\n"
                   f"بناءً على اختيارك، السعر ارتفع بنسبة {increase_pct}%.")
        else:
            return f"💰 السعر حالياً طبيعي (3,000 IQD) - لا توجد زيادة في {area} حالياً."
    
    # ========== سؤال: أفضل وقت ==========
    if any(word in question_lower for word in ['أفضل', 'وقت', 'يناسب', 'امتى']):
        return (f"🕐 **أفضل أوقات التنقل في {area}:**\n\n"
               f"✅ الصباح الباكر: 6:00 - 8:00 صباحاً\n"
               f"✅ بعد الظهر: 14:00 - 16:00\n"
               f"✅ المساء: 21:00 - 23:00\n\n"
               f"❌ تجنب:\n"
               f"• ساعة الذروة الصباحية: 7:00 - 9:00\n"
               f"• ساعة الذروة المسائية: 16:00 - 19:00\n\n"
               f"💡 نصيحة: في {area}، أفضل وقت هو الصباح الباكر.")
    
    # ========== سؤال: السائقين ==========
    if any(word in question_lower for word in ['سائق', 'سائقين', 'توصيل', 'driver']):
        drivers = area_data.get('drivers', 50)
        return (f"🚗 **حالة السائقين في {area}:**\n\n"
               f"• عدد السائقين المطلوب: {drivers}\n"
               f"• نوع المنطقة: {area_type}\n"
               f"• الطلب المعتاد: {typical_demand}\n\n"
               f"💡 في حالة {event}، أنصح بزيادة السائقين بنسبة 50%.")
    
    # ========== سؤال: الأمطار ==========
    if any(word in question_lower for word in ['مطر', 'أمطار', 'rain']):
        if event == "أمطار غزيرة":
            return (f"🌧️ **تأثير الأمطار على {area}:**\n\n"
                   f"⚠️ الأمطار الغزيرة تؤدي لارتفاع حاد في الأسعار!\n"
                   f"• معامل السعر: {multiplier}x\n"
                   f"• نسبة الارتفاع: +{increase_pct}%\n\n"
                   f"💡 نصيحة: تجنب التنقل قدر الإمكان. إذا كنت "
                   f"بحاجة للتوصيلة، توقع أسعار أعلى بـ {multiplier} مرة.")
        else:
            return f"☀️ الطقس حالياً صافٍ في {area}. لا توجد أمطار."
    
    # ========== سؤال: المنطقة ==========
    if any(word in question_lower for word in ['منطقة', 'المنطقة', 'area']):
        return (f"🗺️ **معلومات عن {area}:**\n\n"
               f"• النوع: {area_type}\n"
               f"• الطلب المعتاد: {typical_demand}\n"
               f"• السائقون المطلوبون: {area_data.get('drivers', 50)}\n\n"
               f"💡 هذه المنطقة {typical_demand} الطلب.")
    
    # ========== سؤال عام ==========
    if any(word in question_lower for word in ['عام', 'everything', 'كل']):
        return (f"📋 **ملخص الحالة في {area}:**\n\n"
               f"🏷️ المنطقة: {area}\n"
               f"🕐 الوقت: {hour}:00\n"
               f"☁️ الحالة: {event}\n"
               f"💰 معامل السعر: {multiplier}x (+{increase_pct}%)\n"
               f"🚦 الطلب: {typical_demand}\n\n"
               f"💡 اسألني عن أي شيء محدد!")
    
    # ========== إجابة افتراضية ذكية ==========
    return (f"🤔 سؤالك: {question}\n\n"
           f"📊 **بناءً على حالتك الحالية:**\n"
           f"• المنطقة: {area}\n"
           f"• الوقت: {hour}:00\n"
           f"• الحدث: {event}\n"
           f"• معامل السعر: {multiplier}x\n\n"
           f"💡 اسألني: 'كيف الوضع؟' أو 'لماذا السعر مرتفع؟' أو 'ما أفضل وقت؟'")


# ============================================
# إعدادات الصفحة
# ============================================
st.set_page_config(
    page_title="نظام زحامات بغداد الذكي",
    page_icon="🚕",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# CSS للتصميم الداكن والذهبي
# ============================================
st.markdown("""
    <style>
    /* RTL Support */
    html[dir="rtl"] {
        direction: rtl;
        text-align: right;
    }
    
    /* Dark Theme Base */
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    
    /* Main Title */
    .main-title {
        font-size: 44px;
        font-weight: bold;
        color: #FFD700;
        text-align: center;
        padding: 25px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Gold Button Styling */
    .stButton > button {
        background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
        color: #000000;
        font-weight: bold;
        border: 2px solid #FFD700;
        border-radius: 10px;
        padding: 10px 25px;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #FFC107 0%, #FF8C00 100%);
        border-color: #FFC107;
        box-shadow: 0 0 15px rgba(255, 215, 0, 0.5);
    }
    
    /* Warning Boxes */
    .critical-warning {
        background: linear-gradient(135deg, #DC143C 0%, #8B0000 100%);
        color: white;
        font-size: 26px;
        font-weight: bold;
        text-align: center;
        padding: 25px;
        border-radius: 15px;
        border: 4px solid #FFD700;
        margin: 15px 0;
    }
    
    .high-warning {
        background: linear-gradient(135deg, #FF6347 0%, #FF4500 100%);
        color: white;
        font-size: 22px;
        font-weight: bold;
        text-align: center;
        padding: 20px;
        border-radius: 12px;
        border: 3px solid #FFD700;
        margin: 12px 0;
    }
    
    .normal-info {
        background: linear-gradient(135deg, #228B22 0%, #006400 100%);
        color: white;
        font-size: 20px;
        font-weight: bold;
        text-align: center;
        padding: 15px;
        border-radius: 10px;
        border: 3px solid #FFD700;
        margin: 10px 0;
    }
    
    /* Metrics */
    .stMetric {
        background-color: #1C1C1C;
        padding: 20px;
        border-radius: 12px;
        border: 2px solid #FFD700;
    }
    
    /* Chat Section */
    .chat-section {
        background: linear-gradient(135deg, #1C1C1C 0%, #2C2C2C 100%);
        padding: 25px;
        border-radius: 20px;
        border: 3px solid #FFD700;
        margin-top: 30px;
    }
    
    .user-message {
        background: linear-gradient(135deg, #2C2C2C 0%, #3C3C3C 100%);
        border-right: 4px solid #FFD700;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
    
    .assistant-message {
        background: linear-gradient(135deg, #1C3C5C 0%, #2C4C6C 100%);
        border-right: 4px solid #00CED1;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
    
    /* Gold accent for headers */
    h1, h2, h3 {
        color: #FFD700 !important;
    }
    </style>
""", unsafe_allow_html=True)

# تطبيق RTL
st.markdown('<html dir="rtl" lang="ar"></html>', unsafe_allow_html=True)

# ============================================
# العنوان الرئيسي
# ============================================
st.markdown('<p class="main-title">🚕 نظام زحامات بغداد الذكي 🛣️</p>', unsafe_allow_html=True)
st.markdown("---")

# ============================================
# الشريط الجانبي - المدخلات
# ============================================
st.sidebar.header("⚙️ إعدادات النظام")

# اختيار الوقت - 12 ساعة
st.sidebar.subheader("🕐 الوقت")

col_time1, col_time2 = st.sidebar.columns(2)
with col_time1:
    selected_hour = st.slider(
        "الساعة",
        min_value=1,
        max_value=12,
        value=datetime.now().hour % 12 if datetime.now().hour % 12 != 0 else 12,
        help="اختر الساعة من 1 إلى 12"
    )

with col_time2:
    am_pm = st.radio(
        "الفترة",
        ["صباحاً 🌅", "مساءاً 🌙"],
        index=0 if datetime.now().hour < 12 else 1,
        horizontal=True
    )

# تحويل إلى تنسيق 24 ساعة
hour_24 = selected_hour if "صباحاً" in am_pm else selected_hour + 12
if selected_hour == 12 and "مساءاً" in am_pm:
    hour_24 = 12

st.sidebar.info(f"🕐 الوقت المحدد: {hour_24}:00")

# ============================================
# المناطق
# ============================================
st.sidebar.subheader("📍 اختيار المنطقة")
areas = {
    "المنصور": {"icon": "🏛️", "typical_demand": "عالية", "drivers": 85, "type": "تجاري"},
    "الكرادة": {"icon": "🛒", "typical_demand": "عالية", "drivers": 80, "type": "مطاعم ومقاهي"},
    "الجادرية": {"icon": "🏢", "typical_demand": "عالية", "drivers": 75, "type": "الأعمال"},
    "الأعظمية": {"icon": "🕌", "typical_demand": "متوسطة-عالية", "drivers": 60, "type": "تاريخي وديني"},
    "زيونة": {"icon": "🏠", "typical_demand": "متوسطة", "drivers": 50, "type": "سكني"},
    "حي الجامعة": {"icon": "🎓", "typical_demand": "متوسطة", "drivers": 45, "type": "تعليمي"},
    "الدورة": {"icon": "🌊", "typical_demand": "متوسطة", "drivers": 40, "type": "صناعي"}
}

area_names = list(areas.keys())
selected_area = st.sidebar.selectbox(
    "المنطقة",
    area_names,
    help="اختر منطقة بغداد"
)

# ============================================
# الأحداث/الحالات
# ============================================
st.sidebar.subheader("☁️ الحالة المرورية")

events = {
    "يوم عادي": {"icon": "☀️", "multiplier": 1.0},
    "ساعة الذروة": {"icon": "🚨", "multiplier": 1.8},
    "مباراة للمنتخ": {"icon": "⚽", "multiplier": 2.5},
    "أمطار غزيرة": {"icon": "🌧️", "multiplier": 3.5}
}

event_names = list(events.keys())
selected_event = st.sidebar.selectbox(
    "الحالة",
    event_names,
    help="اختر الحالة المرورية الحالية"
)

# عرض الاختيارات الحالية
st.sidebar.markdown("---")
st.sidebar.markdown(f"**📍 المنطقة:** {areas[selected_area]['icon']} {selected_area}")
st.sidebar.markdown(f"**🕐 الساعة:** {hour_24}:00")
st.sidebar.markdown(f"**☁️ الحالة:** {events[selected_event]['icon']} {selected_event}")

# ============================================
# المنطق الرئيسي
# ============================================
price_multiplier = events[selected_event]['multiplier']

# تطبيق معامل ساعة الذروة تلقائياً
if 7 <= hour_24 <= 9 or 16 <= hour_24 <= 19:
    if selected_event == "يوم عادي":
        price_multiplier = 1.8
        st.sidebar.warning("🚨 ساعة الذروة تفعل تلقائياً!")

# حساب مستوى الطلب
if price_multiplier >= 2.5:
    demand_status = "🚨 ازدحام حرج"
    demand_color = "critical"
elif price_multiplier >= 1.8:
    demand_status = "⚠️ ازدحام عالي"
    demand_color = "high"
else:
    demand_status = "✅ حركة طبيعية"
    demand_color = "normal"

# ============================================
# القسم العلوي: لوحة المعلومات والرسوم البيانية
# ============================================
st.subheader("📊 لوحة المعلومات الفورية")

col1, col2, col3, col4 = st.columns(4)

#_METRICS
active_drivers = random.randint(150, 400)
pending_orders = random.randint(50, 250)
base_price = 3000
final_price = int(base_price * price_multiplier)
surge_percentage = int((price_multiplier - 1) * 100)

with col1:
    st.metric(
        label="🚗 السائقين النشطين",
        value=active_drivers,
        delta=random.randint(-30, 60)
    )

with col2:
    st.metric(
        label="📋 الطلبات المعلقة",
        value=pending_orders,
        delta=random.randint(-40, 40)
    )

with col3:
    st.metric(
        label="💰 سعر التوصيلة",
        value=f"{final_price:,} IQD",
        delta=f"+{surge_percentage}%" if surge_percentage > 0 else "طبيعي",
        delta_color="inverse" if surge_percentage > 0 else "normal"
    )

with col4:
    st.metric(
        label="📈 معامل السعر",
        value=f"{price_multiplier}x",
        delta=events[selected_event]['icon'],
        delta_color="inverse"
    )

st.markdown("---")

# حالة الزحام
st.subheader("📈 حالة الزحام الحالية")

if demand_color == "critical":
    st.markdown(f'<div class="critical-warning">{demand_status}</div>', unsafe_allow_html=True)
    st.error("🚨 **توصية:** توجه جميع السائقين المتاحين إلى هذه المنطقة فوراً!")
elif demand_color == "high":
    st.markdown(f'<div class="high-warning">{demand_status}</div>', unsafe_allow_html=True)
    st.warning("⚠️ **توصية:** زيادة عدد السائقين في المنطقة بنسبة 50%")
else:
    st.markdown(f'<div class="normal-info">{demand_status}</div>', unsafe_allow_html=True)
    st.success("✅ عمليات طبيعية - حافظ على توزيع السائقين المعتاد")

st.markdown("---")

# الرسم البياني وتحليل الأسعار
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("💵 تحليل الأسعار")
    st.write(f"**السعر الأساسي:** {base_price:,} IQD")
    st.write(f"**معامل السعر:** {price_multiplier}x")
    st.write(f"**السعر النهائي:** {final_price:,} IQD")
    
    if price_multiplier >= 2.5:
        st.error(f"🚨 **ارتفاع حاد:** تم تطبيق معامل {price_multiplier}x!")
    elif price_multiplier >= 1.8:
        st.warning(f"📈 **ارتفاع معتدل:** تم تطبيق معامل {price_multiplier}x")
    else:
        st.info("💚 **سعري طبيعي** - لا يوجد ارتفاع في الأسعار")

with col_right:
    st.subheader("📊 الطلب المتوقع حسب الساعة")
    
    hours = list(range(24))
    base_demand = [25, 18, 12, 8, 8, 12, 28, 55, 75, 85, 80, 72,
                   68, 62, 68, 78, 88, 95, 92, 82, 72, 62, 48, 32]
    
    if selected_event == "مباراة للمنتخ":
        event_multiplier = 2.5
    elif selected_event == "أمطار غزيرة":
        event_multiplier = 3.5
    elif selected_event == "ساعة الذروة":
        event_multiplier = 1.8
    else:
        event_multiplier = 1.0
    
    event_demand = [int(d * event_multiplier) for d in base_demand]
    
    df = pd.DataFrame({'الساعة': hours, 'الطلب': event_demand})
    chart_data = df.set_index('الساعة')
    
    # استخدام لون ذهبي ثابت للرسم البياني
    st.bar_chart(chart_data, color='#FFD700')
    
    st.write(f"📍 **الساعة المحددة:** {hour_24}:00 - **الطلب:** {event_demand[hour_24]} طلب")

# تحليل المنطقة
st.markdown("---")
st.subheader("🗺️ تحليل المنطقة")

area_data = areas[selected_area]
col_a, col_b, col_c = st.columns(3)
with col_a:
    st.metric("🚦 الطلب المعتاد", area_data["typical_demand"])
with col_b:
    st.metric("🚗 السائقون المطلوبون", area_data["drivers"])
with col_c:
    st.metric("🏷️ نوع المنطقة", area_data["type"])

# ============================================
# القسم السفلي: مساعد بغداد الذكي (Smart Chat)
# ============================================
st.markdown("---")
st.markdown('<div class="chat-section">', unsafe_allow_html=True)
st.subheader("💬 مساعد بغداد الذكي 🤖")

# عرض حالة المحادثة
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# عرض الرسائل
for message in st.session_state.chat_history:
    if message['role'] == 'user':
        st.markdown(f'<div class="user-message">👤 <strong>أنت:</strong> {message["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="assistant-message">🤖 <strong>المساعد:</strong><br>{message["content"]}</div>', unsafe_allow_html=True)

# إدخال السؤال
user_question = st.text_input(
    "💭 اسأل عن حالة الزحام:",
    placeholder="مثال: كيف الوضع؟ أو لماذا السعر مرتفع؟",
    key="chat_input"
)

# أزرار الإرسال والمسح
col_btn1, col_btn2 = st.columns([1, 4])
with col_btn1:
    if st.button("إرسال 📤", key="send_btn"):
        if user_question:
            st.session_state.chat_history.append({
                'role': 'user',
                'content': user_question
            })
            
            # استدعاء الدالة بعد تعريفها
            response = generate_response(
                user_question, 
                selected_area, 
                selected_event, 
                hour_24, 
                price_multiplier,
                areas
            )
            
            st.session_state.chat_history.append({
                'role': 'assistant',
                'content': response
            })
            
            st.rerun()

with col_btn2:
    if st.button("مسح المحادثة 🗑️", key="clear_btn"):
        st.session_state.chat_history = []
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# ============================================
# الذيل
# ============================================
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #FFD700; padding: 25px; background: linear-gradient(135deg, #1C1C1C 0%, #2C2C2C 100%); border-radius: 15px; border: 2px solid #FFD700;">
    <p style="font-size: 20px;"><strong>🚕 نظام زحامات بغداد الذكي</strong></p>
    <p>نظام متقدم للتنبؤ بحركة المرور | الإصدار 2.0</p>
    <p>🛣️ جعل التنقل أسهل في مدينة الذهب والأسواق</p>
</div>
""", unsafe_allow_html=True)
