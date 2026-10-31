// X の投稿画面・返信欄で「コンテンツ開示 → AIで生成」をオンにする。
// 画面の位置ではなく、X の部品の名前（data-testid・文字）で探して押す。
// 投稿・送信は絶対にしない。
// hotkey.js が先に読み込まれている（manifest の content_scripts の順）。

(() => {
  const AI_LABEL_TEXTS = ["AIで生成", "Made with AI", "AI-generated", "Generated with AI"];
  const DONE_TEXTS = ["完了", "Done"];

  const settings = { hotkey: XH_DEFAULT_HOTKEY, showToast: true };

  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

  async function waitFor(fn, timeout = 3000) {
    const end = Date.now() + timeout;
    while (Date.now() < end) {
      const v = fn();
      if (v) return v;
      await sleep(80);
    }
    return null;
  }

  const isVisible = (el) => el && el.getClientRects().length > 0;

  // ラベルを付ける相手の入力欄を選ぶ：開いている投稿ダイアログ → 打っている欄 → 画面に見えている欄
  function findTextarea() {
    const all = [...document.querySelectorAll('[data-testid^="tweetTextarea_"][contenteditable="true"]')].filter(isVisible);
    if (all.length === 0) return null;
    const inDialog = all.filter((t) => t.closest('[role="dialog"]'));
    if (inDialog.length) return inDialog[inDialog.length - 1];
    const active = all.find((t) => t.contains(document.activeElement));
    return active ?? all[0];
  }

  // 入力欄から親をたどり、同じ投稿欄の旗マーク（コンテンツ開示）を探す
  function findDisclosureButton(textarea) {
    for (let el = textarea.parentElement; el && el !== document.body; el = el.parentElement) {
      const btn = el.querySelector('[data-testid="contentDisclosureButton"]');
      if (btn) return btn;
    }
    return null;
  }

  // 開示メニューの中の「AIで生成」スイッチ。
  // 文字で見つからない表示言語のときは、スイッチがちょうど 2 つ（有料パートナーシップ・AI）なら後ろのほうを使う
  function findAiSwitch() {
    const labels = [...document.querySelectorAll('[role="dialog"] label')];
    const label = labels.find((l) => AI_LABEL_TEXTS.some((t) => l.innerText.includes(t)));
    if (label) return label.querySelector('input[role="switch"], input[type="checkbox"]');
    if (!location.pathname.endsWith("/content_disclosure")) return null;
    const switches = [...document.querySelectorAll('[role="dialog"] input[role="switch"]')].filter((s) => s.closest("label"));
    return switches.length === 2 ? switches[1] : null;
  }

  function findDoneButton(dialog) {
    const buttons = [...dialog.querySelectorAll("button")];
    return buttons.find((b) => DONE_TEXTS.includes(b.innerText.trim())) ??
      (buttons.length === 1 ? buttons[0] : null);
  }

  function focusAtEnd(textarea) {
    textarea.focus();
    const sel = window.getSelection();
    const range = document.createRange();
    range.selectNodeContents(textarea);
    range.collapse(false);
    sel.removeAllRanges();
    sel.addRange(range);
  }

  let toastTimer;
  function toast(message, ok = true) {
    if (ok && !settings.showToast) return;
    let el = document.getElementById("x-helper-toast");
    if (!el) {
      el = document.createElement("div");
      el.id = "x-helper-toast";
      Object.assign(el.style, {
        position: "fixed", left: "50%", bottom: "32px", transform: "translateX(-50%)",
        zIndex: 2147483647, padding: "10px 18px", borderRadius: "999px",
        font: "bold 14px system-ui, sans-serif", color: "#fff",
        boxShadow: "0 4px 16px rgba(0,0,0,.25)", pointerEvents: "none", transition: "opacity .2s",
      });
      document.body.appendChild(el);
    }
    el.textContent = message;
    el.style.background = ok ? "#7c4dff" : "#d0242f";
    el.style.opacity = "1";
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => (el.style.opacity = "0"), 1800);
  }

  let running = false;

  async function addAiLabel() {
    if (running) return;
    running = true;
    try {
      const textarea = findTextarea();
      if (!textarea) return toast("投稿欄・返信欄が見つかりません", false);

      // 返信欄は、一度入力欄にフォーカスしないと旗マークが出てこない
      let button = findDisclosureButton(textarea);
      if (!button) {
        textarea.focus();
        button = await waitFor(() => findDisclosureButton(textarea), 1500);
      }
      if (!button) return toast("旗マーク（コンテンツ開示）が見つかりません", false);

      button.click();
      const sw = await waitFor(findAiSwitch);
      if (!sw) return toast("「AIで生成」のスイッチが見つかりません", false);

      const wasOn = sw.checked;
      if (!wasOn) {
        sw.click();
        await waitFor(() => sw.checked, 1000);
      }
      const nowOn = sw.checked;

      findDoneButton(sw.closest('[role="dialog"]'))?.click();
      await waitFor(() => !findAiSwitch(), 1500);

      const target = findTextarea() ?? textarea;
      focusAtEnd(target);

      if (!nowOn) toast("オンにできませんでした", false);
      else toast(wasOn ? "AIラベルはすでにON" : "AIラベル ON ✓");
    } catch (e) {
      console.error("[ai-label-onekey]", e);
      toast("エラー：" + e.message, false);
    } finally {
      running = false;
    }
  }

  // キーはページの中で直接受ける。日本語入力中でも効くよう、文字ではなくキーの場所（code）で見る
  window.addEventListener(
    "keydown",
    (e) => {
      if (!xhHotkeyMatches(settings.hotkey, e)) return;
      e.preventDefault();
      e.stopImmediatePropagation();
      if (!e.repeat) addAiLabel();
    },
    true
  );

  if (globalThis.chrome?.storage?.sync) {
    chrome.storage.sync.get(settings).then((s) => Object.assign(settings, s));
    chrome.storage.onChanged.addListener((changes, area) => {
      if (area !== "sync") return;
      for (const [k, { newValue }] of Object.entries(changes)) {
        if (k in settings) settings[k] = newValue ?? (k === "hotkey" ? XH_DEFAULT_HOTKEY : true);
      }
    });
    chrome.runtime.onMessage.addListener((msg) => {
      if (msg?.command === "add-ai-label") addAiLabel();
    });
  }
  globalThis.__xHelperAddAiLabel = addAiLabel;

  // 読み込めているかを外から確かめるための目印
  document.documentElement.dataset.aiLabelOnekey = "ready";
})();
