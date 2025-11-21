🎯 Setup بسيط جداً:
1. ضع الملفات:
mkdir -p ~/.config/campaigno
cd ~/.config/campaigno

# ضع:
# - campaign-prompt.py
# - campaign-info.py
# - campaign-edit
2. اجعلها قابلة للتنفيذ:
chmod +x campaign-prompt.py
chmod +x campaign-info.py
chmod +x campaign-edit

## 🔧 إضافة للـBash:

### في `~/.bashrc`:

```bash
# Campaign Manager
export PATH="$HOME/.config/campaigno:$PATH"

# Prompt
campaign_status() {
    python3 $HOME/.config/campaigno/campaign-prompt.py 2>/dev/null || echo ""
}

# إضافة للـPS1
PS1='\[\e[32m\]\u@\h\[\e[0m\]:\[\e[34m\]\w\[\e[0m\]$(campaign_status) \$ '
```

---

## 🔧 إضافة للـZsh:

### في `~/.zshrc`:

```bash
# Campaign Manager
export PATH="$HOME/.config/campaigno:$PATH"

# Prompt
campaign_status() {
    python3 $HOME/.config/campaigno/campaign-prompt.py 2>/dev/null || echo ""
}

# إضافة للـRPROMPT
RPROMPT='$(campaign_status)'
```

---

## 🚀 بعد كده:

```bash
# أعد تحميل
source ~/.bashrc  # أو ~/.zshrc

# اختبر
campaign-info
campaign-edit
```

---

**كده تمام! 
