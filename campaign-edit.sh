#!/bin/bash
# Campaign Edit - Open campaigns file in editor

CAMPAIGNS_FILE="$HOME/campaigns.md"
EDITOR="${EDITOR:-nvim}"

# إنشاء الملف إذا لم يكن موجوداً
if [ ! -f "$CAMPAIGNS_FILE" ]; then
    cat > "$CAMPAIGNS_FILE" << 'EOF'
---
###TEMPLATE(remove it when copy)###
number:
name:
description:
start:
end: 
recovery_end: 
status: 
rate: 
---

EOF
    echo "✅ Created new campaigns file"
fi

# فتح الملف في المحرر
exec "$EDITOR" "$CAMPAIGNS_FILE"
