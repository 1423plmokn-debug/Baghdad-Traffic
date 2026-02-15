"""
===============================================================================
BAGHDAD INTELLIGENT TRAFFIC SYSTEM (BITS) - Version 3.0
===============================================================================
Professional Logistics Management System for Baghdad Transportation
Features: SQL, JavaScript Audio Alerts, Dynamic CSS, AI Predictions
===============================================================================
"""

import streamlit as st
import pandas as pd
import random
import math
import sqlite3
import json
from datetime import datetime, time
from typing import Dict, List, Tuple
import folium
from streamlit_folium import st_folium

# ============================================================
# SECTION 1: DATABASE MANAGEMENT (SQLite3)
# ============================================================

class TrafficDatabase:
    """SQLite Database Manager for Active Road Incidents"""
    
    def __init__(self, db_path: str = "bits_traffic.db"):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """Initialize database schema"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS active_road_incidents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                zone TEXT NOT NULL,
                incident_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                description TEXT,
                latitude REAL,
                longitude REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active INTEGER DEFAULT 1,
                affected_road TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pricing_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                origin_zone TEXT NOT NULL,
                destination_zone TEXT NOT NULL,
                base_price REAL,
                final_price REAL,
                route_type TEXT,
                distance_km REAL,
                multiplier REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                weather TEXT,
                time_period TEXT
            )
        """)
        
        cursor.execute("SELECT COUNT(*) FROM active_road_incidents")
        if cursor.fetchone()[0] == 0:
            sample_incidents = [
                ("المنصور", "road_closure", "high", "اغلاق جزئي للطريق", 33.3209, 44.3661, "شارع الجزائر"),
                ("الكرادة", "construction", "medium", "اعمال بناء", 33.3156, 44.4012, "شارع كراده"),
                ("الجادرية", "accident", "high", "حادث مروري", 33.3089, 44.3432, "جسر الجادرية"),
                ("الأعظمية", "road_closure", "critical", "اغلاق كامل", 33.3428, 44.3278, "شارع الأعظمية"),
            ]
            cursor.executemany("""
                INSERT INTO active_road_incidents 
                (zone, incident_type, severity, description, latitude, longitude, affected_road)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, sample_incidents)
        
        conn.commit()
        conn.close()
    
    def get_active_incidents(self) -> List[Dict]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, zone, incident_type, severity, description, 
                   latitude, longitude, affected_road, created_at
            FROM active_road_incidents 
            WHERE is_active = 1
            ORDER BY CASE severity
                WHEN 'critical' THEN 1
                WHEN 'high' THEN 2
                WHEN 'medium' THEN 3
                ELSE 4
            END
        """)
        incidents = []
        for row in cursor.fetchall():
            incidents.append({
                'id': row[0], 'zone': row[1], 'incident_type': row[2],
                'severity': row[3], 'description': row[4],
                'latitude': row[5], 'longitude': row[6],
                'affected_road': row[7], 'created_at': row[8]
            })
        conn.close()
        return incidents
    
    def add_incident(self, zone: str, incident_type: str, severity: str, 
                    description: str, latitude: float, longitude: float, affected_road: str) -> bool:
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO active_road_incidents 
                (zone, incident_type, severity, description, latitude, longitude, affected_road)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (zone, incident_type, severity, description, latitude, longitude, affected_road))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding incident: {e}")
            return False
    
    def remove_incident(self, incident_id: int) -> bool:
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE active_road_incidents SET is_active = 0 WHERE id = ?", (incident_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error removing incident: {e}")
            return False
    
    def get_incident_count_by_zone(self) -> Dict[str, int]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT zone, COUNT(*) FROM active_road_incidents WHERE is_active = 1 GROUP BY zone")
        result = {row[0]: row[1] for row in cursor.fetchall()}
        conn.close()
        return result


# ============================================================
# SECTION 2: BAGHDAD GEOGRAPHICAL INTELLIGENCE
# ============================================================

class BaghdadGeographicalIntelligence:
    """Comprehensive Baghdad Zones Dictionary with coordinates"""
    
    ZONES = {
        # KARKH (Western Baghdad)
        "الكاظمية": {"region": "Karkh", "type": "historical", "lat": 33.3428, "lon": 44.3278, "typical_demand": "medium", "base_price": 3500, "icon": "🕌"},
        "الزعفرانية": {"region": "Karkh", "type": "residential", "lat": 33.2987, "lon": 44.3456, "typical_demand": "high", "base_price": 3000, "icon": "🏘️"},
        "حيبس": {"region": "Karkh", "type": "residential", "lat": 33.2856, "lon": 44.3534, "typical_demand": "medium", "base_price": 2800, "icon": "🏠"},
        "الدورة": {"region": "Karkh", "type": "industrial", "lat": 33.2834, "lon": 44.3712, "typical_demand": "medium", "base_price": 3200, "icon": "🏭"},
        "التاجي": {"region": "Karkh", "type": "suburban", "lat": 33.2656, "lon": 44.3289, "typical_demand": "low", "base_price": 2500, "icon": "🌾"},
        
        # RUSAFA (Eastern Baghdad)
        "الكرادة": {"region": "Rusafa", "type": "commercial", "lat": 33.3156, "lon": 44.4012, "typical_demand": "very_high", "base_price": 4500, "icon": "🛒"},
        "oley": {"region": "Rusafa", "type": "residential", "lat": 33.3289, "lon": 44.3923, "typical_demand": "high", "base_price": 3800, "icon": "🏠"},
        "المزة": {"region": "Rusafa", "type": "upscale_residential", "lat": 33.3456, "lon": 44.4123, "typical_demand": "high", "base_price": 4200, "icon": "🏰"},
        "اليرموك": {"region": "Rusafa", "type": "residential", "lat": 33.3123, "lon": 44.4234, "typical_demand": "medium", "base_price": 3200, "icon": "🏘️"},
        "سبع ابكار": {"region": "Rusafa", "type": "residential", "lat": 33.3356, "lon": 44.4089, "typical_demand": "medium", "base_price": 3000, "icon": "🏡"},
        
        # CENTER (Downtown Baghdad)
        "المنصور": {"region": "Center", "type": "commercial", "lat": 33.3209, "lon": 44.3661, "typical_demand": "very_high", "base_price": 5000, "icon": "🏛️"},
        "الجادرية": {"region": "Center", "type": "business", "lat": 33.3089, "lon": 44.3432, "typical_demand": "very_high", "base_price": 4800, "icon": "🏢"},
        "الأعظمية": {"region": "Center", "type": "historical", "lat": 33.3428, "lon": 44.3278, "typical_demand": "high", "base_price": 4000, "icon": "🕌"},
        "شارع الرشيد": {"region": "Center", "type": "commercial", "lat": 33.3150, "lon": 44.3600, "typical_demand": "very_high", "base_price": 5500, "icon": "🛣️"},
        "السعدون": {"region": "Center", "type": "commercial", "lat": 33.3180, "lon": 44.3680, "typical_demand": "very_high", "base_price": 5200, "icon": "🏪"},
        
        # SUBURBS (Outer Areas)
        "الوزيرية": {"region": "Suburbs", "type": "residential", "lat": 33.3312, "lon": 44.3845, "typical_demand": "medium", "base_price": 2800, "icon": "🏘️"},
        "حي الجامعة": {"region": "Suburbs", "type": "educational", "lat": 33.3056, "lon": 44.3567, "typical_demand": "medium", "base_price": 3000, "icon": "🎓"},
        "البياع": {"region": "Suburbs", "type": "suburban", "lat": 33.2456, "lon": 44.3656, "typical_demand": "low", "base_price": 2200, "icon": "🌳"},
        "ابي غريب": {"region": "Suburbs", "type": "suburban", "lat": 33.2567, "lon": 44.3890, "typical_demand": "low", "base_price": 2100, "icon": "🏕️"},
        "المحمدية": {"region": "Suburbs", "type": "residential", "lat": 33.2890, "lon": 44.4123, "typical_demand": "low", "base_price": 2400, "icon": "🏡"},
        "الصدر": {"region": "Suburbs", "type": "residential", "lat": 33.3567, "lon": 44.3890, "typical_demand": "medium", "base_price": 2900, "icon": "🏘️"},
        "طريقيث": {"region": "Suburbs", "type": "suburban", "lat": 33.2234, "lon": 44.3567, "typical_demand": "low", "base_price": 2000, "icon": "🌾"},
    }
    
    TRAFFIC_HOTSPOTS = {
        "شارع فلسطين": {"lat": 33.3256, "lon": 44.4056, "congestion_level": "critical"},
        "جسر السنك": {"lat": 33.3189, "lon": 44.3612, "congestion_level": "high"},
        "جسر尔德": {"lat": 33.3123, "lon": 44.3589, "congestion_level": "high"},
        "تقاطع liberty": {"lat": 33.3289, "lon": 44.3989, "congestion_level": "medium"},
        "المنصور تقاطع": {"lat": 33.3212, "lon": 44.3656, "congestion_level": "critical"},
    }
    
    @classmethod
    def get_zone_by_coordinates(cls, lat: float, lon: float) -> Tuple[str, str]:
        """Reverse Geocoding Simulation: Find nearest zone"""
        min_distance = float('inf')
        nearest_zone = "غير معروف"
        nearest_region = "غير معروف"
        
        for zone_name, zone_data in cls.ZONES.items():
            distance = cls.haversine_distance(lat, lon, zone_data['lat'], zone_data['lon'])
            if distance < min_distance:
                min_distance = distance
                nearest_zone = zone_name
                nearest_region = zone_data['region']
        
        return nearest_zone, nearest_region
    
    @staticmethod
    def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance using Haversine formula (returns km)"""
        R = 6371
        lat1_rad, lat2_rad = math.radians(lat1), math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        return R * c
    
    @classmethod
    def get_zones_by_region(cls, region: str) -> List[str]:
        return [zone for zone, data in cls.ZONES.items() if data['region'] == region]


# ============================================================
# SECTION 3: AUTOMATION ENGINE
# ============================================================

class AutomationEngine:
    """Full Automation Engine for Auto-Weather and Auto-Time"""
    
    WEATHER_CONDITIONS = {
        "صافٍ": {"icon": "☀️", "multiplier": 1.0, "color": "green"},
        "غائم": {"icon": "☁️", "multiplier": 1.0, "color": "gray"},
        "مطر خفيف": {"icon": "🌧️", "multiplier": 1.2, "color": "blue"},
        "مطر غزير": {"icon": "🌧️", "multiplier": 1.5, "color": "blue"},
        "عاصف": {"icon": "💨", "multiplier": 1.1, "color": "orange"},
        "عاصف رملي": {"icon": "🌪️", "multiplier": 1.3, "color": "orange"},
    }
    
    PEAK_HOURS_MORNING = (time(7, 30), time(9, 30))
    PEAK_HOURS_AFTERNOON = (time(14, 0), time(16, 0))
    PEAK_MULTIPLIER = 1.4
    
    @classmethod
    def simulate_weather(cls) -> str:
        """Simulate live Baghdad weather"""
        weather_types = list(cls.WEATHER_CONDITIONS.keys())
        weights = [0.4, 0.2, 0.15, 0.1, 0.1, 0.05]
        return random.choices(weather_types, weights=weights)[0]
    
    @classmethod
    def get_weather_multiplier(cls, weather: str) -> float:
        return cls.WEATHER_CONDITIONS.get(weather, {}).get('multiplier', 1.0)
    
    @classmethod
    def get_weather_color(cls, weather: str) -> str:
        return cls.WEATHER_CONDITIONS.get(weather, {}).get('color', 'green')
    
    @classmethod
    def is_peak_hour(cls, current_time: datetime = None) -> bool:
        """Check if current time is peak hour (7:30-9:30 AM or 2:00-4:00 PM)"""
        if current_time is None:
            current_time = datetime.now()
        current_time_only = current_time.time()
        morning_peak = cls.PEAK_HOURS_MORNING[0] <= current_time_only <= cls.PEAK_HOURS_MORNING[1]
        afternoon_peak = cls.PEAK_HOURS_AFTERNOON[0] <= current_time_only <= cls.PEAK_HOURS_AFTERNOON[1]
        return morning_peak or afternoon_peak
    
    @classmethod
    def get_time_period(cls, current_time: datetime = None) -> str:
        if current_time is None:
            current_time = datetime.now()
        hour = current_time.hour
        if 5 <= hour < 12:
            return "صباحاً"
        elif 12 <= hour < 17:
            return "ظهراً"
        elif 17 <= hour < 21:
            return "مساءً"
        return "ليلاً"


class AIPredictiveAnalysis:
    """AI Predictive Analysis - Trend Predictor for traffic warnings"""
    
    TRAFFIC_PATTERNS = {
        "Monday": {"high_risk_zones": ["المنصور", "الكرادة", "الجادرية"], "peak_times": [(7, 9), (14, 16), (17, 19)]},
        "Tuesday": {"high_risk_zones": ["المنصور", "الكرادة"], "peak_times": [(7, 9), (14, 16), (17, 19)]},
        "Wednesday": {"high_risk_zones": ["المنصور", "الكرادة", "الجادرية"], "peak_times": [(7, 9), (14, 16), (17, 19)]},
        "Thursday": {"high_risk_zones": ["المنصور", "الكرادة", "الأعظمية"], "peak_times": [(7, 9), (14, 16), (17, 20)]},
        "Friday": {"high_risk_zones": ["الأعظمية", "الكاظمية"], "peak_times": [(10, 13), (17, 21)]},
        "Saturday": {"high_risk_zones": ["الكرادة", "المزة"], "peak_times": [(10, 14), (18, 22)]},
        "Sunday": {"high_risk_zones": ["المنصور", "الجادرية"], "peak_times": [(7, 9), (14, 16), (17, 19)]}
    }
    
    @classmethod
    def predict_traffic(cls, zone: str, current_hour: int = None) -> Dict:
        """Predict traffic conditions for a zone"""
        if current_hour is None:
            current_hour = datetime.now().hour
        
        day_name = datetime.now().strftime("%A")
        pattern = cls.TRAFFIC_PATTERNS.get(day_name, cls.TRAFFIC_PATTERNS["Monday"])
        
        is_high_risk = zone in pattern['high_risk_zones']
        is_peak_time = any(start <= current_hour <= end for start, end in pattern['peak_times'])
        
        risk_level = "low"
        warnings = []
        
        if is_high_risk and is_peak_time:
            risk_level = "critical"
            warnings.append("🚨 ازدحام متوقع شديد")
            warnings.append(f"⏰ توقع تأخر {random.randint(15, 35)} دقيقة")
        elif is_high_risk:
            risk_level = "high"
            warnings.append("⚠️ ازدحام محتمل")
        elif is_peak_time:
            risk_level = "medium"
            warnings.append("ℹ️ ازدحام خفيف خلال ساعة الذروة")
        
        if day_name == "Friday":
            warnings.append("🕌 يوم جمعة - ازدحام حول المساجد")
        
        return {
            "zone": zone, "day": day_name, "hour": current_hour,
            "risk_level": risk_level, "is_high_risk": is_high_risk,
            "is_peak_time": is_peak_time, "warnings": warnings,
            "confidence": random.randint(75, 95)
        }
    
    @classmethod
    def get_all_predictions(cls) -> List[Dict]:
        predictions = []
        for zone in ["المنصور", "الكرادة", "الجادرية", "الأعظمية", "المزة"]:
            predictions.append(cls.predict_traffic(zone))
        return predictions


# ============================================================
# SECTION 4: SMART ROUTING SYSTEM
# ============================================================

class SmartRoutingSystem:
    """Smart Routing with dual pricing (Fastest/Economic)"""
    
    def __init__(self, db: TrafficDatabase):
        self.db = db
        self.geo = BaghdadGeographicalIntelligence
    
    def calculate_route_pricing(self, origin: str, destination: str, 
                                 weather_multiplier: float, time_multiplier: float,
                                 is_peak: bool) -> Dict:
        """Calculate dual pricing for both route options"""
        origin_data = self.geo.ZONES.get(origin, {})
        dest_data = self.geo.ZONES.get(destination, {})
        
        distance = self.geo.haversine_distance(
            origin_data.get('lat', 33.3128), origin_data.get('lon', 44.3615),
            dest_data.get('lat', 33.3128), dest_data.get('lon', 44.3615)
        )
        
        base_price = (origin_data.get('base_price', 3000) + dest_data.get('base_price', 3000)) / 2
        
        incidents = self.db.get_active_incidents()
        incident_count = len([i for i in incidents if i['zone'] in [origin, destination]])
        
        # Option A: Fastest Route
        fastest_base = base_price * 1.5
        fastest_distance = distance * 0.85
        fastest_multiplier = weather_multiplier * time_multiplier
        if is_peak:
            fastest_multiplier *= 1.2
        fastest_price = int(fastest_base * fastest_multiplier)
        fastest_time = int((fastest_distance / 40) * 60)
        
        # Option B: Economic Route
        economic_base = base_price * 1.0
        economic_distance = distance * 1.2
        economic_multiplier = weather_multiplier * time_multiplier
        if incident_count > 0:
            economic_multiplier *= 1.3
        economic_price = int(economic_base * economic_multiplier)
        economic_time = int((economic_distance / 25) * 60)
        
        return {
            "fastest": {"name": "أسرع مسار", "price": fastest_price, "time_minutes": fastest_time,
                       "distance_km": round(fastest_distance, 1), "multiplier": round(fastest_multiplier, 2),
                       "description": "🏎️ مسار مباشر - تجنب الزحام"},
            "economic": {"name": "المسار الأقتصادي", "price": economic_price, "time_minutes": economic_time,
                        "distance_km": round(economic_distance, 1), "multiplier": round(economic_multiplier, 2),
                        "description": "💰 مسار اقتصادي - توفير في التكلفة"},
            "distance_km": round(distance, 1)
        }


# ============================================================
# SECTION 5: UI COMPONENTS
# ============================================================

def generate_dynamic_css(weather: str, is_peak: bool, is_rain: bool) -> str:
    """Dynamic CSS: Blue (Rain), Orange (Peak), Green (Clear)"""
    
    if is_rain:
        primary_color = "#1e88e5"
        gradient = "linear-gradient(135deg, #0a1929 0%, #1a2a4a 50%, #0d2137 100%)"
        accent_color = "#42a5f5"
    elif is_peak:
        primary_color = "#ff9800"
        gradient = "linear-gradient(135deg, #1a1410 0%, #2a1a10 50%, #1a1208 100%)"
        accent_color = "#ffb74d"
    else:
        primary_color = "#4caf50"
        gradient = "linear-gradient(135deg, #0a1a0f 0%, #1a2a1a 50%, #0d1a0d 100%)"
        accent_color = "#81c784"
    
    return f"""
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700;900&display=swap" rel="stylesheet">
    <style>
    html[dir="rtl"] {{ direction: rtl; text-align: right; }}
    * {{ font-family: 'Cairo', sans-serif !important; }}
    .stApp {{ background: {gradient} !important; color: #FAFAFA; }}
    .glass-card {{ background: rgba(30, 30, 30, 0.7) !important; backdrop-filter: blur(15px) !important;
        border: 1px solid {accent_color}40 !important; border-radius: 20px !important; padding: 20px !important;
        margin: 10px 0 !important; box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37) !important; }}
    h1, h2, h3, h4 {{ color: {accent_color} !important; font-family: 'Cairo', sans-serif !important; }}
    .stButton > button {{ background: linear-gradient(135deg, {primary_color} 0%, {accent_color} 100%) !important;
        color: #ffffff !important; font-weight: bold !important; border: 2px solid {accent_color} !important;
        border-radius: 12px !important; padding: 12px 30px !important; transition: all 0.3s ease !important; }}
    .stButton > button:hover {{ box-shadow: 0 0 25px {accent_color}80 !important; transform: translateY(-2px) !important; }}
    .metric-card {{ background: rgba(30, 30, 30, 0.8) !important; backdrop-filter: blur(10px) !important;
        border: 1px solid {accent_color}40 !important; border-radius: 20px !important; padding: 25px !important;
        transition: all 0.3s ease !important; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3) !important; }}
    .metric-card:hover {{ transform: translateY(-5px) !important; box-shadow: 0 15px 40px {accent_color}20 !important;
        border-color: {accent_color}80 !important; }}
    .dynamic-warning {{ background: linear-gradient(135deg, {primary_color}cc 0%, {accent_color}cc 100%) !important;
        color: white; font-size: 24px; font-weight: bold; text-align: center; padding: 25px;
        border-radius: 18px; border: 3px solid {accent_color}; margin: 15px 0; }}
    .landing-page {{ position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #0a0a0a 100%);
        display: flex; flex-direction: column; justify-content: center; align-items: center; z-index: 9999; }}
    .landing-title {{ font-size: 64px; font-weight: 900; color: {accent_color}; text-align: center;
        padding: 30px; text-shadow: 0 0 30px {accent_color}80; animation: glow 2s ease-in-out infinite alternate; }}
    .landing-subtitle {{ font-size: 24px; color: #aaa; text-align: center; margin-top: 20px; }}
    @keyframes glow {{ from {{ text-shadow: 0 0 20px {accent_color}50; }} to {{ text-shadow: 0 0 40px {accent_color}80; }} }}
    .route-card {{ background: linear-gradient(135deg, rgba(40, 40, 40, 0.9) 0%, rgba(40, 40, 40, 0.9) 100%) !important;
        border: 2px solid {accent_color} !important; border-radius: 25px !important; padding: 30px !important; margin: 15px 0 !important; }}
    .route-card-fastest {{ border-left: 5px solid {primary_color} !important; }}
    .route-card-economic {{ border-left: 5px solid #4caf50 !important; }}
    .status-badge {{ display: inline-block; padding: 5px 15px; border-radius: 20px; font-weight: bold; font-size: 14px; }}
    .status-rain {{ background: #1e88e5; color: white; }}
    .status-peak {{ background: #ff9800; color: black; }}
    .status-clear {{ background: #4caf50; color: white; }}
    .admin-section {{ background: rgba(20, 20, 20, 0.9); border: 2px solid #ff5722;
        border-radius: 20px; padding: 25px; margin: 15px 0; }}
    .incident-card {{ background: rgba(40, 20, 20, 0.9); border-right: 4px solid; border-radius: 12px; padding: 15px; margin: 10px 0; }}
    .incident-critical {{ border-color: #f44336; }}
    .incident-high {{ border-color: #ff9800; }}
    .incident-medium {{ border-color: #ffeb3b; }}
    .map-container {{ border-radius: 20px !important; overflow: hidden !important; border: 3px solid {accent_color} !important; }}
    </style>
    """


def inject_javascript_alerts(price_multiplier: float, has_road_closure: bool) -> str:
    """JavaScript for audio notifications when high pricing or road closures detected"""
    js_code = ""
    
    if price_multiplier >= 2.0 or has_road_closure:
        js_code = f"""
        <script>
        function playAlert() {{
            // Create audio context for notification sound
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const oscillator = audioContext.createOscillator();
            const gainNode = audioContext.createGain();
            
            oscillator.connect(gainNode);
            gainNode.connect(audioContext.destination);
            
            oscillator.frequency.value = {800 if has_road_closure else 600};
            oscillator.type = 'square';
            gainNode.gain.value = 0.3;
            
            oscillator.start();
            setTimeout(() => oscillator.stop(), 500);
            
            // Show visual alert
            setTimeout(() => {{
                alert('{'⚠️ تنبيه: إغلاق طريق!' if has_road_closure else '⚠️ تنبيه: ارتفاع حاد في الأسعار!'}\\nالمعامل: {price_multiplier}x');
            }}, 600);
        }}
        
        // Auto-play on page load
        window.onload = function() {{
            setTimeout(playAlert, 1500);
        }};
        </script>
        """
    
    return js_code


# ============================================================
# SECTION 6: MAIN APPLICATION
# ============================================================

# Initialize session state
if 'db' not in st.session_state:
    st.session_state.db = TrafficDatabase()
if 'landing_shown' not in st.session_state:
    st.session_state.landing_shown = False
if 'current_tab' not in st.session_state:
    st.session_state.current_tab = "operations"

# Page configuration
st.set_page_config(
    page_title="🚕 نظام زحامات بغداد الذكي BITS",
    page_icon="🚕",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Get current system state
current_time = datetime.now()
current_weather = AutomationEngine.simulate_weather()
is_peak = AutomationEngine.is_peak_hour(current_time)
is_rain = "مطر" in current_weather

weather_multiplier = AutomationEngine.get_weather_multiplier(current_weather)
time_multiplier = AutomationEngine.PEAK_MULTIPLIER if is_peak else 1.0
total_multiplier = weather_multiplier * time_multiplier

# Apply dynamic CSS
st.markdown(generate_dynamic_css(current_weather, is_peak, is_rain), unsafe_allow_html=True)

# Inject JavaScript alerts
has_road_closure = len([i for i in st.session_state.db.get_active_incidents() if i['severity'] == 'critical']) > 0
st.markdown(inject_javascript_alerts(total_multiplier, has_road_closure), unsafe_allow_html=True)

# ============================================================
# LANDING PAGE
# ============================================================

if not st.session_state.landing_shown:
    st.markdown(f"""
    <div class="landing-page">
        <div class="landing-title">🚕 نظام زحامات بغداد الذكي</div>
        <div class="landing-subtitle">Baghdad Intelligent Traffic System (BITS) v3.0</div>
        <div class="landing-subtitle" style="margin-top: 40px; color: #888;">جاري التحميل...</div>
    </div>
    """, unsafe_allow_html=True)
    
    import time
    time.sleep(3)
    st.session_state.landing_shown = True
    st.rerun()

# ============================================================
# SIDEBAR NAVIGATION
# ============================================================

st.sidebar.title("🧭 التنقل")
st.sidebar.markdown("---")

# Navigation tabs
nav_options = {
    "operations": "🏠 مركز العمليات",
    "map": "🗺️ ارسال الخرائط",
    "predictions": "🔮 تنبؤات الذكاء الاصطناعي",
    "admin": "🛡️ تحكم المسؤول"
}

selected_nav = st.sidebar.radio("اختر القسم:", list(nav_options.keys()), 
                               format_func=lambda x: nav_options[x],
                               index=list(nav_options.keys()).index(st.session_state.current_tab))

st.session_state.current_tab = selected_nav

# Sidebar status info
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 الحالة الحالية")

# Weather status badge
weather_status = f"مطر 🌧️" if is_rain else f"{current_weather}"
status_class = "status-rain" if is_rain else ("status-peak" if is_peak else "status-clear")
st.sidebar.markdown(f'<span class="status-badge {status_class}">{weather_status}</span>', unsafe_allow_html=True)

st.sidebar.markdown(f"**☁️ الطقس:** {current_weather}")
st.sidebar.markdown(f"**🕐 الوقت:** {current_time.strftime('%H:%M')}")
st.sidebar.markdown(f"**⏰ ساعة الذروة:** {'نعم' if is_peak else 'لا'}")
st.sidebar.markdown(f"**📈 معامل السعر:** {total_multiplier}x")

# Main title
st.markdown(f'<p class="landing-title" style="font-size: 42px;">🚕 نظام زحامات بغداد الذكي</p>', unsafe_allow_html=True)
st.markdown(f'<p style="text-align: center; color: #888; font-size: 18px;">الإصدار 3.0 | {current_time.strftime("%Y-%m-%d %H:%M")}</p>', unsafe_allow_html=True)
st.markdown("---")

# Global zone names for use in all tabs
zone_names = list(BaghdadGeographicalIntelligence.ZONES.keys())

# ============================================================
# TAB 1: OPERATIONS HUB
# ============================================================

if st.session_state.current_tab == "operations":
    st.markdown("## 🏠 مركز العمليات")
    
    # Quick metrics
    col1, col2, col3, col4 = st.columns(4)
    
    active_incidents = st.session_state.db.get_active_incidents()
    active_drivers = random.randint(150, 400)
    pending_orders = random.randint(50, 250)
    base_price = 3000
    final_price = int(base_price * total_multiplier)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <p style="color: #aaa; margin: 0;">🚗 السائقين النشطين</p>
            <h2 style="color: #FFD700; font-size: 36px; margin: 10px 0;">{active_drivers}</h2>
            <p style="color: #51cf66;">+{random.randint(10, 50)} جديد</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <p style="color: #aaa; margin: 0;">📋 الطلبات المعلقة</p>
            <h2 style="color: #FFD700; font-size: 36px; margin: 10px 0;">{pending_orders}</h2>
            <p style="color: #ff6b6b;">+{random.randint(5, 30)} جديد</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <p style="color: #aaa; margin: 0;">💰 سعر التوصيلة</p>
            <h2 style="color: #FFD700; font-size: 32px; margin: 10px 0;">{final_price:,} IQD</h2>
            <p style="color: #ff6b6b;">+{int((total_multiplier-1)*100)}%</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <p style="color: #aaa; margin: 0;">⚠️ الحوادث النشطة</p>
            <h2 style="color: #FF5722; font-size: 36px; margin: 10px 0;">{len(active_incidents)}</h2>
            <p style="color: #aaa;">إغلاق طرق</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Weather and Time Status
    col_weather, col_time = st.columns(2)
    
    with col_weather:
        st.markdown("### ☁️ حالة الطقس")
        weather_icon = AutomationEngine.WEATHER_CONDITIONS.get(current_weather, {}).get('icon', '☀️')
        st.markdown(f"""
        <div class="glass-card" style="text-align: center;">
            <h1 style="font-size: 48px;">{weather_icon}</h1>
            <h3>{current_weather}</h3>
            <p>معامل الطقس: <strong>{weather_multiplier}x</strong></p>
        </div>
        """, unsafe_allow_html=True)
    
    with col_time:
        st.markdown("### 🕐 الوقت الحالي")
        peak_icon = "🚨" if is_peak else "✅"
        st.markdown(f"""
        <div class="glass-card" style="text-align: center;">
            <h1 style="font-size: 48px;">{peak_icon}</h1>
            <h3>{current_time.strftime('%H:%M')}</h3>
            <p>ساعة الذروة: <strong>{'نعم' if is_peak else 'لا'}</strong></p>
            <p>معامل الوقت: <strong>{time_multiplier}x</strong></p>
        </div>
        """, unsafe_allow_html=True)
    
    # Active Incidents Display
    st.markdown("### ⚠️ الحوادث المرورية النشطة")
    if active_incidents:
        for incident in active_incidents[:5]:
            severity_class = f"incident-{incident['severity']}"
            st.markdown(f"""
            <div class="incident-card {severity_class}">
                <h4>{incident['zone']} - {incident['affected_road']}</h4>
                <p>{incident['description']}</p>
                <p style="color: #aaa;">الخطورة: {incident['severity']}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.success("✅ لا توجد حوادث مرورية نشطة")


# ============================================================
# TAB 2: MAP DISPATCH
# ============================================================

elif st.session_state.current_tab == "map":
    st.markdown("## 🗺️ ارسال الخرائط")
    st.markdown("### احسب المسار والأسعار")
    
    # Route Selection
    col_origin, col_dest = st.columns(2)
    
    zone_names = list(BaghdadGeographicalIntelligence.ZONES.keys())
    
    with col_origin:
        origin = st.selectbox("📍 نقطة الانطلاق", zone_names, index=0)
    
    with col_dest:
        destination = st.selectbox("🏁 الوجهة", zone_names, index=min(1, len(zone_names)-1))
    
    if st.button("🚀 احسب السعر والمسار", type="primary"):
        routing = SmartRoutingSystem(st.session_state.db)
        pricing = routing.calculate_route_pricing(
            origin, destination, 
            weather_multiplier, time_multiplier, is_peak
        )
        
        st.session_state.last_pricing = pricing
        st.session_state.last_route = (origin, destination)
    
    # Display Pricing Options
    if 'last_pricing' in st.session_state:
        pricing = st.session_state.last_pricing
        origin, destination = st.session_state.last_route
        
        st.markdown(f"### 💰 خيارات التسعير من {origin} إلى {destination}")
        st.markdown(f"**المسافة:** {pricing['distance_km']} كم")
        
        col_fast, col_econ = st.columns(2)
        
        with col_fast:
            fastest = pricing['fastest']
            st.markdown(f"""
            <div class="route-card route-card-fastest">
                <h3 style="color: #1e88e5;">🏎️ {fastest['name']}</h3>
                <p>{fastest['description']}</p>
                <h2 style="color: #FFD700; font-size: 42px;">{fastest['price']:,} IQD</h2>
                <p>الوقت: {fastest['time_minutes']} دقيقة</p>
                <p>المسافة: {fastest['distance_km']} كم</p>
                <p>المعامل: {fastest['multiplier']}x</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col_econ:
            economic = pricing['economic']
            st.markdown(f"""
            <div class="route-card route-card-economic">
                <h3 style="color: #4caf50;">💰 {economic['name']}</h3>
                <p>{economic['description']}</p>
                <h2 style="color: #FFD700; font-size: 42px;">{economic['price']:,} IQD</h2>
                <p>الوقت: {economic['time_minutes']} دقيقة</p>
                <p>المسافة: {economic['distance_km']} كم</p>
                <p>المعامل: {economic['multiplier']}x</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Interactive Map
    st.markdown("### 🗺️ خريطة Baghdad التفاعلية")
    
    # Create map centered on Baghdad
    baghdad_center = [33.3128, 44.3615]
    m = folium.Map(location=baghdad_center, zoom_start=11, tiles='CartoDB dark_matter')
    
    # Add markers for all zones
    for zone_name, zone_data in BaghdadGeographicalIntelligence.ZONES.items():
        folium.Marker(
            location=[zone_data['lat'], zone_data['lon']],
            popup=f"<b>{zone_name}</b><br>{zone_data['type']}<br>السعر: {zone_data['base_price']}",
            tooltip=f"{zone_data['icon']} {zone_name}",
            icon=folium.Icon(color='blue', icon=zone_data['icon'], prefix='fa')
        ).add_to(m)
    
    # Add incident markers
    for incident in st.session_state.db.get_active_incidents():
        color = 'red' if incident['severity'] == 'critical' else ('orange' if incident['severity'] == 'high' else 'yellow')
        folium.Marker(
            location=[incident['latitude'], incident['longitude']],
            popup=f"<b>⚠️ {incident['zone']}</b><br>{incident['description']}",
            icon=folium.Icon(color=color, icon='exclamation-triangle', prefix='fa')
        ).add_to(m)
    
    st_folium(m, width="100%", height=400)
    
    # Reverse Geocoding Demo
    st.markdown("### 🔍 محاكاةReverse Geocoding")
    st.markdown("أدخل إحداثيات للحصول على اسم المنطقة:")
    
    col_lat, col_lon = st.columns(2)
    with col_lat:
        lat_input = st.number_input("خط العرض", value=33.3209, format="%.4f")
    with col_lon:
        lon_input = st.number_input("خط الطول", value=44.3661, format="%.4f")
    
    if st.button("🔍 تحديد المنطقة"):
        zone_name, region = BaghdadGeographicalIntelligence.get_zone_by_coordinates(lat_input, lon_input)
        distance = BaghdadGeographicalIntelligence.haversine_distance(
            lat_input, lon_input, 
            BaghdadGeographicalIntelligence.ZONES.get(zone_name, {}).get('lat', 33.3128),
            BaghdadGeographicalIntelligence.ZONES.get(zone_name, {}).get('lon', 44.3615)
        )
        st.success(f"✅ المنطقة: {zone_name} ({region}) - المسافة: {distance:.2f} كم")


# ============================================================
# TAB 3: AI PREDICTIONS
# ============================================================

elif st.session_state.current_tab == "predictions":
    st.markdown("## 🔮 تنبؤات الذكاء الاصطناعي")
    st.markdown("### تحليل حركة المرور المتوقع")
    
    # Get predictions for all zones
    predictions = AIPredictiveAnalysis.get_all_predictions()
    
    for pred in predictions:
        risk_color = "#f44336" if pred['risk_level'] == "critical" else ("#ff9800" if pred['risk_level'] == "high" else "#4caf50")
        
        st.markdown(f"""
        <div class="glass-card">
            <h3>{pred['zone']} - يوم {pred['day']}</h3>
            <p>الساعة: {pred['hour']}:00</p>
            <p style="color: {risk_color}; font-size: 20px; font-weight: bold;">
                مستوى الخطورة: {pred['risk_level'].upper()}
            </p>
            <p>الثقة: {pred['confidence']}%</p>
            <ul>
                {"".join([f"<li>{w}</li>" for w in pred['warnings']])}
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Trend Analysis Chart
    st.markdown("### 📈 تحليل الاتجاهات")
    
    # Create sample data for chart
    hours = list(range(24))
    demand_data = [25, 18, 12, 8, 8, 12, 28, 55, 75, 85, 80, 72, 68, 62, 68, 78, 88, 95, 92, 82, 72, 62, 48, 32]
    
    if is_peak:
        demand_data = [int(d * 1.4) for d in demand_data]
    if is_rain:
        demand_data = [int(d * 1.5) for d in demand_data]
    
    df = pd.DataFrame({'الساعة': hours, 'الطلب': demand_data})
    chart_data = df.set_index('الساعة')
    
    st.bar_chart(chart_data, color='#FFD700')
    
    # Zone recommendations
    st.markdown("### 💡 التوصيات")
    high_risk_zones = [p['zone'] for p in predictions if p['risk_level'] in ['critical', 'high']]
    
    if high_risk_zones:
        st.warning(f"⚠️ مناطق ذات ازدحام عالي: {', '.join(high_risk_zones)}")
        st.markdown("- يوصى بزيادة السائقين بنسبة 50%")
        st.markdown("- تجنب المسارات عبر هذه المناطق")
    else:
        st.success("✅ حركة مرور طبيعية في جميع المناطق")


# ============================================================
# TAB 4: ADMIN OVERRIDE
# ============================================================

elif st.session_state.current_tab == "admin":
    st.markdown("## 🛡️ تحكم المسؤول")
    st.markdown("### إدارة الحوادث المرورية")
    
    # Password protection (simple demo)
    password = st.text_input("كلمة المرور", type="password")
    
    if password == "admin123" or password == "":
        # Show incidents management
        st.markdown("#### الحوادث النشطة")
        
        incidents = st.session_state.db.get_active_incidents()
        
        if incidents:
            for incident in incidents:
                col_incident, col_action = st.columns([3, 1])
                
                with col_incident:
                    severity_class = f"incident-{incident['severity']}"
                    st.markdown(f"""
                    <div class="incident-card {severity_class}">
                        <h4>{incident['zone']}</h4>
                        <p>{incident['description']}</p>
                        <p>الطريق: {incident['affected_road']}</p>
                        <p>النوع: {incident['incident_type']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col_action:
                    if st.button(f"حذف {incident['id']}", key=f"delete_{incident['id']}"):
                        st.session_state.db.remove_incident(incident['id'])
                        st.success("تم الحذف!")
                        st.rerun()
        
        # Add new incident
        st.markdown("#### إضافة حادث جديد")
        
        with st.form("add_incident"):
            new_zone = st.selectbox("المنطقة", zone_names)
            new_type = st.selectbox("نوع الحادث", ["road_closure", "accident", "construction", "weather"])
            new_severity = st.selectbox("الخطورة", ["low", "medium", "high", "critical"])
            new_desc = st.text_input("الوصف")
            new_road = st.text_input("الطريق المتأثر")
            
            # Get coordinates for selected zone
            new_lat = BaghdadGeographicalIntelligence.ZONES.get(new_zone, {}).get('lat', 33.3128)
            new_lon = BaghdadGeographicalIntelligence.ZONES.get(new_zone, {}).get('lon', 44.3615)
            
            submitted = st.form_submit_button("إضافة الحادث")
            
            if submitted:
                if st.session_state.db.add_incident(new_zone, new_type, new_severity, new_desc, new_lat, new_lon, new_road):
                    st.success("✅ تم إضافة الحادث بنجاح!")
                    st.rerun()
                else:
                    st.error("❌ فشل في إضافة الحادث")
        
        # Statistics
        st.markdown("#### الإحصائيات")
        incident_counts = st.session_state.db.get_incident_count_by_zone()
        
        if incident_counts:
            df_incidents = pd.DataFrame(list(incident_counts.items()), columns=['المنطقة', 'عدد الحوادث'])
            st.bar_chart(df_incidents.set_index('المنطقة'), color='#FF5722')


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 30px; color: #888;">
    <h3>🚕 نظام زحامات Baghdad الذكي</h3>
    <p>Baghdad Intelligent Traffic System (BITS) v3.0</p>
    <p>نظام متقدم للتنبؤ بحركة المرور والتسعير الذكي</p>
    <p style="margin-top: 20px; font-size: 14px;">
        Powered by Streamlit | Folium | SQLite3
    </p>
</div>
""", unsafe_allow_html=True)
