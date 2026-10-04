"""ตรวจช่วงเวลาจองโต๊ะ (Standard Library เท่านั้น): การจอง 1 ครั้งใช้โต๊ะ 90 นาที"""
from datetime import datetime, timedelta

SLOT = timedelta(minutes=90)

def parse_time(text):
    try: return datetime.strptime(text.strip(), "%Y-%m-%d %H:%M")
    except (ValueError, AttributeError): return None

def find_conflict(existing, when, phone, total_tables):
    """existing = list ของ (เวลาข้อความ, เบอร์) -> คืนข้อความปัญหา หรือ None ถ้าจองได้"""
    near = []
    for text, ph in existing:
        t = parse_time(text)
        if t and abs(t - when) < SLOT: near.append(ph)
    if phone and phone in near: return "คุณมีการจองในช่วงเวลาใกล้เคียงนี้อยู่แล้ว"
    if len(near) >= total_tables: return f"ช่วงเวลานี้โต๊ะเต็มแล้ว (ร้านมี {total_tables} โต๊ะ) กรุณาเลือกเวลาอื่น"
    return None
