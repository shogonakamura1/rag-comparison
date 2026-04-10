#!/usr/bin/env bash
# tmux で4ペインを開き、それぞれに役割を持たせた claude を起動するスクリプト
#
# レイアウト:
#   ┌─────────────┬─────────────┐
#   │             │             │
#   │  Lead/Sup.  │  Developer1 │
#   │             │             │
#   ├─────────────┼─────────────┤
#   │             │             │
#   │  QA Eng.    │  Developer2 │
#   │             │             │
#   └─────────────┴─────────────┘
#
# 使い方:
#   ./scripts/tmux-team.sh             # セッションを起動
#   ./scripts/tmux-team.sh kill        # セッションを終了

set -euo pipefail

SESSION="rag-team"
PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
AGENTS_DIR="${PROJECT_DIR}/.claude/agents"

# kill サブコマンド
if [[ "${1:-}" == "kill" ]]; then
  tmux kill-session -t "$SESSION" 2>/dev/null && echo "Session '$SESSION' killed." || echo "No session to kill."
  exit 0
fi

# 既存セッションがあればアタッチして終了
if tmux has-session -t "$SESSION" 2>/dev/null; then
  echo "Session '$SESSION' already exists. Attaching..."
  tmux attach-session -t "$SESSION"
  exit 0
fi

# YAML フロントマターを取り除いて role 本文だけを取り出す関数
extract_body() {
  awk '/^---$/{c++; next} c>=2' "$1"
}

# 各エージェントのシステムプロンプトを生成
LEAD_PROMPT="$(extract_body "${AGENTS_DIR}/lead-supervisor.md")"
DEV_PROMPT="$(extract_body "${AGENTS_DIR}/developer.md")"
QA_PROMPT="$(extract_body "${AGENTS_DIR}/qa-engineer.md")"

# tmux セッション作成（pane 0 = Lead）
tmux new-session -d -s "$SESSION" -n team -c "$PROJECT_DIR"

# 縦に分割 → pane 1 (右上 = Developer 1)
tmux split-window -h -t "$SESSION:0" -c "$PROJECT_DIR"

# pane 0 (左) を上下に分割 → pane 2 (左下 = QA)
tmux split-window -v -t "$SESSION:0.0" -c "$PROJECT_DIR"

# pane 1 (右上) を上下に分割 → pane 3 (右下 = Developer 2)
tmux split-window -v -t "$SESSION:0.1" -c "$PROJECT_DIR"

# ペインタイトルを表示する設定
tmux set -t "$SESSION" pane-border-status top
tmux set -t "$SESSION" pane-border-format " #{pane_title} "

# 各ペインのタイトルを設定
tmux select-pane -t "$SESSION:0.0" -T "Lead/Supervisor"
tmux select-pane -t "$SESSION:0.1" -T "Developer 1"
tmux select-pane -t "$SESSION:0.2" -T "QA Engineer"
tmux select-pane -t "$SESSION:0.3" -T "Developer 2"

# 各ペインで claude を起動（--append-system-prompt にロール本文を渡す）
launch_claude() {
  local pane="$1"
  local prompt="$2"
  local label="$3"
  # シングルクォートをエスケープしてシェルに安全に渡す
  local escaped
  escaped=$(printf '%s' "$prompt" | sed "s/'/'\\\\''/g")
  tmux send-keys -t "$pane" "clear && echo '=== ${label} ===' && claude --append-system-prompt '${escaped}'" C-m
}

launch_claude "$SESSION:0.0" "$LEAD_PROMPT" "Lead / Supervisor"
launch_claude "$SESSION:0.1" "$DEV_PROMPT"  "Developer 1 (dev-1)"
launch_claude "$SESSION:0.2" "$QA_PROMPT"   "QA Engineer"
launch_claude "$SESSION:0.3" "$DEV_PROMPT"  "Developer 2 (dev-2)"

# Lead ペインを選択してアタッチ
tmux select-pane -t "$SESSION:0.0"
tmux attach-session -t "$SESSION"
