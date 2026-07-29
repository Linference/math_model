# 数学モデリング マルチエージェント論文生成システム

[![Stars](https://img.shields.io/github/stars/Linference/math_model?style=social)](https://github.com/Linference/math_model/stargazers)
[![Version](https://img.shields.io/badge/version-v2.2-6f42c1)](https://github.com/Linference/math_model/blob/main/skill/CHANGELOG.md)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python)
![LaTeX](https://img.shields.io/badge/LaTeX-xelatex-008080?logo=latex)
![Claude Code](https://img.shields.io/badge/Claude_Code-v2.2-D97757)
![CUMCM / MCM / HiMCM](https://img.shields.io/badge/CUMCM_|_MCM_|_HiMCM-e74c3c)

---

[中文](../../README.md) · [English](../en/README.md) · **日本語** ← 現在 · [한국어](../ko/README.md)

---

**v2.2** — マルチエージェント敵対的協調 + 9つの独立QAゲート + アンチパターンハードブロック + ヒューマンインザループチェックポイント + クロスステージ状態管理。21冊のリファレンスマニュアル、6冊のアルゴリズムクックブック、日中英フレーズバンク、アンチパターン知識ベース、環境診断スクリプト。

コンテスト問題のPDFを投入するだけで、問題分析 → 手法選択 → Webデータ収集 → Python求解 → 可視化 → LaTeX論文コンパイル → 3役割並列敵対的レビュー → 最終PDFまでを自動実行。CUMCM（中国）、MCM/ICM（米国）、HiMCMに対応。

---

## クイックスタート

### 前提条件

- **Node.js** ≥ v18 — [nodejs.org](https://nodejs.org/)
- **Claude Code**: `npm install -g @anthropic-ai/claude-code`

### インストール

```bash
git clone https://github.com/Linference/math_model.git ~/.claude/skills/math-modeling
```

または [Releases](https://github.com/Linference/math_model/releases) からZIPをダウンロード。

### 実行

```bash
claude
/math-modeling
[コンテスト問題を貼り付け、またはPDFをドラッグ]
```

---

## 7段階パイプライン

| 段階 | タスク | 成果物 |
|:--:|------|------|
| 0 | プロジェクト足場 | 標準ディレクトリ構造 |
| 1 | 詳細な問題分析 | 構造化分析レポート（2000字以上） |
| 2 | 手法選択 + ML/DL判断 | モデリング計画 + 図表チェックリスト |
| 3 | Webデータ収集 | CSVファイル + SOURCES.md |
| 4 | Python実装 | 実行可能スクリプト + 数値結果 |
| 5 | 可視化（16種類の図表） | 高品質図表（300 DPI） |
| 6 | LaTeX執筆 + コンパイル | 論文草稿 |
| 7 | 3役割敵対的レビュー | 最終PDF（スコア ≥ 7.5/10） |

## 8つのサブエージェント

| エージェント | 役割 |
|------|------|
| `mm-problem-analyst` | 問題分析：設問分解、制約・罠の発見 |
| `mm-modeler` | 手法選択：ML/DL判断、図表計画 |
| `mm-data-hunter` | データ：Wikipedia/GitHub/Kaggle/sklearn検索 |
| `mm-coder` | 実装：Python求解 + 可視化 |
| `mm-writer` | 執筆：LaTeXテンプレート記入、レビュー対応 |
| `mm-reviewer` | レビュー：5次元採点、弱点発見 |
| `mm-verifier` | 検証：数値・単位・境界条件クロスチェック |
| `mm-reasoner` | 推論：数式導出監査、証明ギャップ補完 |

## 敵対的レビュー

3つのレビュアー役割が同じ論文を並列評価 — レビュアー（モデリング品質）、検証者（数値正確性）、推論者（数学的厳密性）。ライターが各指摘に対応し、3者が再採点。平均スコア ≥ 7.5または最大4ラウンドまで繰り返し。

## 品質ゲート（v2.2）

9つの独立Subagent QAゲート + アンチパターンハードブロック + ヒューマンインザループチェックポイントにより、各段階の出力品質を確保。

---

## プロジェクト構成

```
math_model/
├── README.md
├── samples/                      # 完全なサンプルプロジェクト
│   ├── 2024_CUMCM_A/             # CUMCM 問題A
│   └── 2025_HiMCM_Problem_B/     # HiMCM 問題B
└── skill/                        # スキルインストールパッケージ
    ├── SKILL.md                  # メインスキル定義
    ├── references/               # 15冊マニュアル + 6冊クックブック
    ├── scripts/                  # ヘルパースクリプト
    ├── templates/                # LaTeXテンプレート（中/英）
    └── workflows/                # レビューワークフロー
```

---

## サンプルプロジェクト

### 2024 CUMCM A — ベンチドラゴン運動

223節のベンチがアルキメデス螺旋に沿って移動する軌跡をモデル化し、衝突を検出し、方向転換経路を最適化。技術：弦長制約二分探索、SAT衝突検出、制約付き非線形最適化。

### 2025 HiMCM B — スーパーボウル持続可能な開催地選定

NFLのための環境要素のみの開催地選定モデルを構築し、19の歴史的都市 + 3つの候補都市を評価、オリンピックに拡張。技術：AHP + TOPSIS二層意思決定、Scope 1/2/3炭素排出分析、感度分析。

---

## 変更履歴

### v2.2.0 — 深層修正（現在）
- **バグ修正**：スコア集計を単純平均から役割×次元重み付け行列 + ハードキャップ + 外れ値仲裁にアップグレード
- **アンチパターンハードブロック (A1/A2/A3)**：コード/執筆/全次元アンチパターンスキャン、Highヒットは修正必須
- **データ品質ゲート (D1)**：ステージ3で欠損値 + 外れ値 + マルチソース整合性チェックを追加
- **ヒューマンインザループチェックポイント**：ステージ1/4/6後に一時停止し、ユーザー確認
- ゲートを5から9に拡張

### v2.0.0 — アーキテクチャアップグレード
- 独立Subagent QAプロトコル（5ゲート）
- クロスステージ状態管理

---

## ライセンス

MIT
