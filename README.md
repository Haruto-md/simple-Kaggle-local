# kaggle local starter

Kaggle Code をローカルで再現して、実験を進めるためのシンプルなリポジトリです。

このリポジトリでは、以下を最小構成で扱います。
- Python 環境の用意
- Kaggle コンペデータのダウンロード
- Jupyter Notebook での学習・推論実験

## 想定ユースケース

- Kaggle Notebook で試したコードをローカルで実行したい
- 依存関係を固定しつつ、手元で繰り返し実験したい
- `kaggle/input/...` の構成をローカルでも揃えたい

## ディレクトリ構成

主要な構成は次のとおりです。

- `code.ipynb`: 実験用ノートブック
- `download_dataset.py`: コンペデータのダウンロード実行スクリプト
- `utils/kaggle_download.py`: Kaggle API 経由のダウンロード処理
- `kaggle/input/competitions/<competition-name>/`: 展開済みデータ配置先

## セットアップ

このリポジトリは `uv` の利用を前提にしています。

- 依存関係をインストール

   uv sync

## Kaggle 認証

データダウンロード前に、いずれかの方法で Kaggle 認証を設定してください。
以下はLegacyを使っています。

- 環境変数を使う

  export KAGGLE_USERNAME=your_username
  export KAGGLE_KEY=your_key

- Kaggleのページからダウンロードした `~/.kaggle/kaggle.json` を使う

加えて、対象コンペページでルール同意を事前に済ませてください。(1敗)

## データダウンロード

現在は `download_dataset.py` で以下のコンペを取得する設定です。
- CMPETITION_NAME = `leonardo-airborne-object-recognition-challenge`

実行方法:

uv run python download_dataset.py

ダウンロードと展開先:

- `kaggle/input/competitions/leonardo-airborne-object-recognition-challenge/`

## 補足

- 依存関係は `pyproject.toml` で管理しています
- Kaggle と同様のパスを意識し、`kaggle/input/...` にデータを配置します
- 学習済み重みなどは必要に応じて `kaggle/notebooks/...` 配下に置いています
