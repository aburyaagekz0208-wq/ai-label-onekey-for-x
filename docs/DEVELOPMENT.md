# 開発メモ

## ファイル

| ファイル | 役目 |
|---|---|
| `manifest.json` | 拡張の設定（名前・バージョン・権限） |
| `hotkey.js` | キーの組み合わせの扱い（表示・判定・使えるかの確認）。content.js と設定画面で共用 |
| `content.js` | X の画面の中でキーを受け、旗マークとスイッチを探して押す |
| `background.js` | 拡張アイコンを押したときに X のタブへ伝える／はじめて入れたとき設定画面を開く |
| `options.html` / `options.css` / `options.js` | 設定画面 |
| `icons/` | アイコン |
| `docs/images/` | 説明書のイラスト（PNG）。元の SVG は `docs/images/src/` |
| `scripts/build.py` | 配布用の zip を作る |
| `scripts/make_icons.py` | アイコンを作り直す（Pillow が必要） |
| `scripts/make_illustrations.py` | 説明書のイラストを作り直す（Chrome が必要） |

## 開発中の読み込み

`chrome://extensions` → デベロッパーモード → 「パッケージ化されていない拡張機能を読み込む」でこのフォルダを選ぶ。
中身を直したら、更新ボタン（ぐるっと矢印）→ X のタブを再読み込み。

## X の部品の見つけ方

画面の位置ではなく、次の目印で探している。X が画面を変えたら、ここを直す。

| 部品 | 目印 |
|---|---|
| 入力欄 | `[data-testid^="tweetTextarea_"][contenteditable="true"]` |
| 旗マーク（コンテンツ開示） | `[data-testid="contentDisclosureButton"]` |
| 「AIで生成」スイッチ | ダイアログの中の `label` のうち、文字が `AI_LABEL_TEXTS` に当たるものの `input[role="switch"]`。見つからなければ、`/content_disclosure` のダイアログにスイッチがちょうど 2 つあるとき後ろのほう |
| 完了ボタン | 文字が `完了` / `Done` の `button` |

返信欄は、入力欄にフォーカスするまで旗マークが出てこない。

## リリースの手順

1. `manifest.json` の `version` を上げる（例 1.0.0 → 1.0.1）
2. `python scripts/build.py` → `dist/ai-label-onekey-<version>.zip` ができる
3. コミットして push し、タグ `v<version>` を付ける
4. GitHub の Releases で新しいリリースを作り、zip を添付する

## 履歴

- v1.0.0（2026-10-31）：キーを設定画面で変えられるようにした。名前を「AIラベル ワンキー for X」にし、アイコン・説明書・配布用 zip を用意。英語表示の X にも対応
- v0.2.0：キーをページの中で直接受ける形に変えた（v0.1 は裏の部分がタブの URL を読めず、何もしなかった）
- v0.1.0：最初の版（仮の名前「X Helper」）
