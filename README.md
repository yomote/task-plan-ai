# Task Plan AI

Task Plan AI は、OpenAI モデルを活用してプロジェクト計画を生成し、反復的にブラッシュアップできるコマンドラインツールです。スケジュールを [Markwhen](https://markwhen.com/) 形式で作成し、すべてのタスクを記述した JSON ファイルを生成します。計画は、指定した採用スコアに達するまで自動でレビュー・改善されます。

## 特徴

* Markwhen 形式のタイムライン (`plan.mw`) を生成
* タスクのメタデータを `meta.json` に出力
* 計画を反復的にレビューして改善を適用
* 採用スコアと反復回数を設定可能

## インストール

本プロジェクトは依存関係管理に [Poetry](https://python-poetry.org/) を使用しています。Python 3.9 をインストールし、以下を実行してください。

```bash
poetry install
```

## 使い方

まず、プロジェクトを記述した YAML 形式の入力ファイルを用意します。サンプルとして `sample_input.yaml` が付属しています。

プランを生成するには次を実行します。

```bash
poetry run python cli/generate_plan.py --input sample_input.yaml
```

`--adoption-score` でプランを受け入れるための最小スコア（0–100）を指定できます。スクリプトは `plan.mw` と `meta.json` をカレントディレクトリに書き出します。

## プロジェクト構成

* `ai/` – プランニングエージェント、レビュアー、データモデル
* `cli/generate_plan.py` – コマンドラインインターフェース

## ライセンス

本プロジェクトは MIT ライセンスのもとで公開されています。
