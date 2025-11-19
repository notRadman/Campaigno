#!/usr/bin/env python3
"""
Campaign Daily Notification - إشعار يومي عن الحملة
"""

import yaml
import subprocess
from pathlib import Path
from datetime import datetime, timedelta

CAMPAIGNS_DIR = Path.home() / "Campaigns"

# للتحقق إذا كان يعمل من venv
SCRIPT_DIR = Path(__file__).parent if '__file__' in globals() else Path.cwd()

# ================== TRANSLATIONS ==================
TRANSLATIONS = {
    'ar': {
        'campaign_title': 'الحملة',
        'week': 'الأسبوع',
        'days_left': 'أيام متبقية',
        'milestones_completed': 'المراحل المنجزة',
        'recovery_period': '🌴 فترة الاستشفاء',
        'ends': 'تنتهي',
        'days': 'أيام',
        'rest_well': 'استرح جيداً، أنت تستحق ذلك!',
    },
    'en': {
        'campaign_title': 'Campaign',
        'week': 'Week',
        'days_left': 'days left',
        'milestones_completed': 'milestones completed',
        'recovery_period': '🌴 Recovery Period',
        'ends': 'Ends',
        'days': 'days',
        'rest_well': 'Rest well, you deserve it!',
    },
    'he': {
        'campaign_title': 'מסע',
        'week': 'שבוע',
        'days_left': 'ימים נותרו',
        'milestones_completed': 'אבני דרך הושלמו',
        'recovery_period': '🌴 תקופת התאוששות',
        'ends': 'מסתיים',
        'days': 'ימים',
        'rest_well': 'תנוח היטב, מגיע לך!',
    }
}

def load_language():
    """تحميل اللغة المحفوظة"""
    config_file = CAMPAIGNS_DIR / ".language"
    if config_file.exists():
        return config_file.read_text().strip()
    return 'ar'

def t(key, lang):
    """ترجمة نص"""
    return TRANSLATIONS[lang].get(key, key)

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
                        # حساب الـmilestones
                        milestones_total = content.count("- [ ]") + content.count("- [x]") + content.count("- [-]")
                        milestones_done = content.count("- [x]")
                        
                        # قراءة اللغة من الملف أو استخدام اللغة العامة
                        campaign_lang = data.get('language', load_language())

                        return {
                            'data': data,
                            'file': campaign_file,
                            'end_date': end_date,
                            'recovery_end': recovery_end,
                            'milestones_total': milestones_total,
                            'milestones_done': milestones_done,
                            'language': campaign_lang
                        }
        except:
            continue

    return None

def send_notification(title, message):
    """إرسال notification"""
    subprocess.run(['notify-send', '-u', 'normal', '-t', '10000', title, message])

def main():
    campaign = find_active_campaign()

    if not campaign:
        return

    data = campaign['data']
    today = datetime.now().date()
    end_date = campaign['end_date']
    recovery_end = campaign['recovery_end']
    lang = campaign['language']

    if today <= end_date:
        # في الحملة - عرض معلومات الحملة
        days_left = (end_date - today).days
        week = data.get('current_week', 1)

        title = f"📊 {t('campaign_title', lang)}: {data['name']}"
        message = (
            f"{t('week', lang)} {week}/6 • {days_left} {t('days_left', lang)}\n"
            f"✓ {campaign['milestones_done']}/{campaign['milestones_total']} {t('milestones_completed', lang)}"
        )

        send_notification(title, message)
    else:
        # في الاستشفاء - عرض معلومات الاستشفاء
        days_left = (recovery_end - today).days

        title = t('recovery_period', lang)
        message = (
            f"{t('ends', lang)}: {recovery_end.strftime('%B %d, %Y')} ({days_left} {t('days', lang)})\n"
            f"{t('rest_well', lang)}"
        )

        send_notification(title, message)

if __name__ == "__main__":
    main()
