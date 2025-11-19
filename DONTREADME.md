# Campaign Manager

نظام بسيط لإدارة حملات العمل (6 أسابيع عمل + 2 أسبوع استشفاء) معتمد على Markdown وPython TUI.

## ✨ المميزات

- 🎯 **بسيط** - Markdown-based، سهل القراءة والتعديل
- 📊 **TUI جميل** - واجهة نصية بسيطة بـRich
- ⚡ **سريع** - يعمل من الـprompt مباشرة
- 🔒 **معزول** - كل dependencies في venv
- 🚀 **محمول** - يعمل على أي Linux/Unix

## 📦 المتطلبات

```bash
# Void Linux
sudo xbps-install -S python3 libnotify

# Arch Linux
sudo pacman -S python libnotify

# Debian/Ubuntu
sudo apt install python3 python3-venv libnotify-bin
```

## 🚀 التثبيت

### 1. Clone المستودع:
```bash
git clone https://github.com/YOUR_USERNAME/campaign-manager.git
cd campaign-manager
cp -r . ~/.config/campaigno/
```

### 2. شغل الـsetup:
```bash
cd ~/.config/campaigno
chmod +x setup.sh
./setup.sh
```

### 3. أضف للـshell config:

**للـBash** (`~/.bashrc`):
```bash
# Campaign Manager
export PATH="$HOME/.config/campaigno:$PATH"

# Prompt integration (optional)
campaign_status() {
    $HOME/.config/campaigno/campaign-prompt 2>/dev/null || echo ""
}
export PS1="\[\e[32m\]\u@\h\[\e[0m\]:\[\e[34m\]\w\[\e[0m\]\$(campaign_status) \$ "
```

**للـZsh** (`~/.zshrc`):
```bash
# Campaign Manager
export PATH="$HOME/.config/campaigno:$PATH"

# Prompt integration (optional)
campaign_status() {
    $HOME/.config/campaigno/campaign-prompt 2>/dev/null || echo ""
}
RPROMPT='$(campaign_status)'
```

### 4. أعد تحميل الـshell:
```bash
source ~/.bashrc  # أو ~/.zshrc
```

### 5. ابدأ:
```bash
campaign-tui init
```

## 🎮 الاستخدام

### فتح الـTUI:
```bash
campaign-tui
```

### إنشاء حملة جديدة:
```bash
campaign-tui init
```

### الـPrompt:
سيظهر تلقائياً:
```bash
~/code [C1•W3•18d] $   # في الحملة - 18 يوم متبقي
~/code [R•5d] $        # في الاستشفاء - 5 أيام متبقية
```

### Sway Keybinding (اختياري):
أضف في `~/.config/sway/config`:
```
bindsym Mod1+Shift+g exec alacritty -e $HOME/.config/campaigno/campaign-tui
```

## 📁 هيكل البيانات

```
~/Campaigns/
├── _templates/              # قوالب الحملات
├── _wiki.md                # شرح النظام
├── _history.md             # سجل الحملات
└── Campaign-Name/
    ├── campaign.md         # معلومات الحملة
    ├── sum.md             # الملخص والدروس
    └── notes/             # نوتات يومية
```

## 🎯 النظام

### الفلسفة:
- **6 أسابيع عمل متواصل** - طويلة كفاية للإنجاز، قصيرة كفاية للإلحاح
- **2 أسبوع استشفاء** - التعافي العصبي والحفاظ على الزخم
- **8 حملات في السنة** - 48 أسبوع عمل

### القواعد:
1. هدف واحد واضح قابل للقياس
2. موعد نهائي حقيقي مع عواقب
3. حد أقصى 4-6 ساعات عمل مركز يومياً
4. نقطة مساءلة واضحة

## ⌨️ اختصارات الـTUI

- `✓` - تعليم milestone كمنجزة
- `✗` - تعليم milestone كـ"لن يتم"
- `n` - إضافة note
- `f` - فتح folder في terminal
- `h` - عرض الـhistory
- `w` - عرض الـwiki
- `q` - خروج

## 🔧 التخصيص

### تغيير مكان البيانات:
عدل في `campaign-tui.py` و `campaign-prompt.py`:
```python
CAMPAIGNS_DIR = Path.home() / "Your/Custom/Path"
```

### تغيير الـEditor:
```bash
export EDITOR=vim  # أو nano أو أي editor
```

### تغيير الـPager:
```bash
export PAGER=bat   # أو less
```

## 🗑️ إلغاء التثبيت

```bash
# حذف الملفات
rm -rf ~/.config/campaigno

# حذف من shell config
# (السطور اللي فيها campaign)

# حذف البيانات (اختياري)
rm -rf ~/Campaigns
```

## 🐛 استكشاف الأخطاء

### البرنامج لا يعمل:
```bash
# تحقق من dependencies
~/.config/campaigno/venv/bin/pip list

# شغل مباشرة
~/.config/campaigno/venv/bin/python3 ~/.config/campaigno/campaign-tui.py
```

### الـPrompt لا يظهر:
```bash
# تحقق من PATH
echo $PATH | grep campaigno

# اختبار يدوي
campaign-prompt

# أعد تحميل shell
source ~/.bashrc
```

## 📄 الترخيص

MIT License - استخدمه زي ما تحب!


## 🤝 المساهمة

المشروع مفتوح للمساهمات! افتح issue أو pull request.

---

**صُنع بـ ❤️ للإنتاجية الصحية والمستدامة**
