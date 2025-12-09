#!/usr/bin/env python3
"""
Campaign Manager - نظام إدارة الحملات
ملف واحد - كل الوظائف
"""

import sys
import os
import subprocess
import random
from pathlib import Path
from datetime import datetime, timedelta

# ═══════════════════════════════════════
# إعدادات اللغة - Language Settings
# ═══════════════════════════════════════

KEYS = {
    'number': 'number',
    'name': 'name',
    'description': 'description',
    'start': 'start',
    'end': 'end',
    'recovery_end': 'recovery-end',
    'milestones': 'milestones',
    'status': 'status',
    'rate': 'rate',
    'links': 'links&drafts'
}

# ═══════════════════════════════════════
# إعدادات الملفات - File Settings
# ═══════════════════════════════════════

SCRIPT_DIR = Path(__file__).parent

CAMPAIGNS_FILE = Path.home() / "Documents/campaigno/campaigns.md"
WIKI_FILE = SCRIPT_DIR / "wiki.pdf"
WIKI_VIEWER = "zathura"
MOTIVATE_FILE = SCRIPT_DIR / "quotes.md"
YOURSELF_FILE = SCRIPT_DIR / "yourself.md"
YOURSELF_VIEWER = "less"  # or: less, cat, nvim
EDITOR = os.environ.get('EDITOR', 'nvim')

# ═══════════════════════════════════════
# Custom Parser - لقراءة الملف
# ═══════════════════════════════════════

def parse_campaigns_file():
    """قراءة ملف الحملات بدون YAML"""
    if not CAMPAIGNS_FILE.exists():
        return []
    
    content = CAMPAIGNS_FILE.read_text()
    campaigns = []
    
    # تقسيم حسب ---
    blocks = content.split('---\n')
    
    for block in blocks:
        block = block.strip()
        if not block or '###TEMPLATE###' in block:
            continue
        
        campaign = {}
        current_key = None
        current_list = []
        
        for line in block.split('\n'):
            line_stripped = line.strip()
            
            # تخطي الأسطر الفارغة
            if not line_stripped:
                continue
            
            # التحقق من السطر يحتوي على :
            if ':' in line and not line_stripped.startswith('-'):
                # حفظ القائمة السابقة إذا كانت موجودة
                if current_key and current_list:
                    campaign[current_key] = current_list
                    current_list = []
                
                # قراءة المفتاح والقيمة
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                
                current_key = key
                
                # إذا كانت القيمة فارغة، نتوقع قائمة
                if not value:
                    current_list = []
                else:
                    campaign[key] = value
                    current_key = None
            
            # عنصر في قائمة (حفظ السطر مع المسافات للـ subtasks)
            elif line_stripped.startswith('-') and current_key:
                current_list.append(line.rstrip())
        
        # حفظ القائمة الأخيرة
        if current_key and current_list:
            campaign[current_key] = current_list
        
        # إضافة الحملة إذا كانت تحتوي على رقم
        if KEYS['number'] in campaign:
            campaigns.append(campaign)
    
    return campaigns

# ═══════════════════════════════════════
# وظائف مساعدة - Helper Functions
# ═══════════════════════════════════════

def find_active_campaign():
    """البحث عن الحملة النشطة"""
    campaigns = parse_campaigns_file()
    if not campaigns:
        return None
    
    today = datetime.now().date()
    
    for campaign in campaigns:
        try:
            start_str = campaign.get(KEYS['start'], '')
            end_str = campaign.get(KEYS['end'], '')
            
            if not start_str or not end_str:
                continue
            
            start = datetime.strptime(start_str, '%Y-%m-%d').date()
            end = datetime.strptime(end_str, '%Y-%m-%d').date()
            
            # حساب نهاية الاستشفاء
            recovery_end_str = campaign.get(KEYS['recovery_end'], '').strip()
            if recovery_end_str:
                recovery_end = datetime.strptime(recovery_end_str, '%Y-%m-%d').date()
            else:
                recovery_end = end + timedelta(days=14)
            
            # التحقق إذا كان اليوم ضمن نطاق الحملة
            if start <= today <= end:
                return {
                    'data': campaign,
                    'start': start,
                    'end': end,
                    'recovery_end': recovery_end
                }
        except:
            continue
    
    return None

def calculate_week(start, today):
    """حساب الأسبوع الحالي"""
    days_passed = (today - start).days
    week = (days_passed // 7) + 1
    return min(week, 6)

def get_current_milestone(campaign_data):
    """الحصول على المهمة الحالية مع subtasks"""
    milestones = campaign_data.get(KEYS['milestones'], [])
    
    for i, milestone in enumerate(milestones):
        milestone_stripped = milestone.strip()
        
        if not milestone_stripped or not milestone_stripped.startswith('- ['):
            continue
        
        # عد المسافات البادئة
        leading_spaces = len(milestone) - len(milestone.lstrip())
        
        # main task = مسافات قليلة (3 أو أقل)
        if leading_spaces <= 3:
            if '[ ]' in milestone_stripped:
                # لقينا main task معلقة
                text = milestone_stripped.split('[ ]', 1)[1].strip()
                
                # دور على subtask معلقة تحتها
                for j in range(i + 1, len(milestones)):
                    sub_milestone = milestones[j]
                    sub_stripped = sub_milestone.strip()
                    sub_spaces = len(sub_milestone) - len(sub_milestone.lstrip())
                    
                    # لو لقينا main task تانية، وقف
                    if sub_spaces <= 3 and sub_stripped.startswith('- ['):
                        break
                    
                    # لو لقينا subtask معلقة، ارجعها
                    if sub_spaces > 3 and sub_stripped.startswith('- [') and '[ ]' in sub_stripped:
                        sub_text = sub_stripped.split('[ ]', 1)[1].strip()
                        return i + 1, text, sub_text, len(milestones)
                
                # مفيش subtasks معلقة، ارجع الـ main task بس
                return i + 1, text, None, len(milestones)
    
    # مفيش حاجة معلقة خالص
    return None, None, None, len(milestones)

def count_completed_milestones(campaign_data):
    """عد المهام المنجزة (main tasks فقط)"""
    milestones = campaign_data.get(KEYS['milestones'], [])
    completed = 0
    total = 0
    
    for milestone in milestones:
        milestone_stripped = milestone.strip()
        
        # تخطي الأسطر الفارغة
        if not milestone_stripped:
            continue
        
        # عد المسافات البادئة
        leading_spaces = len(milestone) - len(milestone.lstrip())
        
        # main task = مسافات قليلة (3 أو أقل)
        # subtask = مسافات كتيرة (أكتر من 3)
        if leading_spaces <= 3 and milestone_stripped.startswith('- ['):
            total += 1
            if '[x]' in milestone_stripped or '[X]' in milestone_stripped:
                completed += 1
    
    return completed, total

# ═══════════════════════════════════════
# الأوامر - Commands
# ═══════════════════════════════════════

def cmd_help():
    """عرض المساعدة"""
    print("""
الأوامر المتاحة:

  help          عرض هذه المساعدة
  info          عرض معلومات الحملة الحالية
  current       عرض المهمة الحالية والتقدم
  edit          تعديل ملف الحملات
  wiki          فتح ملف الويكي
  motivate      مقولة تحفيزية عشوائية
  yourself      فتح ملف "عن نفسك"

الاستخدام:
  python3 campaign.py <command>

مثال:
  python3 campaign.py info
  python3 campaign.py current
""")

def cmd_info():
    """عرض معلومات الحملة الحالية"""
    campaign = find_active_campaign()
    
    if not campaign:
        print("❌ لا توجد حملة نشطة")
        print("✏️  أنشئ واحدة: python3 campaign.py edit")
        return
    
    data = campaign['data']
    name = data.get(KEYS['name'], 'غير محدد')
    description = data.get(KEYS['description'], '')
    start = campaign['start']
    
    print()
    print(f"Name: {name}")
    print(f"Start date: {start.strftime('%d %B %Y')}")
    if description:
        print(f"Description: {description}")
    print()

def cmd_current():
    """عرض المهمة الحالية والتقدم"""
    campaign = find_active_campaign()
    
    if not campaign:
        print("❌ لا توجد حملة نشطة")
        return
    
    data = campaign['data']
    completed, total = count_completed_milestones(data)
    milestone_num, parent_text, subtask_text, _ = get_current_milestone(data)
    
    if parent_text:
        if subtask_text:
            # عندنا parent و subtask
            print(f"[{completed}/{total}] {parent_text} → {subtask_text}")
        else:
            # عندنا parent بس بدون subtasks معلقة
            print(f"[{completed}/{total}] {parent_text}")
    else:
        print(f"[{completed}/{total}] جميع المهام منجزة! 🎉")

def cmd_edit():
    """فتح ملف الحملات للتعديل"""
    # إنشاء الملف إذا لم يكن موجوداً
    if not CAMPAIGNS_FILE.exists():
        CAMPAIGNS_FILE.parent.mkdir(parents=True, exist_ok=True)
        template = f"""---
{KEYS['number']}: 0
{KEYS['name']}: حملتي الأولى
{KEYS['description']}: 
{KEYS['start']}: {datetime.now().strftime('%Y-%m-%d')}
{KEYS['end']}: {(datetime.now() + timedelta(days=42)).strftime('%Y-%m-%d')}
{KEYS['recovery_end']}: 
{KEYS['milestones']}:
   - [ ] مهمة 1
   - [ ] مهمة 2
      - [ ] subtask 2.1
      - [ ] subtask 2.2
   - [ ] مهمة 3
{KEYS['status']}: 
{KEYS['rate']}: 
{KEYS['links']}:
   - 
---

---
###TEMPLATE###
{KEYS['number']}: 
{KEYS['name']}: 
{KEYS['description']}: 
{KEYS['start']}:
{KEYS['end']}:
{KEYS['recovery_end']}:
{KEYS['milestones']}:
   - [x] مثال منجز
      - [x] subtask منجز
      - [ ] subtask معلق
   - [-] مثال ملغي
   - [ ] مثال معلق
{KEYS['status']}: 
{KEYS['rate']}: 
{KEYS['links']}:
   -
---
"""
        CAMPAIGNS_FILE.write_text(template)
        print(f"✅ تم إنشاء ملف جديد: {CAMPAIGNS_FILE}")
    
    # فتح الملف في المحرر
    subprocess.run([EDITOR, str(CAMPAIGNS_FILE)])

def cmd_wiki():
    """فتح ملف الويكي"""
    if not WIKI_FILE.exists():
        print(f"❌ الملف غير موجود: {WIKI_FILE}")
        print(f"💡 عدّل المسار في الكود: WIKI_FILE")
        return
    
    try:
        subprocess.Popen([WIKI_VIEWER, str(WIKI_FILE)], 
                        stdout=subprocess.DEVNULL, 
                        stderr=subprocess.DEVNULL)
        print(f"✅ فتح الويكي في {WIKI_VIEWER}")
    except FileNotFoundError:
        print(f"❌ البرنامج غير موجود: {WIKI_VIEWER}")
        print(f"💡 عدّل في الكود: WIKI_VIEWER")

def cmd_motivate():
    """مقولة تحفيزية عشوائية"""
    if not MOTIVATE_FILE.exists():
        print(f"❌ الملف غير موجود: {MOTIVATE_FILE}")
        print(f"💡 أنشئ ملف {MOTIVATE_FILE} وضع كل مقولة في سطر")
        return
    
    lines = MOTIVATE_FILE.read_text().strip().split('\n')
    lines = [l.strip() for l in lines if l.strip()]
    
    if not lines:
        print("❌ الملف فارغ!")
        return
    
    quote = random.choice(lines)
    print()
    print(f"  💡 {quote}")
    print()

def cmd_yourself():
    """فتح ملف "عن نفسك" """
    if not YOURSELF_FILE.exists():
        print(f"❌ الملف غير موجود: {YOURSELF_FILE}")
        print(f"💡 أنشئ ملف {YOURSELF_FILE}")
        return
    
    try:
        subprocess.run([YOURSELF_VIEWER, str(YOURSELF_FILE)])
    except FileNotFoundError:
        print(f"❌ البرنامج غير موجود: {YOURSELF_VIEWER}")
        print(f"💡 عدّل في الكود: YOURSELF_VIEWER")

# ═══════════════════════════════════════
# Main
# ═══════════════════════════════════════

def main():
    if len(sys.argv) < 2:
        cmd_help()
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    commands = {
        'help': cmd_help,
        'info': cmd_info,
        'current': cmd_current,
        'edit': cmd_edit,
        'wiki': cmd_wiki,
        'motivate': cmd_motivate,
        'yourself': cmd_yourself,
    }
    
    if command in commands:
        commands[command]()
    else:
        print(f"❌ أمر غير معروف: {command}")
        print()
        cmd_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
