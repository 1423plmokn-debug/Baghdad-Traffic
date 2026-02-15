"""
🚕 نظام زحامات بغداد الذكي - الإصدار 2.0
نظام متقدم للتنبؤ بحركة المرور والتوصيل في بغداد
"""

import streamlit as st
import pandas as pd
import random
from datetime import datetime
import folium
from streamlit_folium import st_folium

# ============================================
# دالة محلل الاستجابة الذكية (Analysis Engine)
# ============================================
def generate_response(question, area, event, hour, multiplier, area_info):
    """محلل ذكي يقرأ الحالة المختارة ويجيب بناءً عليها فقط"""
    
    question_lower = question.lower()
    area_data = area_info.get(area, {})
    area_type = area_data.get('type', 'غير معروف')
    typical_demand = area_data.get('typical_demand', 'متوسط')
    
    increase_pct = int((multiplier - 1) * 100)
    
    if any(word in question_lower for word in ['كيف', 'وضع', 'شو', 'حالة']):
        if multiplier >= 2.5:
            return (f"📊 **تحليل الوضع الحالي:**\n\n"
                   f"• المنطقة: {area} ({area_type})\n"
                   f"• الساعة: {hour}:00\n"
                   f"• الحالة: {event}\n"
                   f"• مستوى الطلب: {typical_demand}\n"
                   f"• معامل السعر: {multiplier}x (+{increase_pct}%)\n\n"
                   f"⚠️ **النتيجة:** الوضع حرج! الزحام شديد جداً.")
        elif multiplier >= 1.8:
            return (f"📊 **تحليل الوضع الحالي:**\n\n"
                   f"• المنطقة: {area} ({area_type})\n"
                   f"• الساعة: {hour}:00\n"
                   f"• الحالة: {event}\n"
                   f"• معامل السعر: {multiplier}x (+{increase_pct}%)\n\n"
                   f"⚠️ **النتيجة:** ازدحام ملحوظ.")
        else:
            return (f"📊 **تحليل الوضع الحالي:**\n\n"
                   f"• المنطقة: {area} ({area_type})\n"
                   f"• الساعة: {hour}:00\n"
                   f"• الحالة: {event}\n"
                   f"• معامل السعر: {multiplier}x\n\n"
                   f"✅ **النتيجة:** الوضع طبيعي.")
    
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
                   f"• السعر النهائي: {int(3000 * multiplier):,} IQD")
        else:
            return f"💰 السعر حالياً طبيعي (3,000 IQD)"
    
    if any(word in question_lower for word in ['أفضل', 'وقت', 'يناسب', 'امتى']):
        return (f"🕐 **أفضل أوقات التنقل في {area}:**\n\n"
               f"✅ الصباح الباكر: 6:00 - 8:00 صباحاً\n"
               f"✅ بعد الظهر: 14:00 - 16:00\n"
               f"✅ المساء: 21:00 - 23:00\n\n"
               f"❌ تجنب:\n"
               f"• ساعة الذروة الصباحية: 7:00 - 9:00\n"
               f"• ساعة الذروة المسائية: 16:00 - 19:00")
    
    if any(word in question_lower for word in ['سائق', 'سائقين', 'توصيل', 'driver']):
        drivers = area_data.get('drivers', 50)
        return (f"🚗 **حالة السائقين في {area}:**\n\n"
               f"• عدد السائقين المطلوب: {drivers}\n"
               f"• نوع المنطقة: {area_type}\n"
               f"• الطلب المعتاد: {typical_demand}\n\n"
               f"💡 في حالة {event}، أنصح بزيادة السائقين بنسبة 50%.")
    
    if any(word in question_lower for word in ['مطر', 'أمطار', 'rain']):
        if event == "أمطار غزيرة":
            return (f"🌧️ **تأثير الأمطار على {area}:**\n\n"
                   f"⚠️ الأمطار الغزيرة تؤدي لارتفاع حاد في الأسعار!\n"
                   f"• معامل السعر: {multiplier}x\n"
                   f"• نسبة الارتفاع: +{increase_pct}%\n\n"
                   f"💡 نصيحة: تجنب التنقل قدر الإمكان.")
        else:
            return f"☀️ الطقس حالياً صافٍ في {area}."
    
    if any(word in question_lower for word in ['منطقة', 'المنطقة', 'area']):
        return (f"🗺️ **معلومات عن {area}:**\n\n"
               f"• النوع: {area_type}\n"
               f"• الطلب المعتاد: {typical_demand}\n"
               f"• السائقون المطلوبون: {area_data.get('drivers', 50)}")
    
    if any(word in question_lower for word in ['عام', 'everything', 'كل']):
        return (f"📋 **ملخص الحالة في {area}:**\n\n"
               f"🏷️ المنطقة: {area}\n"
               f"🕐 الوقت: {hour}:00\n"
               f"☁️ الحالة: {event}\n"
               f"💰 معامل السعر: {multiplier}x (+{increase_pct}%)\n"
               f"🚦 الطلب: {typical_demand}\n\n"
               f"💡 اسألني عن أي شيء محدد!")
    
    return (f"🤔 سؤالك: {question}\n\n"
           f"📊 **بناءً على حالتك الحالية:**\n"
           f"• المنطقة: {area}\n"
           f"• الوقت: {hour}:00\n"
           f"• الحدث: {event}\n"
           f"• معامل السعر: {multiplier}x\n\n"
           f"💡 اسألني: 'كيف الوضع؟' أو 'لماذا السعر مرتفع؟'")


# ============================================
# Baghdad Areas Data with Real Coordinates
# ============================================
BAGHDAD_AREAS = {
    "المنصور": {
        "icon": "🏛️", 
        "typical_demand": "عالية", 
        "drivers": 85, 
        "type": "تجاري",
        "lat": 33.3209, 
        "lon": 44.3661
    },
    "الكرادة": {
        "icon": "🛒", 
        "typical_demand": "عالية", 
        "drivers": 80, 
        "type": "مطاعم ومقاهي",
        "lat": 33.3156, 
        "lon": 44.4012
    },
    "الجادرية": {
        "icon": "🏢", 
        "typical_demand": "عالية", 
        "drivers": 75, 
        "type": "الأعمال",
        "lat": 33.3089, 
        "lon": 44.3432
    },
    "الأعظمية": {
        "icon": "🕌", 
        "typical_demand": "متوسطة-عالية", 
        "drivers": 60, 
        "type": "تاريخي وديني",
        "lat": 33.3428, 
        "lon": 44.3278
    },
    " زيونة": {
        "icon": "🏠", 
        "typical_demand": "متوسطة", 
        "drivers": 50, 
        "type": "سكني",
        "lat": 33.3289, 
        "lon": 44.3923
    },
    "حي الجامعة": {
        "icon": "🎓", 
        "typical_demand": "متوسطة", 
        "drivers": 45, 
        "type": "تعليمي",
        "lat": 33.3056, 
        "lon": 44.3567
    },
    "الدورة": {
        "icon": "🌊", 
        "typical_demand": "متوسطة", 
        "drivers": 40, 
        "type": "صناعي",
        "lat": 33.2834, 
        "lon": 44.3712
    },
    "الوزيرية": {
        "icon": "⚰️", 
        "typical_demand": "منخفضة", 
        "drivers": 30, 
        "type": "سكني",
        "lat": 33.3312, 
        "lon": 44.3845
    },
    "المزة": {
        "icon": "🏰", 
        "typical_demand": "متوسطة-عالية", 
        "drivers": 55, 
        "type": "سكني فاخر",
        "lat": 33.3456, 
        "lon": 44.4123
    },
    "اليرموك": {
        "icon": "🏘️", 
        "typical_demand": "متوسطة", 
        "drivers": 48, 
        "type": "سكني",
        "lat": 33.3123, 
        "lon": 44.4234
    }
}


# ============================================
# Create Baghdad Map with Dynamic Markers
# ============================================
@st.cache_data
def create_baghdad_map(areas, selected_area, price_multiplier, demand_color):
    """إنشاء خريطة بغداد التفاعلية"""
    
    # مركز الخريطة على بغداد
    baghdad_center = [33.3128, 44.3615]
    
    # إنشاء الخريطة
    m = folium.Map(
        location=baghdad_center,
        zoom_start=12,
        tiles='CartoDB dark_matter'
    )
    
    # تحديد لون الحالة المرورية
    if demand_color == "critical":
        status_color = "red"
        status_icon = "exclamation-triangle"
    elif demand_color == "high":
        status_color = "orange"
        status_icon = "warning"
    else:
        status_color = "green"
        status_icon = "check"
    
    # إضافة علامات للمناطق
    for area_name, area_data in areas.items():
        lat = area_data.get('lat', 33.3128)
        lon = area_data.get('lon', 44.3615)
        
        # تحديد لون العلامة بناءً على المنطقة المحددة
        if area_name == selected_area:
            marker_color = status_color
            is_selected = True
        else:
            # ألوان المناطق الأخرى بناءً على الطلب
            if area_data['typical_demand'] == "عالية":
                marker_color = "orange"
            elif area_data['typical_demand'] == "متوسطة-عالية":
                marker_color = "lightorange"
            else:
                marker_color = "green"
            is_selected = False
        
        # إنشاء popup للمعلومات
        popup_html = f"""
        <div style="font-family: Cairo, sans-serif; text-align: right; direction: rtl;">
            <h4 style="color: #FFD700; margin-bottom: 10px;">{area_data['icon']} {area_name}</h4>
            <p><strong>النوع:</strong> {area_data['type']}</p>
            <p><strong>الطلب:</strong> {area_data['typical_demand']}</p>
            <p><strong>السائقون:</strong> {area_data['drivers']}</p>
            <p><strong>معامل السعر:</strong> {price_multiplier}x</p>
        </div>
        """
        
        # إضافة العلامة
        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=f"{area_name} - {area_data['typical_demand']} الطلب",
            icon=folium.Icon(color=marker_color, icon=area_data['icon'], prefix='fa')
        ).add_to(m)
    
    return m


# ============================================
# Trip Forecaster Function
# ============================================
def calculate_trip_time(start_location, end_location, event_multiplier):
    """حساب وقت الرحلة المتوقع"""
    import math
    
    #_coordinates
    start_lat = BAGHDAD_AREAS.get(start_location, {}).get('lat', 33.3128)
    start_lon = BAGHDAD_AREAS.get(start_location, {}).get('lon', 44.3615)
    end_lat = BAGHDAD_AREAS.get(end_location, {}).get('lat', 33.3128)
    end_lon = BAGHDAD_AREAS.get(end_location, {}).get('lon', 44.3615)
    
    # Calculate distance using Haversine formula
    R = 6371  # Earth's radius in km
    
    lat1, lon1, lat2, lon2 = map(math.radians, [start_lat, start_lon, end_lat, end_lon])
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    distance = R * c  # Distance in km
    
    # Base time: assume average speed of 25 km/h in Baghdad traffic
    base_time = (distance / 25) * 60  # Convert to minutes
    
    # Add random variation (±20%)
    base_time = base_time * random.uniform(0.8, 1.2)
    
    # Ensure minimum time
    base_time = max(base_time, 10)
    
    # Apply event multiplier
    final_time = base_time * event_multiplier
    
    # Round to nearest minute
    final_time = round(final_time)
    
    return final_time, round(base_time), round(distance, 1)


# ============================================
# إعدادات الصفحة
# ============================================
st.set_page_config(
    page_title="🚕 نظام زحامات بغداد الذكي",
    page_icon="🚕",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# CSS - Glassmorphism & Cyberpunk Gold Theme
# ============================================

# Determine if rain mode
is_rain_mode = "أمطار غزيرة" in st.session_state.get('selected_event', '')

# Base CSS
st.markdown(f"""
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700;900&display=swap" rel="stylesheet">
    
    <style>
    /* RTL Support */
    html[dir="rtl"] {{
        direction: rtl;
        text-align: right;
    }}
    
    /* Global Font */
    * {{
        font-family: 'Cairo', sans-serif !important;
    }}
    
    /* Dark Theme Base */
    .stApp {{
        background-color: #0E1117;
        color: #FAFAFA;
        {'background: linear-gradient(135deg, #0a1929 0%, #1a2a4a 100%) !important;' if is_rain_mode else ''}
    }}
    
    /* Glassmorphism Effect */
    .glass-card {{
        background: rgba(30, 30, 30, 0.7) !important;
        backdrop-filter: blur(10px) !important;
        -webkit-backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(255, 215, 0, 0.3) !important;
        border-radius: 20px !important;
        padding: 20px !important;
        margin: 10px 0 !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37) !important;
    }}
    
    /* Main Title */
    .main-title {{
        font-size: 52px;
        font-weight: 900;
        color: #FFD700;
        text-align: center;
        padding: 30px;
        text-shadow: 0 0 20px rgba(255, 215, 0, 0.5), 0 0 40px rgba(255, 215, 0, 0.3);
        font-family: 'Cairo', sans-serif;
        animation: glow 2s ease-in-out infinite alternate;
    }}
    
    @keyframes glow {{
        from {{ text-shadow: 0 0 20px rgba(255, 215, 0, 0.5), 0 0 40px rgba(255, 215, 0, 0.3); }}
        to {{ text-shadow: 0 0 30px rgba(255, 215, 0, 0.8), 0 0 60px rgba(255, 215, 0, 0.5); }}
    }}
    
    /* Neon Gold Button Styling */
    .stButton > button {{
        background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%) !important;
        color: #000000 !important;
        font-weight: bold !important;
        border: 2px solid #FFD700 !important;
        border-radius: 12px !important;
        padding: 12px 30px !important;
        transition: all 0.3s ease !important;
        font-family: 'Cairo', sans-serif !important;
        position: relative;
        overflow: hidden;
    }}
    
    .stButton > button:hover {{
        background: linear-gradient(135deg, #FFC107 0%, #FF8C00 100%) !important;
        border-color: #FFC107 !important;
        box-shadow: 0 0 25px rgba(255, 215, 0, 0.6) !important;
        transform: translateY(-2px) !important;
    }}
    
    .stButton > button:before {{
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: linear-gradient(45deg, transparent, rgba(255,255,255,0.3), transparent);
        transform: rotate(45deg);
        animation: shine 3s infinite;
    }}
    
    @keyframes shine {{
        0% {{ transform: translateX(-100%) rotate(45deg); }}
        100% {{ transform: translateX(100%) rotate(45deg); }}
    }}
    
    /* Floating Metric Cards */
    .metric-card {{
        background: rgba(30, 30, 30, 0.8) !important;
        backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(255, 215, 0, 0.4) !important;
        border-radius: 20px !important;
        padding: 25px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3) !important;
    }}
    
    .metric-card:hover {{
        transform: translateY(-5px) !important;
        box-shadow: 0 15px 40px rgba(255, 215, 0, 0.2) !important;
        border-color: rgba(255, 215, 0, 0.8) !important;
    }}
    
    /* Warning Boxes */
    .critical-warning {{
        background: linear-gradient(135deg, rgba(220, 20, 60, 0.9) 0%, rgba(139, 0, 0, 0.9) 100%) !important;
        color: white;
        font-size: 28px;
        font-weight: bold;
        text-align: center;
        padding: 30px;
        border-radius: 20px;
        border: 3px solid #FFD700;
        margin: 15px 0;
        animation: pulse-critical 1.5s ease-in-out infinite;
    }}
    
    @keyframes pulse-critical {{
        0%, 100% {{ box-shadow: 0 0 20px rgba(220, 20, 60, 0.5); }}
        50% {{ box-shadow: 0 0 40px rgba(220, 20, 60, 0.8); }}
    }}
    
    .high-warning {{
        background: linear-gradient(135deg, rgba(255, 99, 71, 0.9) 0%, rgba(255, 69, 0, 0.9) 100%) !important;
        color: white;
        font-size: 24px;
        font-weight: bold;
        text-align: center;
        padding: 25px;
        border-radius: 18px;
        border: 3px solid #FFD700;
        margin: 12px 0;
    }}
    
    .normal-info {{
        background: linear-gradient(135deg, rgba(34, 139, 34, 0.9) 0%, rgba(0, 100, 0, 0.9) 100%) !important;
        color: white;
        font-size: 22px;
        font-weight: bold;
        text-align: center;
        padding: 20px;
        border-radius: 15px;
        border: 3px solid #FFD700;
        margin: 10px 0;
    }}
    
    /* Chat Section */
    .chat-section {{
        background: rgba(30, 30, 30, 0.8) !important;
        backdrop-filter: blur(15px) !important;
        padding: 30px !important;
        border-radius: 25px !important;
        border: 2px solid rgba(255, 215, 0, 0.4) !important;
        margin-top: 30px !important;
    }}
    
    .user-message {{
        background: rgba(50, 50, 50, 0.9) !important;
        border-right: 5px solid #FFD700 !important;
        padding: 18px !important;
        border-radius: 15px !important;
        margin: 12px 0 !important;
    }}
    
    .assistant-message {{
        background: rgba(28, 60, 92, 0.9) !important;
        border-right: 5px solid #00CED1 !important;
        padding: 18px !important;
        border-radius: 15px !important;
        margin: 12px 0 !important;
    }}
    
    /* Gold accent for headers */
    h1, h2, h3, h4 {{
        color: #FFD700 !important;
        font-family: 'Cairo', sans-serif !important;
    }}
    
    /* Sidebar Styling */
    .css-1d391kg {{
        background: rgba(20, 20, 20, 0.95) !important;
    }}
    
    /* Rain Animation */
    .rain-overlay {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: 9999;
        background: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><line x1="10" y1="0" x2="10" y2="30" stroke="rgba(174, 194, 224, 0.3)" stroke-width="1"/></svg>');
        animation: rain 0.5s linear infinite;
    }}
    
    @keyframes rain {{
        from {{ background-position: 0 0; }}
        to {{ background-position: 20px 100px; }}
    }}
    
    /* Trip Forecast Card */
    .trip-forecast {{
        background: linear-gradient(135deg, rgba(255, 215, 0, 0.2) 0%, rgba(255, 165, 0, 0.2) 100%) !important;
        border: 2px solid #FFD700 !important;
        border-radius: 25px !important;
        padding: 30px !important;
        text-align: center !important;
    }}
    
    /* Map Container */
    .map-container {{
        border-radius: 20px !important;
        overflow: hidden !important;
        border: 3px solid #FFD700 !important;
    }}
    
    /* Section Divider */
    .section-divider {{
        height: 3px;
        background: linear-gradient(90deg, transparent, #FFD700, transparent);
        margin: 25px 0;
    }}
    
    /* Footer */
    .footer {{
        text-align: center;
        color: #FFD700;
        padding: 30px;
        background: linear-gradient(135deg, rgba(30, 30, 30, 0.9) 0%, rgba(40, 40, 40, 0.9) 100%);
        border-radius: 20px;
        border: 2px solid #FFD700;
        margin-top: 30px;
    }}
    
    /* Responsive Design */
    @media (max-width: 768px) {{
        .main-title {{
            font-size: 32px !important;
            padding: 15px !important;
        }}
        .metric-card {{
            padding: 15px !important;
        }}
        .critical-warning, .high-warning, .normal-info {{
            font-size: 18px !important;
            padding: 15px !important;
        }}
    }}
    </style>
    
    <!-- Rain Effect Overlay -->
    {'<div class="rain-overlay"></div>' if is_rain_mode else ''}
    
    <!-- RTL HTML -->
    <html dir="rtl" lang="ar"></html>
""", unsafe_allow_html=True)

# ============================================
# العنوان الرئيسي
# ============================================
st.markdown('<p class="main-title">🚕 نظام زحامات بغداد الذكي 🛣️</p>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #aaa; font-size: 18px;">نظام متقدم للتنبؤ بحركة المرور والتوصيل في مدينة الذهب والأسواق</p>', unsafe_allow_html=True)
st.markdown("---")

# ============================================
# الشريط الجانبي - المدخلات
# ============================================
st.sidebar.header("⚙️ إعدادات النظام")

# اختيار الوقت
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

area_names = list(BAGHDAD_AREAS.keys())
selected_area = st.sidebar.selectbox(
    "المنطقة",
    area_names,
    help="اختر منطقة بغداد",
    index=0
)

# ============================================
# الأحداث/الحالات
# ============================================
st.sidebar.subheader("☁️ الحالة المرورية")

events = {
    "يوم عادي": {"icon": "☀️", "multiplier": 1.0},
    "ساعة الذروة": {"icon": "🚨", "multiplier": 1.8},
    "مباراة للمنتخ": {"icon": "⚽", "multiplier": 2.5},
    "أمطار غزيرة": {"icon": "🌧️", "multiplier": 3.5},
    "حدث وطني": {"icon": "🎌", "multiplier": 2.2},
    "إغلاق طرق": {"icon": "🚧", "multiplier": 2.8}
}

event_names = list(events.keys())
selected_event = st.sidebar.selectbox(
    "الحالة",
    event_names,
    help="اختر الحالة المرورية الحالية",
    index=0
)

# Store in session state for rain detection
st.session_state['selected_event'] = selected_event

# ============================================
# 🔮 Trip Forecaster Section
# ============================================
st.sidebar.markdown("---")
st.sidebar.markdown("### 🔮 تنبؤ الرحلة")

start_location = st.sidebar.selectbox(
    "📍 نقطة الانطلاق",
    area_names,
    index=0,
    key="start_loc"
)

end_location = st.sidebar.selectbox(
    "🏁 الوجهة",
    area_names,
    index=1 if len(area_names) > 1 else 0,
    key="end_loc"
)

if st.sidebar.button("🔮 احسب وقت الرحلة", key="forecast_btn"):
    event_multiplier = events[selected_event]['multiplier']
    final_time, base_time, distance = calculate_trip_time(
        start_location, 
        end_location, 
        event_multiplier
    )
    
    st.session_state['trip_forecast'] = {
        'final_time': final_time,
        'base_time': base_time,
        'distance': distance,
        'start': start_location,
        'end': end_location,
        'multiplier': event_multiplier
    }

# Display trip forecast if available
if 'trip_forecast' in st.session_state:
    forecast = st.session_state['trip_forecast']
    st.sidebar.markdown(f"""
    <div class="trip-forecast">
        <h3 style="color: #FFD700; margin-bottom: 15px;">⏱️ وقت الرحلة المتوقع</h3>
        <h2 style="font-size: 48px; color: #fff; margin: 10px 0;">{forecast['final_time']} دقيقة</h2>
        <p style="color: #aaa;">من {forecast['start']} إلى {forecast['end']}</p>
        <p style="color: #aaa;">المسافة: {forecast['distance']} كم</p>
        {'<p style="color: #ff6b6b;">⚠️ بسبب الزحام الحالي</p>' if forecast['multiplier'] > 1.0 else '<p style="color: #51cf66;">✅ حركة طبيعية</p>'}
    </div>
    """, unsafe_allow_html=True)

# ============================================
# عرض الاختيارات الحالية
# ============================================
st.sidebar.markdown("---")
st.sidebar.markdown(f"**📍 المنطقة:** {BAGHDAD_AREAS[selected_area]['icon']} {selected_area}")
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
st.markdown("## 📊 لوحة المعلومات الفورية")

col1, col2, col3, col4 = st.columns(4)

# Metrics
active_drivers = random.randint(150, 400)
pending_orders = random.randint(50, 250)
base_price = 3000
final_price = int(base_price * price_multiplier)
surge_percentage = int((price_multiplier - 1) * 100)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <p style="color: #aaa; margin: 0;">🚗 السائقين النشطين</p>
        <h2 style="color: #FFD700; font-size: 36px; margin: 10px 0;">{active_drivers}</h2>
        <p style="color: {"#51cf66" if random.randint(0,1) else "#ff6b6b"};">{"+" if random.randint(0,1) else ""}{random.randint(-30, 60)}</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <p style="color: #aaa; margin: 0;">📋 الطلبات المعلقة</p>
        <h2 style="color: #FFD700; font-size: 36px; margin: 10px 0;">{pending_orders}</h2>
        <p style="color: {"#51cf66" if random.randint(0,1) else "#ff6b6b"};">{"+" if random.randint(0,1) else ""}{random.randint(-40, 40)}</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <p style="color: #aaa; margin: 0;">💰 سعر التوصيلة</p>
        <h2 style="color: #FFD700; font-size: 32px; margin: 10px 0;">{final_price:,} IQD</h2>
        <p style="color: {"#ff6b6b" if surge_percentage > 0 else "#51cf66"};">{"+" if surge_percentage > 0 else ""}{surge_percentage}%</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <p style="color: #aaa; margin: 0;">📈 معامل السعر</p>
        <h2 style="color: #FFD700; font-size: 36px; margin: 10px 0;">{price_multiplier}x</h2>
        <p style="color: #aaa;">{events[selected_event]['icon']}</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ============================================
# 🗺️ خريطة Baghdad التفاعلية
# ============================================
st.markdown("## 🗺️ خريطة المناطق")

# Create map
baghdad_map = create_baghdad_map(
    BAGHDAD_AREAS, 
    selected_area, 
    price_multiplier, 
    demand_color
)

# Display map
st_folium(
    baghdad_map,
    width="100%",
    height=450,
    returned_objects=[]
)

st.markdown("---")

# ============================================
# 📈 حالة الزحام
# ============================================
st.markdown("## 📈 حالة الزحام الحالية")

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

# ============================================
# 💵 تحليل الأسعار و📊 الطلب المتوقع
# ============================================
col_left, col_right = st.columns(2)

with col_left:
    st.markdown("### 💵 تحليل الأسعار")
    st.markdown(f"""
    <div class="glass-card">
        <p><strong>السعر الأساسي:</strong> {base_price:,} IQD</p>
        <p><strong>معامل السعر:</strong> {price_multiplier}x</p>
        <p><strong>السعر النهائي:</strong> {final_price:,} IQD</p>
    </div>
    """, unsafe_allow_html=True)
    
    if price_multiplier >= 2.5:
        st.error(f"🚨 **ارتفاع حاد:** تم تطبيق معامل {price_multiplier}x!")
    elif price_multiplier >= 1.8:
        st.warning(f"📈 **ارتفاع معتدل:** تم تطبيق معامل {price_multiplier}x")
    else:
        st.info("💚 **سعري طبيعي** - لا يوجد ارتفاع في الأسعار")

with col_right:
    st.markdown("### 📊 الطلب المتوقع حسب الساعة")
    
    hours = list(range(24))
    base_demand = [25, 18, 12, 8, 8, 12, 28, 55, 75, 85, 80, 72,
                   68, 62, 68, 78, 88, 95, 92, 82, 72, 62, 48, 32]
    
    if selected_event == "مباراة للمنتخ":
        event_multiplier_chart = 2.5
    elif selected_event == "أمطار غزيرة":
        event_multiplier_chart = 3.5
    elif selected_event == "ساعة الذروة":
        event_multiplier_chart = 1.8
    elif selected_event == "إغلاق طرق":
        event_multiplier_chart = 2.8
    elif selected_event == "حدث وطني":
        event_multiplier_chart = 2.2
    else:
        event_multiplier_chart = 1.0
    
    event_demand = [int(d * event_multiplier_chart) for d in base_demand]
    
    df = pd.DataFrame({'الساعة': hours, 'الطلب': event_demand})
    chart_data = df.set_index('الساعة')
    
    st.bar_chart(chart_data, color='#FFD700')
    
    st.write(f"📍 **الساعة المحددة:** {hour_24}:00 - **الطلب:** {event_demand[hour_24]} طلب")

# تحليل المنطقة
st.markdown("---")
st.markdown("### 🗺️ تحليل المنطقة")

area_data = BAGHDAD_AREAS[selected_area]
col_a, col_b, col_c = st.columns(3)

with col_a:
    st.markdown(f"""
    <div class="glass-card" style="text-align: center;">
        <p style="color: #aaa;">🚦 الطلب المعتاد</p>
        <h3 style="color: #FFD700;">{area_data["typical_demand"]}</h3>
    </div>
    """, unsafe_allow_html=True)

with col_b:
    st.markdown(f"""
    <div class="glass-card" style="text-align: center;">
        <p style="color: #aaa;">🚗 السائقون المطلوبون</p>
        <h3 style="color: #FFD700;">{area_data["drivers"]}</h3>
    </div>
    """, unsafe_allow_html=True)

with col_c:
    st.markdown(f"""
    <div class="glass-card" style="text-align: center;">
        <p style="color: #aaa;">🏷️ نوع المنطقة</p>
        <h3 style="color: #FFD700;">{area_data["type"]}</h3>
    </div>
    """, unsafe_allow_html=True)

# ============================================
# 💬 مساعد Baghdad الذكي (Smart Chat)
# ============================================
st.markdown("---")
st.markdown('<div class="chat-section">', unsafe_allow_html=True)
st.markdown("### 💬 مساعد Baghdad الذكي 🤖")

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
    placeholder="مثال: كيف الوضع؟ أو لماذا السعر مرتفع؟ أو ما أفضل وقت؟",
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
            
            # استدعاء الدالة
            response = generate_response(
                user_question, 
                selected_area, 
                selected_event, 
                hour_24, 
                price_multiplier,
                BAGHDAD_AREAS
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
# الذيل (Footer)
# ============================================
st.markdown("---")
st.markdown("""
<div class="footer">
    <p style="font-size: 24px; margin-bottom: 10px;"><strong>🚕 نظام زحامات Baghdad الذكي</strong></p>
    <p>نظام متقدم للتنبؤ بحركة المرور | الإصدار 2.0</p>
    <p>🛣️ جعل التنقل أسهل في مدينة الذهب والأسواق</p>
    <p style="margin-top: 15px; font-size: 14px; color: #888;">Powered by Streamlit & Folium</p>
</div>
""", unsafe_allow_html=True)
