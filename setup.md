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
3. أضف للـPATH في shell config:
export PATH="$HOME/.config/campaigno:$PATH"

campaign_status() {
    $HOME/.config/campaigno/campaign-prompt.py 2>/dev/null || echo ""
}
RPROMPT='$(campaign_status)'
4. اختر قالب وانسخه:
# للعربية
cp campaigns-template-ar.md ~/campaigns.md

# أو English
cp campaigns-template-en.md ~/campaigns.md

🎮 الاستخدام:
# عرض المعلومات
campaign-info

# تعديل الملف
campaign-edit

# الـprompt تلقائياً
~/code [C1•W3•18d left] $
