# vodafone_api.py
"""
محاكاة واجهة برمجة تطبيقات فودافون مصر
(للأغراض التعليمية - تحتاج API حقيقي للإنتاج)
"""

import random
import time
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple

class VodafoneEgyptAPI:
    """محاكاة API فودافون مصر"""
    
    def __init__(self):
        self.base_url = "https://api.vodafone.com.eg"
        self.session_timeout = 300
        
        # قوالب بيانات وهمية
        self.packages = {
            "internet": {
                "VIP_10GB": {"price": 100, "data": "10GB", "validity": 30},
                "MEGA_5GB": {"price": 60, "data": "5GB", "validity": 30},
                "BASIC_2GB": {"price": 30, "data": "2GB", "validity": 15},
                "DAILY_1GB": {"price": 10, "data": "1GB", "validity": 1}
            },
            "minutes": {
                "ALL_NET_100": {"price": 25, "minutes": 100, "validity": 7},
                "VODAFONE_200": {"price": 15, "minutes": 200, "validity": 7},
                "INTERNATIONAL_30": {"price": 30, "minutes": 30, "validity": 30}
            },
            "balance": {
                "CHARGE_10": {"amount": 10},
                "CHARGE_20": {"amount": 20},
                "CHARGE_50": {"amount": 50},
                "CHARGE_100": {"amount": 100}
            }
        }
    
    def authenticate(self, phone_number: str, password: str) -> Dict:
        """محاكاة تسجيل الدخول"""
        # في الواقع: طلب POST لـ https://api.vodafone.com.eg/auth
        time.sleep(1)  # محاكاة زمن الاستجابة
        
        # بيانات وهمية للمستخدم
        user_data = {
            "user_id": f"VOD_{phone_number[-6:]}",
            "msisdn": phone_number,
            "name": f"عميل فودافون {phone_number[-4:]}",
            "balance": random.uniform(5, 200),
            "remaining_internet": f"{random.randint(1, 20)}GB",
            "remaining_minutes": random.randint(10, 300),
            "package": random.choice(["VIP", "MEGA", "BASIC"]),
            "expiry_date": (datetime.now() + timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%d")
        }
        
        return {
            "success": True,
            "message": "تم تسجيل الدخول بنجاح",
            "data": user_data,
            "session_token": f"VOD_SESSION_{random.randint(100000, 999999)}"
        }
    
    def get_user_info(self, phone_number: str) -> Dict:
        """محاكاة استعلام بيانات المستخدم"""
        return {
            "success": True,
            "data": {
                "msisdn": phone_number,
                "balance": round(random.uniform(10, 150), 2),
                "internet_balance": f"{random.randint(1, 15)}.{random.randint(0, 99)} GB",
                "local_minutes": random.randint(20, 200),
                "international_minutes": random.randint(0, 30),
                "sms_balance": random.randint(10, 100),
                "current_package": random.choice(["كول توك", "إنترنت بلس", "باقة شاملة"]),
                "package_expiry": (datetime.now() + timedelta(days=random.randint(1, 15))).strftime("%Y-%m-%d"),
                "last_recharge": (datetime.now() - timedelta(days=random.randint(1, 7))).strftime("%Y-%m-%d"),
                "status": "نشط"
            }
        }
    
    def transfer_internet(self, from_number: str, to_number: str, amount: str) -> Dict:
        """محاكاة تحويل إنترنت"""
        # amount مثل: "1GB", "500MB"
        return {
            "success": True,
            "message": f"تم تحويل {amount} إنترنت بنجاح",
            "transaction_id": f"INT_TRX_{random.randint(1000000, 9999999)}",
            "from": from_number,
            "to": to_number,
            "amount": amount,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "remaining_balance": f"{random.randint(1, 10)}.{random.randint(0, 99)} GB"
        }
    
    def transfer_minutes(self, from_number: str, to_number: str, minutes: int) -> Dict:
        """محاكاة تحويل دقائق"""
        return {
            "success": True,
            "message": f"تم تحويل {minutes} دقيقة بنجاح",
            "transaction_id": f"MIN_TRX_{random.randint(1000000, 9999999)}",
            "remaining_minutes": random.randint(10, 100)
        }
    
    def recharge_balance(self, phone_number: str, amount: float, method: str = "VODAFONE_CASH") -> Dict:
        """محاكاة شحن رصيد"""
        return {
            "success": True,
            "message": f"تم شحن {amount} جنيه بنجاح",
            "new_balance": round(random.uniform(amount, amount + 50), 2),
            "receipt_number": f"RCPT{random.randint(100000, 999999)}",
            "payment_method": method
        }
    
    def change_package(self, phone_number: str, package_name: str) -> Dict:
        """محاكاة تغيير الباقة"""
        return {
            "success": True,
            "message": f"تم التغيير إلى باقة {package_name}",
            "new_package": package_name,
            "activation_date": datetime.now().strftime("%Y-%m-%d"),
            "monthly_cost": random.randint(50, 200)
        }
    
    def get_offers(self, phone_number: str) -> Dict:
        """محاكاة العروض المتاحة"""
        offers = [
            {"id": 1, "name": "عرض الليلة", "description": "10GB بـ 50 جنيه", "price": 50, "validity": "24 ساعة"},
            {"id": 2, "name": "عرض نهاية الأسبوع", "description": "5GB + 100 دقيقة", "price": 30, "validity": "48 ساعة"},
            {"id": 3, "name": "باقة شهرية", "description": "30GB + 500 دقيقة", "price": 150, "validity": "30 يوم"},
            {"id": 4, "name": "عرض المكالمات", "description": "300 دقيقة جميع الشبكات", "price": 25, "validity": "7 أيام"}
        ]
        
        return {
            "success": True,
            "offers": random.sample(offers, random.randint(2, 4))
        }

# إنشاء نسخة وحيدة من API
vodafone_api = VodafoneEgyptAPI()