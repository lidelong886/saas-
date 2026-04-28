"""
数据验证工具
"""
import re
import bleach
from datetime import datetime

def validate_phone(phone):
    """验证手机号格式"""
    if not phone:
        return False
    pattern = r'^1[3-9]\d{9}$'
    return bool(re.match(pattern, str(phone)))

def validate_email(email):
    """验证邮箱格式"""
    if not email:
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, str(email)))

def validate_password(password):
    """验证密码强度 - 至少8位，且包含字母和数字"""
    value = str(password or '')
    if len(value) < 8:
        return False
    return bool(re.search(r'[A-Za-z]', value) and re.search(r'\d', value))

def validate_battery_code(code):
    """验证电池编码格式"""
    if not code:
        return False
    pattern = r'^BAT\d+'
    return bool(re.match(pattern, str(code)))

def validate_station_code(code):
    """验证站点编码格式"""
    if not code:
        return False
    pattern = r'^STN?\d+'
    return bool(re.match(pattern, str(code)))

def validate_cabinet_code(code):
    """验证柜子编码格式"""
    if not code:
        return False
    pattern = r'^CAB\d+'
    return bool(re.match(pattern, str(code)))

def validate_order_no(order_no):
    """验证订单号格式"""
    if not order_no:
        return False
    pattern = r'^ORD\d+'
    return bool(re.match(pattern, str(order_no)))

def validate_payment_no(payment_no):
    """验证支付单号格式"""
    if not payment_no:
        return False
    pattern = r'^PAY\d+'
    return bool(re.match(pattern, str(payment_no)))

def validate_latitude(lat):
    """验证纬度范围"""
    try:
        lat = float(lat)
        return -90 <= lat <= 90
    except (ValueError, TypeError):
        return False

def validate_longitude(lng):
    """验证经度范围"""
    try:
        lng = float(lng)
        return -180 <= lng <= 180
    except (ValueError, TypeError):
        return False

def validate_datetime(date_str, format='%Y-%m-%d %H:%M:%S'):
    """验证日期时间格式"""
    try:
        datetime.strptime(date_str, format)
        return True
    except (ValueError, TypeError):
        return False

def validate_positive_number(value):
    """验证正数"""
    try:
        num = float(value)
        return num > 0
    except (ValueError, TypeError):
        return False

def validate_integer(value, min_value=None, max_value=None):
    """验证整数"""
    try:
        num = int(value)
        if min_value is not None and num < min_value:
            return False
        if max_value is not None and num > max_value:
            return False
        return True
    except (ValueError, TypeError):
        return False

def sanitize_html(text):
    """清理 HTML 标签，防止 XSS 攻击"""
    if not text:
        return text
    return bleach.clean(str(text), tags=[], strip=True)

def validate_no_sql_injection(text):
    """检测 SQL 注入关键字"""
    if not text:
        return True
    dangerous_patterns = [
        r'(\bUNION\b.*\bSELECT\b)',
        r'(\bDROP\b.*\bTABLE\b)',
        r'(\bINSERT\b.*\bINTO\b)',
        r'(\bDELETE\b.*\bFROM\b)',
        r'(\bUPDATE\b.*\bSET\b)',
        r'(--)',
        r'(;.*\b(DROP|DELETE|INSERT|UPDATE)\b)',
        r'(\bEXEC\b|\bEXECUTE\b)',
    ]
    text_upper = str(text).upper()
    for pattern in dangerous_patterns:
        if re.search(pattern, text_upper, re.IGNORECASE):
            return False
    return True

def sanitize_input(text, max_length=None):
    """综合输入清理：XSS + SQL 注入防护"""
    if not text:
        return text

    # 转换为字符串
    text = str(text).strip()

    # 长度限制
    if max_length and len(text) > max_length:
        text = text[:max_length]

    # SQL 注入检测
    if not validate_no_sql_injection(text):
        raise ValueError("输入包含非法字符")

    # HTML 清理
    text = sanitize_html(text)

    return text

