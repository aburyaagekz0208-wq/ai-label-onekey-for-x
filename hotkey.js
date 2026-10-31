// キーの組み合わせの扱い（content.js と設定画面で共用）
// 形：{ ctrl, shift, alt, meta, code }（code は KeyboardEvent.code。日本語入力中でも変わらない）

const XH_DEFAULT_HOTKEY = { ctrl: true, shift: true, alt: false, meta: false, code: "KeyY" };

const XH_MODIFIER_CODES = new Set([
  "ControlLeft", "ControlRight", "ShiftLeft", "ShiftRight",
  "AltLeft", "AltRight", "MetaLeft", "MetaRight", "OSLeft", "OSRight",
]);

function xhHotkeyFromEvent(e) {
  return { ctrl: e.ctrlKey, shift: e.shiftKey, alt: e.altKey, meta: e.metaKey, code: e.code };
}

function xhHotkeyMatches(hk, e) {
  return !!hk && e.code === hk.code &&
    e.ctrlKey === !!hk.ctrl && e.shiftKey === !!hk.shift &&
    e.altKey === !!hk.alt && e.metaKey === !!hk.meta;
}

const XH_CODE_NAMES = {
  Space: "Space", Enter: "Enter", Tab: "Tab", Backspace: "Backspace", Delete: "Delete",
  Insert: "Insert", Home: "Home", End: "End", PageUp: "PageUp", PageDown: "PageDown",
  ArrowUp: "↑", ArrowDown: "↓", ArrowLeft: "←", ArrowRight: "→",
  Minus: "-", Equal: "=", BracketLeft: "[", BracketRight: "]", Backslash: "\\",
  Semicolon: ";", Quote: "'", Backquote: "`", Comma: ",", Period: ".", Slash: "/",
  IntlRo: "ろ", IntlYen: "¥", Convert: "変換", NonConvert: "無変換",
};

function xhCodeName(code) {
  if (/^Key[A-Z]$/.test(code)) return code.slice(3);
  if (/^Digit\d$/.test(code)) return code.slice(5);
  if (/^Numpad\d$/.test(code)) return "テンキー" + code.slice(6);
  if (/^F\d{1,2}$/.test(code)) return code;
  return XH_CODE_NAMES[code] ?? code;
}

function xhHotkeyLabel(hk) {
  if (!hk) return "なし";
  const parts = [];
  if (hk.ctrl) parts.push("Ctrl");
  if (hk.alt) parts.push("Alt");
  if (hk.shift) parts.push("Shift");
  if (hk.meta) parts.push("Win");
  parts.push(xhCodeName(hk.code));
  return parts.join(" + ");
}

const xhIsFunctionKey = (code) => /^F\d{1,2}$/.test(code);

// Chrome 自身が先に使ってしまい、ページの中では受け取れないキー
const XH_BLOCKED = [
  "Ctrl+T", "Ctrl+N", "Ctrl+W", "Ctrl+Shift+T", "Ctrl+Shift+N", "Ctrl+Shift+W",
  "Ctrl+Tab", "Ctrl+Shift+Tab", "Ctrl+Shift+Q", "Ctrl+PageUp", "Ctrl+PageDown",
  "Alt+F4",
];

// ブラウザや X がふだん使っているキー（選べるが、元の動きが効かなくなる）
const XH_WARN = {
  "Ctrl+Enter": "X の送信", "Ctrl+A": "全部選ぶ", "Ctrl+C": "コピー", "Ctrl+V": "貼り付け",
  "Ctrl+X": "切り取り", "Ctrl+Z": "元に戻す", "Ctrl+Y": "やり直し", "Ctrl+Shift+Z": "やり直し",
  "Ctrl+B": "太字", "Ctrl+I": "斜体", "Ctrl+F": "ページ内検索", "Ctrl+P": "印刷",
  "Ctrl+S": "保存", "Ctrl+R": "再読み込み", "Ctrl+L": "アドレスバー", "Ctrl+D": "ブックマーク",
  "Ctrl+H": "履歴", "Ctrl+J": "ダウンロード", "Ctrl+K": "検索", "Ctrl+U": "ソース表示",
  "Ctrl+Shift+I": "開発者ツール", "Ctrl+Shift+J": "開発者ツール", "Ctrl+Shift+C": "開発者ツール",
  "Ctrl+Shift+V": "書式なし貼り付け", "Ctrl+Shift+B": "ブックマークバー", "Ctrl+Shift+Delete": "履歴の削除",
  F1: "ヘルプ", F3: "検索", F5: "再読み込み", F6: "アドレスバー", F7: "キャレットブラウズ",
  F10: "メニュー", F11: "全画面", F12: "開発者ツール",
};

function xhHotkeyKey(hk) {
  const parts = [];
  if (hk.ctrl) parts.push("Ctrl");
  if (hk.alt) parts.push("Alt");
  if (hk.shift) parts.push("Shift");
  if (hk.meta) parts.push("Win");
  parts.push(xhCodeName(hk.code));
  return parts.join("+");
}

// 設定に使えるか確かめる。{ ok, error?, warning? }
function xhValidateHotkey(hk) {
  if (!hk.code || XH_MODIFIER_CODES.has(hk.code)) {
    return { ok: false, error: "Ctrl などと一緒に、文字のキーも押してください" };
  }
  if (!hk.ctrl && !hk.alt && !hk.meta && !xhIsFunctionKey(hk.code)) {
    return { ok: false, error: "文字を打つときと区別するため、Ctrl か Alt と組み合わせてください（F1〜F12 は単独でも使えます）" };
  }
  const key = xhHotkeyKey(hk);
  if (XH_BLOCKED.includes(key)) {
    return { ok: false, error: `${key} は Chrome が先に使うため、ページの中では受け取れません` };
  }
  const warn = XH_WARN[key];
  return warn ? { ok: true, warning: `${key} はふだん「${warn}」に使われています。X の上ではこの拡張の動きに置き換わります` } : { ok: true };
}
