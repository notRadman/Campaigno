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
WIKI_FILE = CAMPAIGNS_DIR / "_wiki.md"
HISTORY_FILE = CAMPAIGNS_DIR / "_history.md"

# للتحقق إذا كان يعمل من venv
SCRIPT_DIR = Path(__file__).parent if '__file__' in globals() else Path.cwd()

class CampaignManager:
    def __init__(self):
        self.current_campaign = None
        self.campaign_path = None
        
    def init_vault(self):
        """إنشاء الـvault والـtemplates"""
        if CAMPAIGNS_DIR.exists():
            console.print("[yellow]⚠️  Vault already exists![/yellow]")
            if not Confirm.ask("Recreate templates?"):
                return
        
        # إنشاء المجلدات
        CAMPAIGNS_DIR.mkdir(exist_ok=True)
        TEMPLATES_DIR.mkdir(exist_ok=True)
        
        # campaign template
        campaign_template = """---
name: Campaign 01
start: {start}
end: {end}
status: active
recovery_end: 
current_week: 1
---

# Campaign 01: [اسم الحملة]

## Description
[وصف الهدف من الحملة]

## Milestones
- [ ] Milestone 1: 
- [ ] Milestone 2: 
- [ ] Milestone 3: 
- [ ] Milestone 4: 
- [ ] Milestone 5: 

## Accountability
**Person:** [اسم الشخص]
**Check-in:** Every [Sunday/week]
"""
        
        # wiki content
        wiki_content = """# Campaign System Wiki

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
"""
        
        # history template
        history_content = """# Campaign History

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

"""
        
        # note template
        note_template = """# {campaign_name} - {milestone_name}
Date: {date}
Time: {time}

## Notes

"""
        
        # حفظ الملفات
        (TEMPLATES_DIR / "campaign-template.md").write_text(campaign_template)
        (TEMPLATES_DIR / "note-template.md").write_text(note_template)
        WIKI_FILE.write_text(wiki_content)
        HISTORY_FILE.write_text(history_content)
        
        console.print("[green]✅ Vault created successfully![/green]")
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
                # استخراج YAML frontmatter
                if content.startswith("---"):
                    yaml_end = content.find("---", 3)
                    yaml_content = content[3:yaml_end]
                    data = yaml.safe_load(yaml_content)
                    
                    status = data.get('status', 'active')
                    
                    # التحقق من التواريخ
                    if status in ['active', 'rest']:
                        start_date = datetime.strptime(data['start'], '%Y-%m-%d').date()
                        end_date = datetime.strptime(data['end'], '%Y-%m-%d').date()
                        
                        # حساب نهاية الاستشفاء
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
            if line.strip() == "## Milestones":
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
            # في الحملة
            days = (end_date - today).days
            return days, "campaign"
        else:
            # في الاستشفاء
            return recovery_end, "rest"
    
    def display_campaign(self, campaign):
        """عرض الحملة النشطة"""
        data = campaign['data']
        campaign_file = campaign['file']
        
        milestone_idx, current_milestone, all_milestones = self.get_current_milestone(campaign_file)
        
        days_info, mode = self.calculate_days_left(data['end'], campaign['recovery_end'])
        
        if mode == "campaign":
            # واجهة الحملة النشطة
            title = f"[bold cyan]Campaign: {data['name']}[/bold cyan]"
            
            content = Text()
            content.append(f"Week: {data.get('current_week', 1)}/6\n", style="bold yellow")
            content.append(f"Started: {data['start']}\n\n", style="dim")
            
            if current_milestone:
                content.append("Current Milestone:\n", style="bold green")
                content.append(f"[ ] {milestone_idx + 1}. {current_milestone['text']}\n\n", style="white")
            else:
                content.append("🎉 All milestones completed!\n\n", style="bold green")
            
            # الأزرار
            content.append("Actions:\n", style="bold")
            content.append("[✓] Mark as Done\n", style="green")
            content.append("[✗] Mark as Won't Do\n", style="red")
            content.append("[N] Add Note\n", style="cyan")
            content.append("[F] Open folder in terminal\n\n", style="yellow")
            
            content.append("[H] History  [W] Wiki\n", style="dim")
            
            # الأيام المتبقية في الزاوية
            days_text = Text()
            days_text.append(f"\n{days_info:>3}\n", style="bold magenta")
            days_text.append("days\n", style="dim")
            days_text.append("left", style="dim")
            
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
            choice = Prompt.ask("\nChoice", choices=["✓", "✗", "n", "f", "h", "w", "q"], default="q")
            
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
                self.view_file(WIKI_FILE)
            elif choice == "q":
                return
                
        else:  # rest mode
            title = "[bold magenta]🌴 Recovery Period 🌴[/bold magenta]"
            
            content = Text()
            content.append("\n     You are in Recovery!\n\n", style="bold green")
            content.append("       Recovery ends on:\n", style="dim")
            content.append(f"      {days_info.strftime('%B %d, %Y')}\n\n", style="bold yellow")
            content.append("\n[R] Rest now, bro! (close)\n", style="cyan")
            content.append("[C] Configure coming campaign\n", style="yellow")
            
            panel = Panel(content, title=title, border_style="magenta")
            console.print(panel)
            
            choice = Prompt.ask("\nChoice", choices=["r", "c"], default="r")
            
            if choice == "c":
                self.create_new_campaign()
    
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
                        self.notify("🎉 Milestone Completed!", 
                                  f"{line.strip()[6:]}\nالحمد لله! استمر بقوة 💪")
                    elif action == "skip":
                        lines[i] = line.replace("- [ ]", "- [-]")
                        self.notify("📝 Milestone Skipped", 
                                  f"{line.strip()[6:]}\nلا بأس، المهم التقدم. لا تيأس من رحمة الله")
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
        
        # قراءة الـtemplate
        template = (TEMPLATES_DIR / "note-template.md").read_text()
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
        # للـsway
        subprocess.Popen(['alacritty', '--working-directory', str(path)])
    
    def view_file(self, file_path):
        """عرض ملف"""
        pager = os.environ.get('PAGER', 'less')
        subprocess.run([pager, str(file_path)])
    
    def create_new_campaign(self):
        """إنشاء حملة جديدة"""
        name = Prompt.ask("Campaign name")
        
        # حساب التواريخ
        start = datetime.now().date()
        end = start + timedelta(days=42)  # 6 أسابيع
        
        folder_name = f"Campaign-{name.replace(' ', '-')}"
        campaign_path = CAMPAIGNS_DIR / folder_name
        campaign_path.mkdir(exist_ok=True)
        
        # قراءة الـtemplate
        template = (TEMPLATES_DIR / "campaign-template.md").read_text()
        content = template.format(
            start=start.strftime("%Y-%m-%d"),
            end=end.strftime("%Y-%m-%d")
        )
        
        campaign_file = campaign_path / "campaign.md"
        campaign_file.write_text(content)
        
        # إنشاء sum.md
        sum_file = campaign_path / "sum.md"
        sum_file.write_text(f"# {name} - Summary\n\n")
        
        console.print(f"[green]✅ Campaign created: {folder_name}[/green]")
        
        # فتح للتعديل
        if Confirm.ask("Open for editing?"):
            editor = os.environ.get('EDITOR', 'nano')
            subprocess.run([editor, str(campaign_file)])
    
    def notify(self, title, message):
        """إرسال notification عبر mako"""
        subprocess.run(['notify-send', '-u', 'normal', title, message])
    
    def run(self):
        """تشغيل الـTUI"""
        console.clear()
        
        # التحقق من وجود الـvault
        if not CAMPAIGNS_DIR.exists():
            console.print("[yellow]No vault found![/yellow]")
            if Confirm.ask("Create vault?"):
                self.init_vault()
            else:
                return
        
        # البحث عن حملة نشطة
        campaigns = self.find_active_campaign()
        
        if not campaigns:
            console.print("[yellow]No active campaigns found![/yellow]")
            if Confirm.ask("Create new campaign?"):
                self.create_new_campaign()
            return
        
        if len(campaigns) > 1:
            console.print("[red]⚠️  CONFLICT: Multiple active campaigns![/red]")
            for c in campaigns:
                console.print(f"  - {c['path'].name}")
            console.print("\nPlease fix manually in ~/Campaigns/")
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
