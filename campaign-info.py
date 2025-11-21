#!/usr/bin/env python3
"""
Campaign Info - Minimal Version
عرض معلومات الحملة الحالية
"""

import yaml
from pathlib import Path
from datetime import datetime, timedelta

CAMPAIGNS_FILE = Path.home() / "campaigns.md"

def parse_campaigns_file():
    """قراءة ملف الحملات"""
    if not CAMPAIGNS_FILE.exists():
        return []
    
    content = CAMPAIGNS_FILE.read_text()
    campaigns = []
    
    # تقسيم حسب ---
    blocks = content.split('---\n')
    
    for block in blocks:
        block = block.strip()
        if not block or block == '':
            continue
        
        try:
            # محاولة قراءة YAML
            data = yaml.safe_load(block)
            if data and isinstance(data, dict) and 'number' in data:
                campaigns.append(data)
        except:
            continue
    
    return campaigns

def find_active_campaign():
    """البحث عن الحملة النشطة"""
    campaigns = parse_campaigns_file()
    if not campaigns:
        return None
    
    today = datetime.now().date()
    
    for campaign in campaigns:
        try:
            start = datetime.strptime(campaign['start'], '%Y-%m-%d').date()
            end = datetime.strptime(campaign['end'], '%Y-%m-%d').date()
            
            # حساب نهاية الاستشفاء
            recovery_end_str = str(campaign.get('recovery_end', '')).strip()
            if recovery_end_str and recovery_end_str != 'None':
                recovery_end = datetime.strptime(recovery_end_str, '%Y-%m-%d').date()
            else:
                recovery_end = end + timedelta(days=14)
            
            # التحقق إذا كان اليوم ضمن نطاق الحملة
            if start <= today <= recovery_end:
                return {
                    'number': campaign.get('number', 'X'),
                    'name': campaign.get('name', ''),
                    'start': start,
                    'end': end,
                    'recovery_end': recovery_end,
                    'status': campaign.get('status', ''),
                    'rate': campaign.get('rate', '')
                }
        except:
            continue
    
    return None

def calculate_week(start, today):
    """حساب الأسبوع الحالي"""
    days_passed = (today - start).days
    week = (days_passed // 7) + 1
    return min(week, 6)

def main():
    campaign = find_active_campaign()
    
    if not campaign:
        print("❌ No active campaign found")
        print(f"📝 Create one: campaign-edit")
        return
    
    today = datetime.now().date()
    start = campaign['start']
    end = campaign['end']
    recovery_end = campaign['recovery_end']
    number = campaign['number']
    name = campaign['name']
    
    print()
    print(f"Campaign {number:02d}: {name}")
    print("━" * 50)
    
    if today <= end:
        # في الحملة
        week = calculate_week(start, today)
        days_left = (end - today).days
        days_total = (end - start).days
        progress = ((days_total - days_left) / days_total) * 100
        
        print(f"Week:       {week}/6")
        print(f"Started:    {start.strftime('%b %d, %Y')}")
        print(f"Ends:       {end.strftime('%b %d, %Y')}")
        print(f"Days left:  {days_left}")
        print(f"Progress:   {progress:.0f}%")
        print()
        print("Status: Active 🔥")
    else:
        # في الاستشفاء
        days_left = (recovery_end - today).days
        
        print(f"Campaign ended:  {end.strftime('%b %d, %Y')}")
        print(f"Recovery until:  {recovery_end.strftime('%b %d, %Y')}")
        print(f"Days left:       {days_left}")
        print()
        print("Status: Recovery 🌴")
    
    print()

if __name__ == "__main__":
    main()
