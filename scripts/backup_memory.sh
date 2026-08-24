#!/bin/bash
# Бэкап памяти Нейро: memory/ + DNA-файлы (локально) + git push в GitHub
WS="/root/.openclaw/workspace-neuro"
BACKUP_DIR="$WS/backup/memory-$(date +%Y-%m-%d_%H%M)"
mkdir -p "$BACKUP_DIR"
cp -r "$WS/memory" "$BACKUP_DIR/" 2>/dev/null
for f in SOUL MEMORY USER IDENTITY GOALS MISSION PROJECTS PREFERENCES LEARNED AGENTS TOOLS; do
  [ -f "$WS/$f.md" ] && cp "$WS/$f.md" "$BACKUP_DIR/"
done
# оставить только последние 14 локальных бэкапов
ls -dt "$WS"/backup/memory-* 2>/dev/null | tail -n +15 | xargs rm -rf 2>/dev/null

# git push в GitHub (полный бэкап workspace)
cd "$WS" || exit 1
git add -A 2>/dev/null
git commit -m "backup: $(date +%Y-%m-%d_%H%M)" 2>/dev/null
git push origin master 2>&1 | tail -2

echo "Backup + push done: $BACKUP_DIR"
