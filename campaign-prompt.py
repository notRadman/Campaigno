#!/usr/bin/env python3
"""
Campaign Prompt - عرض معلومات الحملة في الـprompt
"""

import yaml
from pathlib import Path
from datetime import datetime, timedelta

CAMPAIGNS_DIR = Path.home() / "Campaigns"

# للتحقق إذا كان يعمل من venv
SCRIPT_DIR = Path(__file__).parent if '__file__' in globals() else Path.cwd()

def find_active_campaign():
    """البحث عن الحملة النشطة"""
    if not CAMPAIGNS_DIR.exists():
        return None
    
    today = datetime.now().date()
    
    for folder in CAMPAIGNS_DIR.iterdir():
        if not folder.is_dir() or folder.name.startswith("_"):
            continue
        
        campaign_file = folder / "campaign.md"
        if not campaign_file.exists():
            continue
        
        try:
            content = campaign_file.read_text()
            if content.startswith("---"):
                yaml_end = content.find("---", 3)
                yaml_content = content[3:yaml_end]
                data = yaml.safe_load(yaml_content)
                
                status = data.get('status', 'active')
                
                if status in ['active', 'rest']:
                    start_date = datetime.strptime(data['start'], '%Y-%m-%d').date()
                    end_date = datetime.strptime(data['end'], '%Y-%m-%d').date()
                    
                    recovery_end_str = data.get('recovery_end', '').strip()
                    if recovery_end_str:
                        recovery_end = datetime.strptime(recovery_end_str, '%Y-%m-%d').date()
                    else:
                        recovery_end = end_date + timedelta(days=14)
                    
                    if start_date <= today <= recovery_end:
                        return {
                            'data': data,
                            'end_date': end_date,
                            'recovery_end': recovery_end
                        }
        except:
            continue
    
    return None

def main():
    campaign = find_active_campaign()
    
    if not campaign:
        return
    
    data = campaign['data']
    today = datetime.now().date()
    end_date = campaign['end_date']
    recovery_end = campaign['recovery_end']
    
    # استخراج رقم الحملة من الاسم
    name = data['name']
    campaign_num = name.split()[1] if len(name.split()) > 1 else "X"
    
    if today <= end_date:
        # في الحملة - عرض الأيام المتبقية
        days_left = (end_date - today).days
        week = data.get('current_week', 1)
        print(f" [C{campaign_num}•W{week}•{days_left}d]", end="")
    else:
        # في الاستشفاء - عرض التاريخ نفسه
        end_date_str = recovery_end.strftime("%b %d")
        print(f" [R→{end_date_str}]", end="")

if __name__ == "__main__":
    main()
