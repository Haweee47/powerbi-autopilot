# はじめに

[English](en.md) · [한국어](ko.md) · **日本語** · [简体中文](zh-CN.md)

ダウンロードから Power BI レポートを開くまで約 5 分。そのあと、言葉で頼んで自分のレポートを作る方法を説明します。

## 必要なもの

| | 使う場面 | 入手先 |
|---|---|---|
| Windows 10/11 + Power BI Desktop **2.157 以降** | 常に | Microsoft Store（無料・自動更新）。古いバージョンでは一部の文字が切れます（[#1](https://github.com/Haweee47/powerbi-autopilot/issues/1)） |
| Python 3.10 以上 | 常に | [python.org](https://www.python.org/downloads/)。インストール時に **Add python.exe to PATH** にチェック |
| Claude Code | 言葉で頼んでレポートを作るとき | [claude.com/claude-code](https://claude.com/claude-code) |
| Microsoft の PBIR 検証ツール | 任意 | `npm install -g @microsoft/powerbi-report-authoring-cli` |

ほかにインストールするものはありません。スクリプトは Python の標準ライブラリだけを使います。

## 1. ダウンロード

緑の **Code** ボタン → **Download ZIP** で展開します。または:

```bash
git clone https://github.com/Haweee47/powerbi-autopilot.git
```

## 2. 完成したレポートを開く（AI 不要）

フォルダー内の **`quickstart.cmd`** をダブルクリックします。同梱のサンプルデータでダッシュボードのパイロットを作り、Power BI Desktop で開きます。

初めて開いたとき:

1. 黄色のバーに「一部のテーブルにデータがありません」と出たら → **今すぐ更新**
2. 続けて「適用されていない変更があります」と出たら → **変更の適用**

別のパイロット・テーマ・言語は、フォルダーでターミナルを開いて実行します:

```bash
python tools/quickstart.py --purpose matrix --theme midnight
python tools/quickstart.py --all --lang ja
```

| オプション | 値 |
|---|---|
| `--purpose` | `dashboard`（ダッシュボード）· `table`（指標テーブル）· `matrix`（マトリックス）· `deepdive`（深掘り分析） |
| `--theme` | `navy` · `paper` · `midnight` · `aurora` · `coast` · `ledger` · `contrast` |
| `--lang` | `en` · `ko` · `ja` · `zh-CN` |

**自社のブランドカラー。** 1 色からテーマを作り、その id を `--theme` に指定します。青・ティール・紫系はデータの色にも使われ、
赤・オレンジ・黄・緑系は左のナビゲーションと選択表示だけに使われます。レポートでは赤がすでに「目標未達」を表すためです。

```bash
python tools/brand_theme.py --id acme --accent "#0F62FE" --base navy
python tools/build_themes.py
python tools/quickstart.py --purpose dashboard --theme acme
```

結果は `out/` フォルダーに作られ、git の対象外です。フィルター・視覚化・データの各ウィンドウを折りたたむ（»）と、ページを大きく表示できます。

## 3. 言葉で頼んでレポートを作る（Claude Code）

```bash
cd powerbi-autopilot
claude
```

作りたいものを書きます。例:

> 店舗 KPI のテーブルを Paper テーマ、日本語で作って。

エージェントは足りない情報（用途・テーマ・言語）だけを質問し、いちばん近いパイロットをコピーしてフィールドとタイトルを置き換え、PBIP を生成して検証します。
手順は [`.claude/skills/new-report/SKILL.md`](../../.claude/skills/new-report/SKILL.md) にあります。

## 4. 自分のデータで作る

1. 使っているレポートを Power BI Desktop で開き、**ファイル → 名前を付けて保存 → Power BI プロジェクト (.pbip)** で保存します。
   古いバージョンでは先に **オプション → プレビュー機能 → Power BI プロジェクト (.pbip) 保存オプション** をオンにします。
2. エージェントにモデルの場所を伝えます:
   > C:\Reports\Sales\Sales.SemanticModel\definition のモデルでダッシュボードを作って
3. エージェントはモデルのファイルを丸ごと読まず、1 画面の要約だけを見ます。`new_report.py` がパイロットに必要なのにあなたのモデルにないもの（DAX の中で使う
   メジャーも含む）をすべて見つけて `model-map.json` に書き出し、基準の定義をヒントとして付けます。エージェントはこの対応表に列名と DAX だけを埋めます。[例 05](../../examples/05-own-model/README.md)

データ接続（SQL Server、ファイル、ODBC など）はモデルと一緒にコピーされ、あなたの PC の中だけにあります。
**ODBC。** ODBC のレポートも上と同じく PBIP で保存します。接続文字列と SQL はそのままコピーされ、パスワードはファイルに書かれません。最初の更新でサインイン方法（既定またはカスタム、Windows、データベース）を一度選ぶと、Desktop が記憶します。ローカルの ODBC ドライバーでの確認は [例 06](../../examples/06-odbc/README.md) にあります。実際のデータウェアハウス（Presto、Redshift など）はまだ試していません。

実データはコミットや Issue に載せないでください。`out/` は git の対象外ですが、`examples/` の下に作ったレポートは追跡されます。

## 言語

| 言語 | レポートの文字 | 数値 | サンプルデータの値 |
|---|---|---|---|
| English | 完成 | K · M | 英語 |
| 한국어 | 完成 | 만 · 억 | 韓国語 |
| 日本語 | 現在はほぼ英語 | K · M | 英語 |
| 简体中文 | 現在はほぼ英語 | K · M | 英語 |

日本語版を完成させたい方は [Language support](https://github.com/Haweee47/powerbi-autopilot/issues/new?template=4-language-request.yml) の Issue を開いてください。レビューしてくれるネイティブの方は特に歓迎です。

## トラブルシューティング

| 起きていること | 対処 |
|---|---|
| ビジュアルが空 | 黄色のバーの **今すぐ更新**、または **ホーム → 更新** |
| 「ファイルが見つかりません」などデータフォルダーのエラー | `templates/` ではなく、quickstart が作った `out/` のレポートを開きます（`templates/` のパイロットには仮のパスが入っています）。または **データの変換 → パラメーターの編集 → 데이터폴더** を `examples\_data\korean-retail\en` のフルパスにします |
| `python` が見つからない | **Add python.exe to PATH** にチェックして Python を入れ直すか、`py tools\quickstart.py` で実行 |
| Desktop が `.pbip` を開けない | Power BI Desktop を更新 |
| データペインのテーブル名・列名が韓国語 | サンプルは韓国の小売データです。ページ上の表示は翻訳されています。自分のモデルは元の名前のままです |
| KPI の比較行がない・文字が切れる | Power BI Desktop が 2.157 より古いバージョンです（**ヘルプ → バージョン情報**）。インストーラー版と Store 版が両方あると、ダブルクリックで古い方が開きます。`python tools/quickstart.py --open` で開くか、スタートメニューから Desktop を起動して **ファイル → 開く** を使ってください（[#1](https://github.com/Haweee47/powerbi-autopilot/issues/1)） |
| そのほかの表示の問題 | ウィンドウ全体のスクリーンショット付きで[知らせてください](https://github.com/Haweee47/powerbi-autopilot/issues/new?template=1-render-bug.yml) |

## フィードバック

すべての Issue を読み、記録し、返信します。[フィードバックが変更につながる流れ](../../CONTRIBUTING.md#how-feedback-becomes-changes)

- [表示がおかしい](https://github.com/Haweee47/powerbi-autopilot/issues/new?template=1-render-bug.yml)
- [デザインへの意見](https://github.com/Haweee47/powerbi-autopilot/issues/new?template=2-design-feedback.yml)（1〜5 の評価だけでも大丈夫です）
- [新しいパイロット・機能の要望](https://github.com/Haweee47/powerbi-autopilot/issues/new?template=3-pilot-request.yml)
- [質問・作ったものの共有](https://github.com/Haweee47/powerbi-autopilot/discussions)
