const $ = (id) => document.getElementById(id);

let recording = false;

function showMessage(text, kind = "ok") {
  const el = $("message");
  el.textContent = text;
  el.className = "message " + kind;
}

async function load() {
  const { hotkey, showToast } = await chrome.storage.sync.get({ hotkey: XH_DEFAULT_HOTKEY, showToast: true });
  $("current").textContent = xhHotkeyLabel(hotkey);
  $("showToast").checked = showToast;
}

async function saveHotkey(hk) {
  await chrome.storage.sync.set({ hotkey: hk });
  $("current").textContent = xhHotkeyLabel(hk);
}

function startRecording() {
  recording = true;
  $("recorder").hidden = false;
  $("preview").textContent = "…";
  $("change").disabled = true;
  showMessage("");
}

function stopRecording() {
  recording = false;
  $("recorder").hidden = true;
  $("change").disabled = false;
}

window.addEventListener(
  "keydown",
  async (e) => {
    if (!recording) return;
    e.preventDefault();
    e.stopPropagation();

    if (e.code === "Escape" && !e.ctrlKey && !e.altKey && !e.shiftKey && !e.metaKey) {
      stopRecording();
      showMessage("変更をやめました", "ok");
      return;
    }

    const hk = xhHotkeyFromEvent(e);
    // Ctrl だけ押している途中などは、組み合わせの途中として見せるだけ
    if (XH_MODIFIER_CODES.has(e.code)) {
      $("preview").textContent = xhHotkeyLabel({ ...hk, code: "" }).replace(/ \+ $/, "") + " + …";
      return;
    }
    $("preview").textContent = xhHotkeyLabel(hk);

    const result = xhValidateHotkey(hk);
    if (!result.ok) {
      showMessage(result.error, "error");
      return; // 記録は続ける。別の組み合わせを押してもらう
    }
    await saveHotkey(hk);
    stopRecording();
    if (result.warning) showMessage("保存しました。" + result.warning, "warn");
    else showMessage(`${xhHotkeyLabel(hk)} に変えました`, "ok");
  },
  true
);

$("change").addEventListener("click", startRecording);

$("reset").addEventListener("click", async () => {
  stopRecording();
  await saveHotkey(XH_DEFAULT_HOTKEY);
  showMessage(`初期設定（${xhHotkeyLabel(XH_DEFAULT_HOTKEY)}）に戻しました`, "ok");
});

$("showToast").addEventListener("change", (e) => {
  chrome.storage.sync.set({ showToast: e.target.checked });
});

$("version").textContent = "バージョン " + chrome.runtime.getManifest().version;
load();
