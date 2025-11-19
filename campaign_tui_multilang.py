#!/usr/bin/env python3
"""
Campaign Manager TUI - نظام إدارة الحملات
"""

import os
import sys
import yaml
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt, Confirm
from rich.table import Table

console = Console()

# المسارات - يمكن تغييرها
CAMPAIGNS_DIR = Path.home() / "Campaigns"
TEMPLATES_DIR = CAMPAIGNS_DIR / "_templates"
HISTORY_FILE = CAMPAIGNS_DIR / "_history.md"

# للتحقق إذا كان يعمل من venv
SCRIPT_DIR = Path(__file__).parent if '__file__' in globals() else Path.cwd()

# ================== TRANSLATIONS ==================
TRANSLATIONS = {
    'ar': {
        # UI Elements
        'campaign': 'الحملة',
        'week': 'الأسبوع',
        'started': 'بدأت',
        'current_milestone': 'المرحلة الحالية',
        'all_completed': '🎉 جميع المراحل أنجزت!',
        'actions': 'الإجراءات',
        'mark_done': '[✓] أنجز',
        'mark_wont': '[✗] لن أنجز',
        'add_note': '[N] إضافة ملاحظة',
        'open_folder': '[F] فتح المجلد في الطرفية',
        'history': '[H] السجل',
        'wiki': '[W] الويكي',
        'language': '[L] اللغة',
        'days': 'أيام',
        'left': 'متبقية',
        'choice': 'الاختيار',
        'recovery_period': '🌴 فترة الاستشفاء 🌴',
        'in_recovery': 'أنت في فترة الاستشفاء!',
        'recovery_ends': 'تنتهي فترة الاستشفاء في',
        'rest_now': '[R] استرح الآن يا بطل! (إغلاق)',
        'configure_next': '[C] تجهيز الحملة القادمة',
        
        # Templates
        'campaign_template': """---
name: Campaign 01
start: {start}
end: {end}
status: active
recovery_end: 
current_week: 1
language: ar
---

# الحملة 01: [اسم الحملة]

## الوصف
[وصف الهدف من الحملة]

## المراحل
- [ ] المرحلة 1: 
- [ ] المرحلة 2: 
- [ ] المرحلة 3: 
- [ ] المرحلة 4: 
- [ ] المرحلة 5: 

## المساءلة
**الشخص:** [اسم الشخص]
**المتابعة:** كل [أحد/أسبوع]
""",
        'note_template': """# {campaign_name} - {milestone_name}
التاريخ: {date}
الوقت: {time}

## الملاحظات

""",
        'wiki_content': """# ويكي نظام الحملات

## النظام

قسم سنتك إلى ثماني حملات. كل حملة مكونة من ستة أسابيع عمل متواصل، تليها أسبوعان استشفاء كامل.

### لماذا 6 أسابيع؟
- طويلة كفاية لإنجاز حقيقي ملموس
- قصيرة كفاية للحفاظ على الإلحاح

### لماذا أسبوعان راحة؟
- أسبوع واحد لا يكفي للتعافي العصبي الكامل
- ثلاثة أسابيع تفقدك الزخم
- أسبوعان هما نقطة التوازن المثلى

## القواعد

1. **هدف واحد واضح قابل للقياس**
2. **موعد نهائي حقيقي مع عواقب**
3. **حد أقصى 4-6 ساعات عمل مركز يومياً**
4. **نقطة مساءلة واضحة**
""",
        'history_template': """# سجل الحملات

## قالب لكل حملة

### الحملة X: [الاسم] (التاريخ - التاريخ)
**الحالة:** مكتملة/متروكة
**المراحل المنجزة:** X/Y
**التقييم:** ⭐⭐⭐⭐⭐

#### ما سار بشكل جيد
- 

#### ما لم يسر بشكل جيد
- 

#### الدروس المستفادة
- 

---

""",
        # Notifications
        'milestone_completed': '🎉 المرحلة أنجزت!',
        'milestone_completed_msg': 'الحمد لله! استمر بقوة 💪',
        'milestone_skipped': '📝 المرحلة تم تخطيها',
        'milestone_skipped_msg': 'لا بأس، المهم التقدم. لا تيأس من رحمة الله',
        
        # Prompts
        'campaign_name': 'اسم الحملة',
        'create_vault': 'إنشاء المخزن؟',
        'open_editing': 'فتح للتعديل؟',
        'no_vault': 'لم يتم العثور على مخزن!',
        'vault_exists': '⚠️  المخزن موجود بالفعل!',
        'recreate_templates': 'إعادة إنشاء القوالب؟',
        'vault_created': '✅ تم إنشاء المخزن بنجاح!',
        'campaign_created': '✅ تم إنشاء الحملة',
        'no_active': 'لم يتم العثور على حملات نشطة!',
        'create_new': 'إنشاء حملة جديدة؟',
        'conflict': '⚠️  تعارض: عدة حملات نشطة!',
        'fix_manually': 'يرجى الإصلاح يدوياً في',
        
        # Language selection
        'select_language': 'اختر اللغة / Choose Language / בחר שפה',
        'convert_files': 'هل تريد تحويل الملفات الحالية إلى اللغة الجديدة؟',
        'converting': 'جاري التحويل...',
        'converted': '✅ تم تحويل الملفات',
    },
    'en': {
        # UI Elements
        'campaign': 'Campaign',
        'week': 'Week',
        'started': 'Started',
        'current_milestone': 'Current Milestone',
        'all_completed': '🎉 All milestones completed!',
        'actions': 'Actions',
        'mark_done': '[✓] Mark as Done',
        'mark_wont': '[✗] Mark as Won\'t Do',
        'add_note': '[N] Add Note',
        'open_folder': '[F] Open folder in terminal',
        'history': '[H] History',
        'wiki': '[W] Wiki',
        'language': '[L] Language',
        'days': 'days',
        'left': 'left',
        'choice': 'Choice',
        'recovery_period': '🌴 Recovery Period 🌴',
        'in_recovery': 'You are in Recovery!',
        'recovery_ends': 'Recovery ends on',
        'rest_now': '[R] Rest now, bro! (close)',
        'configure_next': '[C] Configure coming campaign',
        
        # Templates
        'campaign_template': """---
name: Campaign 01
start: {start}
end: {end}
status: active
recovery_end: 
current_week: 1
language: en
---

# Campaign 01: [Campaign Name]

## Description
[Description of campaign goal]

## Milestones
- [ ] Milestone 1: 
- [ ] Milestone 2: 
- [ ] Milestone 3: 
- [ ] Milestone 4: 
- [ ] Milestone 5: 

## Accountability
**Person:** [Person Name]
**Check-in:** Every [Sunday/week]
""",
        'note_template': """# {campaign_name} - {milestone_name}
Date: {date}
Time: {time}

## Notes

""",
        'wiki_content': """# Campaign System Wiki

## The System

Divide your year into eight campaigns. Each campaign consists of six weeks of continuous work, followed by two weeks of complete recovery.

### Why 6 weeks?
- Long enough for real tangible achievement
- Short enough to maintain urgency

### Why two weeks rest?
- One week isn't enough for complete neural recovery
- Three weeks lose momentum
- Two weeks is the optimal balance point

## The Rules

1. **One clear measurable goal**
2. **Real deadline with consequences**
3. **Maximum 4-6 hours of focused work daily**
4. **Clear accountability point**
""",
        'history_template': """# Campaign History

## Template for Each Campaign

### Campaign X: [Name] (Date - Date)
**Status:** Completed/Abandoned
**Milestones Completed:** X/Y
**Rating:** ⭐⭐⭐⭐⭐

#### What Went Well
- 

#### What Didn't Go Well
- 

#### Lessons Learned
- 

---

""",
        # Notifications
        'milestone_completed': '🎉 Milestone Completed!',
        'milestone_completed_msg': 'Great job! Keep going strong 💪',
        'milestone_skipped': '📝 Milestone Skipped',
        'milestone_skipped_msg': 'That\'s okay, progress matters. Keep moving forward',
        
        # Prompts
        'campaign_name': 'Campaign name',
        'create_vault': 'Create vault?',
        'open_editing': 'Open for editing?',
        'no_vault': 'No vault found!',
        'vault_exists': '⚠️  Vault already exists!',
        'recreate_templates': 'Recreate templates?',
        'vault_created': '✅ Vault created successfully!',
        'campaign_created': '✅ Campaign created',
        'no_active': 'No active campaigns found!',
        'create_new': 'Create new campaign?',
        'conflict': '⚠️  CONFLICT: Multiple active campaigns!',
        'fix_manually': 'Please fix manually in',
        
        # Language selection
        'select_language': 'Choose Language / اختر اللغة / בחר שפה',
        'convert_files': 'Convert existing files to the new language?',
        'converting': 'Converting...',
        'converted': '✅ Files converted',
    },
    'he': {
        # UI Elements
        'campaign': 'מסע',
        'week': 'שבוע',
        'started': 'התחיל',
        'current_milestone': 'אבן דרך נוכחית',
        'all_completed': '🎉 כל אבני הדרך הושלמו!',
        'actions': 'פעולות',
        'mark_done': '[✓] סמן כהושלם',
        'mark_wont': '[✗] סמן כלא יושלם',
        'add_note': '[N] הוסף הערה',
        'open_folder': '[F] פתח תיקייה בטרמינל',
        'history': '[H] היסטוריה',
        'wiki': '[W] ויקי',
        'language': '[L] שפה',
        'days': 'ימים',
        'left': 'נשארו',
        'choice': 'בחירה',
        'recovery_period': '🌴 תקופת התאוששות 🌴',
        'in_recovery': 'אתה בתקופת התאוששות!',
        'recovery_ends': 'ההתאוששות מסתיימת ב',
        'rest_now': '[R] תנוח עכשיו, אחי! (סגור)',
        'configure_next': '[C] הגדר את המסע הבא',
        
        # Templates
        'campaign_template': """---
name: Campaign 01
start: {start}
end: {end}
status: active
recovery_end: 
current_week: 1
language: he
---

# מסע 01: [שם המסע]

## תיאור
[תיאור המטרה של המסע]

## אבני דרך
- [ ] אבן דרך 1: 
- [ ] אבן דרך 2: 
- [ ] אבן דרך 3: 
- [ ] אבן דרך 4: 
- [ ] אבן דרך 5: 

## אחריותיות
**אדם:** [שם האדם]
**בדיקה:** כל [ראשון/שבוע]
""",
        'note_template': """# {campaign_name} - {milestone_name}
תאריך: {date}
שעה: {time}

## הערות

""",
        'wiki_content': """# ויקי מערכת המסעות

## המערכת

חלק את השנה שלך לשמונה מסעות. כל מסע מורכב משישה שבועות של עבודה רצופה, ואחריהם שבועיים של התאוששות מלאה.

### למה 6 שבועות?
- מספיק ארוך להישג אמיתי מוחשי
- מספיק קצר לשמור על דחיפות

### למה שבועיים מנוחה?
- שבוע אחד לא מספיק להתאוששות עצבית מלאה
- שלושה שבועות מאבדים מומנטום
- שבועיים הם נקודת האיזון האופטימלית

## החוקים

1. **מטרה אחת ברורה ומדידה**
2. **דדליין אמיתי עם השלכות**
3. **מקסימום 4-6 שעות עבודה ממוקדת ביום**
4. **נקודת אחריותיות ברורה**
""",
        'history_template': """# היסטוריית מסעות

## תבנית לכל מסע

### מסע X: [שם] (תאריך - תאריך)
**סטטוס:** הושלם/ננטש
**אבני דרך שהושלמו:** X/Y
**דירוג:** ⭐⭐⭐⭐⭐

#### מה עבד טוב
- 

#### מה לא עבד טוב
- 

#### לקחים שנלמדו
- 

---

""",
        # Notifications
        'milestone_completed': '🎉 אבן דרך הושלמה!',
        'milestone_completed_msg': 'עבודה מצוינת! המשך חזק 💪',
        'milestone_skipped': '📝 אבן דרך דולגה',
        'milestone_skipped_msg': 'זה בסדר, ההתקדמות חשובה. המשך קדימה',
        
        # Prompts
        'campaign_name': 'שם המסע',
        'create_vault': 'צור כספת?',
        'open_editing': 'פתח לעריכה?',
        'no_vault': 'לא נמצאה כספת!',
        'vault_exists': '⚠️  הכספת כבר קיימת!',
        'recreate_templates': 'צור מחדש תבניות?',
        'vault_created': '✅ הכספת נוצרה בהצלחה!',
        'campaign_created': '✅ המסע נוצר',
        'no_active': 'לא נמצאו מסעות פעילים!',
        'create_new': 'צור מסע חדש?',
        'conflict': '⚠️  התנגשות: מספר מסעות פעילים!',
        'fix_manually': 'נא לתקן ידנית ב',
        
        # Language selection
        'select_language': 'בחר שפה / Choose Language / اختر اللغة',
        'convert_files': 'להמיר קבצים קיימים לשפה החדשה?',
        'converting': 'ממיר...',
        'converted': '✅ הקבצים הומרו',
    }
}

class CampaignManager:
    def __init__(self):
        self.current_campaign = None
        self.campaign_path = None
        self.current_language = self.load_language()

    def load_language(self):
        """تحميل اللغة المحفوظة أو الافتراضية"""
        config_file = CAMPAIGNS_DIR / ".language"
        if config_file.exists():
            return config_file.read_text().strip()
        return 'ar'  # اللغة الافتراضية

    def save_language(self, lang):
        """حفظ اللغة المختارة"""
        config_file = CAMPAIGNS_DIR / ".language"
        CAMPAIGNS_DIR.mkdir(exist_ok=True)
        config_file.write_text(lang)
        self.current_language = lang

    def t(self, key):
        """ترجمة نص"""
        return TRANSLATIONS[self.current_language].get(key, key)

    def get_wiki_file(self):
        """الحصول على ملف الويكي حسب اللغة"""
        return CAMPAIGNS_DIR / f"_wiki_{self.current_language}.md"

    def change_language(self):
        """تغيير اللغة"""
        console.print(f"\n[bold cyan]{self.t('select_language')}[/bold cyan]")
        console.print("1. العربية (Arabic)")
        console.print("2. English")
        console.print("3. עברית (Hebrew)")
        
        choice = Prompt.ask("Choice", choices=["1", "2", "3"])
        
        lang_map = {"1": "ar", "2": "en", "3": "he"}
        new_lang = lang_map[choice]
        
        if new_lang == self.current_language:
            console.print("[yellow]Same language selected![/yellow]")
            return
        
        # سؤال عن التحويل
        if Confirm.ask(self.t('convert_files')):
            console.print(f"[yellow]{self.t('converting')}[/yellow]")
            self.convert_files_to_language(new_lang)
            console.print(f"[green]{self.t('converted')}[/green]")
        
        self.save_language(new_lang)
        console.print(f"[green]✅ Language changed to {new_lang.upper()}[/green]")

    def convert_files_to_language(self, new_lang):
        """تحويل الملفات للغة الجديدة"""
        # 1. تحويل ملف الحملة الحالية
        campaigns = self.find_active_campaign()
        if campaigns:
            campaign = campaigns[0]
            self.convert_campaign_file(campaign['file'], new_lang)
        
        # 2. تحويل ملف الهيستوري
        if HISTORY_FILE.exists():
            self.convert_history_file(new_lang)

    def convert_campaign_file(self, campaign_file, new_lang):
        """تحويل ملف الحملة مع الحفاظ على المحتوى"""
        content = campaign_file.read_text()
        
        # استخراج YAML
        if content.startswith("---"):
            yaml_end = content.find("---", 3)
            yaml_content = content[3:yaml_end]
            data = yaml.safe_load(yaml_content)
            body = content[yaml_end + 3:].strip()
            
            # تحديث اللغة في YAML
            data['language'] = new_lang
            
            # استخراج القيم المخصصة من المستخدم
            lines = body.split('\n')
            user_title = ""
            user_description = ""
            user_milestones = []
            user_person = ""
            user_checkin = ""
            
            for i, line in enumerate(lines):
                if line.startswith("# "):
                    # استخراج اسم الحملة المخصص
                    parts = line.split(":", 1)
                    if len(parts) > 1:
                        user_title = parts[1].strip()
                
                if "## " in line:
                    section = line.strip()
                    if "Description" in section or "الوصف" in section or "תיאור" in section:
                        if i + 1 < len(lines):
                            user_description = lines[i + 1].strip()
                    
                    if "Accountability" in section or "المساءلة" in section or "אחריותיות" in section:
                        for j in range(i + 1, min(i + 3, len(lines))):
                            if "Person" in lines[j] or "الشخص" in lines[j] or "אדם" in lines[j]:
                                user_person = lines[j].split(":", 1)[1].strip() if ":" in lines[j] else ""
                            if "Check-in" in lines[j] or "المتابعة" in lines[j] or "בדיקה" in lines[j]:
                                user_checkin = lines[j].split(":", 1)[1].strip() if ":" in lines[j] else ""
                
                # استخراج المراحل
                if line.strip().startswith("- ["):
                    milestone_text = line.strip()[6:].strip()
                    if milestone_text and not milestone_text.startswith("Milestone") and not milestone_text.startswith("المرحلة") and not milestone_text.startswith("אבן דרך"):
                        status = "x" if "- [x]" in line else "-" if "- [-]" in line else " "
                        user_milestones.append((status, milestone_text))
            
            # إنشاء المحتوى الجديد من القالب
            new_template = TRANSLATIONS[new_lang]['campaign_template']
            new_content = new_template.format(
                start=data['start'],
                end=data['end']
            )
            
            # استبدال القيم المخصصة
            if user_title:
                new_content = new_content.replace("[اسم الحملة]", user_title)
                new_content = new_content.replace("[Campaign Name]", user_title)
                new_content = new_content.replace("[שם המסע]", user_title)
            
            if user_description and user_description not in ["[وصف الهدف من الحملة]", "[Description of campaign goal]", "[תיאור המטרה של המסע]"]:
                new_content = new_content.replace("[وصف الهدف من الحملة]", user_description)
                new_content = new_content.replace("[Description of campaign goal]", user_description)
                new_content = new_content.replace("[תיאור המטרה של המסע]", user_description)
            
            if user_person and user_person not in ["[اسم الشخص]", "[Person Name]", "[שם האדם]"]:
                new_content = new_content.replace("[اسم الشخص]", user_person)
                new_content = new_content.replace("[Person Name]", user_person)
                new_content = new_content.replace("[שם האדם]", user_person)
            
            if user_checkin and user_checkin not in ["[أحد/أسبوع]", "[Sunday/week]", "[ראשון/שבוע]"]:
                new_content = new_content.replace("[أحد/أسبوع]", user_checkin)
                new_content = new_content.replace("[Sunday/week]", user_checkin)
                new_content = new_content.replace("[ראשון/שבוע]", user_checkin)
            
            # استبدال المراحل
            if user_milestones:
                milestone_lines = new_content.split('\n')
                milestone_section_idx = -1
                for i, line in enumerate(milestone_lines):
                    if "## " in line and ("Milestones" in line or "المراحل" in line or "אבני דרך" in line):
                        milestone_section_idx = i
                        break
                
                if milestone_section_idx != -1:
                    # حذف المراحل القديمة
                    new_milestone_lines = milestone_lines[:milestone_section_idx + 1]
                    # إضافة المراحل الجديدة
                    for status, text in user_milestones:
                        new_milestone_lines.append(f"- [{status}] {text}")
                    
                    # إضافة بقية المحتوى
                    found_next_section = False
                    for i in range(milestone_section_idx + 1, len(milestone_lines)):
                        if milestone_lines[i].startswith("## "):
                            found_next_section = True
                        if found_next_section:
                            new_milestone_lines.append(milestone_lines[i])
                    
                    new_content = '\n'.join(new_milestone_lines)
            
            # تحديث YAML وحفظ
            yaml_str = yaml.dump(data, allow_unicode=True, sort_keys=False)
            final_content = f"---\n{yaml_str}---\n\n{new_content}"
            campaign_file.write_text(final_content)

    def convert_history_file(self, new_lang):
        """تحويل ملف الهيستوري مع الحفاظ على المحتوى"""
        if not HISTORY_FILE.exists():
            return
        
        content = HISTORY_FILE.read_text()
        
        # استخراج المحتوى المخصص (كل شيء بعد القالب)
        user_content = ""
        lines = content.split('\n')
        
        # البحث عن نهاية القالب (السطر الذي فيه ---)
        template_end = -1
        for i, line in enumerate(lines):
            if line.strip() == "---" and i > 10:  # بعد القالب
                template_end = i
                break
        
        if template_end != -1:
            user_content = '\n'.join(lines[template_end + 1:])
        
        # إنشاء المحتوى الجديد
        new_content = TRANSLATIONS[new_lang]['history_template']
        
        if user_content.strip():
            new_content += user_content
        
        HISTORY_FILE.write_text(new_content)

    def init_vault(self):
        """إنشاء الـvault والـtemplates"""
        if CAMPAIGNS_DIR.exists():
            console.print(f"[yellow]{self.t('vault_exists')}[/yellow]")
            if not Confirm.ask(self.t('recreate_templates')):
                return

        # إنشاء المجلدات
        CAMPAIGNS_DIR.mkdir(exist_ok=True)
        TEMPLATES_DIR.mkdir(exist_ok=True)

        # حفظ القوالب لكل اللغات
        for lang in ['ar', 'en', 'he']:
            (TEMPLATES_DIR / f"campaign-template-{lang}.md").write_text(
                TRANSLATIONS[lang]['campaign_template']
            )
            (TEMPLATES_DIR / f"note-template-{lang}.md").write_text(
                TRANSLATIONS[lang]['note_template']
            )
            # ملف ويكي منفصل لكل لغة
            wiki_file = CAMPAIGNS_DIR / f"_wiki_{lang}.md"
            wiki_file.write_text(TRANSLATIONS[lang]['wiki_content'])

        # ملف هيستوري واحد (سيتم تحويله حسب اللغة)
        HISTORY_FILE.write_text(TRANSLATIONS[self.current_language]['history_template'])

        console.print(f"[green]{self.t('vault_created')}[/green]")
        console.print(f"📁 Location: {CAMPAIGNS_DIR}")

    def find_active_campaign(self):
        """البحث عن الحملة النشطة"""
        if not CAMPAIGNS_DIR.exists():
            return None

        active_campaigns = []
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
                            active_campaigns.append({
                                'path': folder,
                                'data': data,
                                'file': campaign_file,
                                'recovery_end': recovery_end
                            })
            except Exception as e:
                console.print(f"[red]Error reading {folder.name}: {e}[/red]")

        return active_campaigns

    def get_current_milestone(self, campaign_file):
        """استخراج الـmilestone الحالية"""
        content = campaign_file.read_text()
        lines = content.split('\n')

        milestones = []
        in_milestones = False

        for line in lines:
            if line.strip() == "## Milestones" or line.strip() == "## المراحل" or line.strip() == "## אבני דרך":
                in_milestones = True
                continue
            if in_milestones:
                if line.strip().startswith("##"):
                    break
                if line.strip().startswith("- [ ]"):
                    milestones.append({
                        'text': line.strip()[6:],
                        'status': 'pending',
                        'line': line
                    })
                elif line.strip().startswith("- [x]"):
                    milestones.append({
                        'text': line.strip()[6:],
                        'status': 'done',
                        'line': line
                    })
                elif line.strip().startswith("- [-]"):
                    milestones.append({
                        'text': line.strip()[6:],
                        'status': 'skipped',
                        'line': line
                    })

        # إرجاع أول milestone معلقة
        for i, m in enumerate(milestones):
            if m['status'] == 'pending':
                return i, m, milestones

        return None, None, milestones

    def calculate_days_left(self, end_date, recovery_end):
        """حساب الأيام المتبقية"""
        today = datetime.now().date()

        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        if isinstance(recovery_end, str):
            recovery_end = datetime.strptime(recovery_end, '%Y-%m-%d').date()

        if today <= end_date:
            days = (end_date - today).days
            return days, "campaign"
        else:
            return recovery_end, "rest"

    def display_campaign(self, campaign):
        """عرض الحملة النشطة"""
        data = campaign['data']
        campaign_file = campaign['file']

        milestone_idx, current_milestone, all_milestones = self.get_current_milestone(campaign_file)

        days_info, mode = self.calculate_days_left(data['end'], campaign['recovery_end'])

        if mode == "campaign":
            # واجهة الحملة النشطة
            title = f"[bold cyan]{self.t('campaign')}: {data['name']}[/bold cyan]"

            content = Text()
            content.append(f"{self.t('week')}: {data.get('current_week', 1)}/6\n", style="bold yellow")
            content.append(f"{self.t('started')}: {data['start']}\n\n", style="dim")

            if current_milestone:
                content.append(f"{self.t('current_milestone')}:\n", style="bold green")
                content.append(f"[ ] {milestone_idx + 1}. {current_milestone['text']}\n\n", style="white")
            else:
                content.append(f"{self.t('all_completed')}\n\n", style="bold green")

            # الأزرار
            content.append(f"{self.t('actions')}:\n", style="bold")
            content.append(f"{self.t('mark_done')}\n", style="green")
            content.append(f"{self.t('mark_wont')}\n", style="red")
            content.append(f"{self.t('add_note')}\n", style="cyan")
            content.append(f"{self.t('open_folder')}\n\n", style="yellow")

            content.append(f"{self.t('history')}  {self.t('wiki')}  {self.t('language')}\n", style="dim")

            # الأيام المتبقية
            days_text = Text()
            days_text.append(f"\n{days_info:>3}\n", style="bold magenta")
            days_text.append(f"{self.t('days')}\n", style="dim")
            days_text.append(f"{self.t('left')}", style="dim")

            # دمج المحتوى
            panel_content = Text()
            lines = content.split('\n')
            days_lines = days_text.split('\n')

            max_len = max(len(line) for line in lines)
            for i, line in enumerate(lines):
                panel_content.append(line)
                if i < len(days_lines):
                    spaces = max_len - len(line) + 2
                    panel_content.append(" " * spaces)
                    panel_content.append(days_lines[i])
                panel_content.append("\n")

            panel = Panel(panel_content, title=title, border_style="cyan")
            console.print(panel)

            # الخيارات
            choice = Prompt.ask(f"\n{self.t('choice')}", 
                              choices=["✓", "✗", "n", "f", "h", "w", "l", "q"], 
                              default="q")

            if choice == "✓":
                self.mark_milestone(campaign_file, milestone_idx, "done")
            elif choice == "✗":
                self.mark_milestone(campaign_file, milestone_idx, "skip")
            elif choice == "n":
                self.add_note(campaign, milestone_idx, current_milestone)
            elif choice == "f":
                self.open_in_terminal(campaign['path'])
            elif choice == "h":
                self.view_file(HISTORY_FILE)
            elif choice == "w":
                self.view_file(self.get_wiki_file())
            elif choice == "l":
                self.change_language()
                self.run()  # إعادة عرض الواجهة
            elif choice == "q":
                return

        else:  # rest mode
            title = f"[bold magenta]{self.t('recovery_period')}[/bold magenta]"

            content = Text()
            content.append(f"\n     {self.t('in_recovery')}\n\n", style="bold green")
            content.append(f"       {self.t('recovery_ends')}:\n", style="dim")
            content.append(f"      {days_info.strftime('%B %d, %Y')}\n\n", style="bold yellow")
            content.append(f"\n{self.t('rest_now')}\n", style="cyan")
            content.append(f"{self.t('configure_next')}\n", style="yellow")
            content.append(f"{self.t('language')}\n", style="dim")

            panel = Panel(content, title=title, border_style="magenta")
            console.print(panel)

            choice = Prompt.ask(f"\n{self.t('choice')}", choices=["r", "c", "l"], default="r")

            if choice == "c":
                self.create_new_campaign()
            elif choice == "l":
                self.change_language()
                self.run()

    def mark_milestone(self, campaign_file, idx, action):
        """تعليم milestone كمنجزة أو ملغية"""
        content = campaign_file.read_text()
        lines = content.split('\n')

        milestone_count = 0
        for i, line in enumerate(lines):
            if line.strip().startswith("- [ ]"):
                if milestone_count == idx:
                    if action == "done":
                        lines[i] = line.replace("- [ ]", "- [x]")
                        self.notify(self.t('milestone_completed'), 
                                  f"{line.strip()[6:]}\n{self.t('milestone_completed_msg')}")
                    elif action == "skip":
                        lines[i] = line.replace("- [ ]", "- [-]")
                        self.notify(self.t('milestone_skipped'), 
                                  f"{line.strip()[6:]}\n{self.t('milestone_skipped_msg')}")
                    break
                milestone_count += 1

        campaign_file.write_text('\n'.join(lines))

    def add_note(self, campaign, milestone_idx, milestone):
        """إضافة note"""
        notes_dir = campaign['path'] / "notes"
        notes_dir.mkdir(exist_ok=True)

        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M:%S")

        milestone_name = milestone['text'] if milestone else "General"
        filename = f"{date_str}-milestone-{milestone_idx + 1}.md"
        note_file = notes_dir / filename

        # قراءة الـtemplate حسب اللغة
        template = TRANSLATIONS[self.current_language]['note_template']
        content = template.format(
            campaign_name=campaign['data']['name'],
            milestone_name=milestone_name,
            date=date_str,
            time=time_str
        )

        note_file.write_text(content)

        # فتح الـeditor
        editor = os.environ.get('EDITOR', 'nano')
        subprocess.run([editor, str(note_file)])

    def open_in_terminal(self, path):
        """فتح terminal في المسار"""
        subprocess.Popen(['alacritty', '--working-directory', str(path)])

    def view_file(self, file_path):
        """عرض ملف"""
        pager = os.environ.get('PAGER', 'less')
        subprocess.run([pager, str(file_path)])

    def create_new_campaign(self):
        """إنشاء حملة جديدة"""
        name = Prompt.ask(self.t('campaign_name'))

        # حساب التواريخ
        start = datetime.now().date()
        end = start + timedelta(days=42)  # 6 أسابيع

        folder_name = f"Campaign-{name.replace(' ', '-')}"
        campaign_path = CAMPAIGNS_DIR / folder_name
        campaign_path.mkdir(exist_ok=True)

        # قراءة الـtemplate حسب اللغة
        template = TRANSLATIONS[self.current_language]['campaign_template']
        content = template.format(
            start=start.strftime("%Y-%m-%d"),
            end=end.strftime("%Y-%m-%d")
        )

        campaign_file = campaign_path / "campaign.md"
        campaign_file.write_text(content)

        # إنشاء sum.md
        sum_file = campaign_path / "sum.md"
        sum_file.write_text(f"# {name} - Summary\n\n")

        console.print(f"[green]{self.t('campaign_created')}: {folder_name}[/green]")

        # فتح للتعديل
        if Confirm.ask(self.t('open_editing')):
            editor = os.environ.get('EDITOR', 'nano')
            subprocess.run([editor, str(campaign_file)])

    def notify(self, title, message):
        """إرسال notification"""
        subprocess.run(['notify-send', '-u', 'normal', title, message])

    def run(self):
        """تشغيل الـTUI"""
        console.clear()

        # التحقق من وجود الـvault
        if not CAMPAIGNS_DIR.exists():
            console.print(f"[yellow]{self.t('no_vault')}[/yellow]")
            if Confirm.ask(self.t('create_vault')):
                self.init_vault()
            else:
                return

        # البحث عن حملة نشطة
        campaigns = self.find_active_campaign()

        if not campaigns:
            console.print(f"[yellow]{self.t('no_active')}[/yellow]")
            if Confirm.ask(self.t('create_new')):
                self.create_new_campaign()
            return

        if len(campaigns) > 1:
            console.print(f"[red]{self.t('conflict')}[/red]")
            for c in campaigns:
                console.print(f"  - {c['path'].name}")
            console.print(f"\n{self.t('fix_manually')} ~/Campaigns/")
            return

        # عرض الحملة
        self.display_campaign(campaigns[0])

def main():
    """نقطة البداية"""
    manager = CampaignManager()

    # التحقق من الأوامر
    if len(sys.argv) > 1:
        if sys.argv[1] == "init":
            manager.init_vault()
            return

    manager.run()

if __name__ == "__main__":
    main()