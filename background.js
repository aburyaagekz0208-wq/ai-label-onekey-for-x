// キーは content.js がページの中で直接受ける（設定画面で変えられる）。
// ここでは、ツールバーの拡張アイコンを押したときに、いまのタブへ伝える。
// タブの URL は "tabs" 権限がないと読めないので確かめない。X 以外のタブには届かないだけ。
chrome.action.onClicked.addListener(async (tab) => {
  if (!tab?.id) return;
  chrome.tabs.sendMessage(tab.id, { command: "add-ai-label" }).catch(() => {
    // X 以外のタブ、または拡張を入れる前から開いていた X のタブ（再読み込みで直る）
  });
});

// はじめて入れたときは設定画面（使い方つき）を開く
chrome.runtime.onInstalled.addListener(({ reason }) => {
  if (reason === "install") chrome.runtime.openOptionsPage();
});
