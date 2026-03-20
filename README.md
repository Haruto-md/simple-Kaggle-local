# Introduction - Kaggle Template

ローカル開発とKaggle環境で**コード変更なし**に動作するテンプレートプロジェクト。

## プロジェクト構造

```
.
├── code.ipynb           # メインのノートブック（ローカル開発 → Kaggleにそのままアップロード）
├── main.py              # スクリプト実行用（オプション）
├── utils/               # ヘルパーモジュール（Kaggleではカスタムデータセットとしてマウント）
│   ├── __init__.py
│   ├── paths.py         # 環境検出・パス管理（ローカル vs Kaggle自動判定）
│   ├── data_loader.py   # DataLoader・OutputWriter（統一インターフェース）
│   └── kaggle_api.py    # Kaggle APIラッパー
├── input/
│   ├── kaggle/          # Kaggleコンペ・データセット（APIでダウンロード）
│   └── local/           # ローカル実験用データ
├── output/              # 実行結果出力
├── pyproject.toml
└── README.md
```

## セットアップ

### 1. 依存パッケージのインストール

```bash
uv sync
```

または pip の場合：

```bash
pip install -e .
```

### 2. Kaggle API認証（オプション - ローカルでダウンロードする場合）

Kaggleからデータセットをダウンロードする場合、認証方法は2通りあります：

**方法1: `.env` ファイル（推奨・現在の設定）**

```bash
# .env ファイルに以下を追加
KAGGLE_API_TOKEN=your_token_here
```

このプロジェクトは既に `.env` から読み込む設定になっています。

**方法2: `~/.kaggle/kaggle.json`（Kaggle推奨方式）**

```bash
# 1. Kaggleアカウント > Settings > API から kaggle.json をダウンロード
# 2. ~/.kaggle/kaggle.json に配置
mkdir -p ~/.kaggle
mv ~/Downloads/kaggle.json ~/.kaggle/

# 3. パーミッション設定
chmod 600 ~/.kaggle/kaggle.json
```

**認証なしの場合**：
- データは手動で `input/kaggle/` に配置可能
- `CompetitionDataLoader` で読み込める
- `download_*` 関数は明確なエラーメッセージで案内

## 使用方法

### ローカル環境での開発

#### パターン1: Kaggleデータセットをダウンロードして実験

```python
from utils import download_dataset_by_id, CompetitionDataLoader

# Kaggleからデータをダウンロード（初回のみ）
download_dataset_by_id("owner/dataset-name", target_dir="my_dataset")

# データを読み込む
loader = CompetitionDataLoader("my_dataset", source="kaggle")
df = loader.load_csv("train.csv")
```

#### パターン2: ローカルデータで実験

```python
from utils import CompetitionDataLoader

# ローカルの input/local/my_data/ にあるデータを読み込む
loader = CompetitionDataLoader("my_data", source="local")
df = loader.load_csv("data.csv")
```

#### パターン3: 結果の保存

```python
from utils import OutputWriter

writer = OutputWriter()
writer.save_csv(df, "predictions.csv")
writer.save_parquet(df, "model_results.parquet")
writer.save_json({"metrics": {...}}, "metrics.json")
```

#### パターン4: Kaggleコンペティション用設定

```python
from utils import leonardo_cfg, CompetitionConfig, LeonardoConfig

# Leonardo チャレンジを使う場合
cfg = leonardo_cfg
cfg.create_dirs()  # ローカルではディレクトリを作成

print(f"Train directory: {cfg.train_dir}")
print(f"Test directory: {cfg.test_dir}")
print(f"Classes: {cfg.classes}")

# データ読み込み
loader = CompetitionDataLoader("leonardo-airborne-object-recognition-challenge")
df = loader.load_csv("train.csv")
```

#### パターン5: カスタムコンペティション設定

```python
from utils import CompetitionConfig

# Titanic や他のコンペティションの設定
cfg = CompetitionConfig(
    comp_name="titanic",
    classes=["Survived", "Not Survived"]
)
```

### Kaggle環境での実行

ノートブック `code.ipynb` をそのまま Kaggle にアップロードします。

**ローカルと同じコードが動作します！**

環境に応じて自動的にパスが切り替わります：
- **ローカル** → `./input/kaggle/`, `./output/`
- **Kaggle** → `/kaggle/input/`, `/kaggle/working/`

#### Kaggleでのセットアップ

1. ノートブック上の最初のセルで：

```python
from utils import CompetitionDataLoader, OutputWriter, LeonardoConfig, leonardo_cfg

# CompetitionDataLoaderは自動的に Kaggle のデータセットをマウント済みパスから読み込みます
cfg = leonardo_cfg
loader = CompetitionDataLoader("leonardo-airborne-object-recognition-challenge")
df = loader.load_csv("train.csv")
```

2. `utils/` をカスタムデータセットとして登録（オプション）
   - Kaggleで `+ New Dataset > Edit your datasets`
   - `utils/` フォルダをアップロード
   - ノートブックで Kaggle データセットとしてマウント

## 環境自動検出の仕組み

```python
# utils/paths.py
import os

IS_KAGGLE = "KAGGLE_KERNEL_INTEGRATIONS_METADATA" in os.environ

if IS_KAGGLE:
    INPUT_DIR = Path("/kaggle/input")
    OUTPUT_DIR = Path("/kaggle/working")
else:
    INPUT_DIR = Path("./input")
    OUTPUT_DIR = Path("./output")
```

この仕組みにより、ノートブックコードの変更は不要です。

## Kaggleへのアップロード

### パターンA: ノートブックのみ

`code.ipynb` だけをKaggleにアップロード

### パターンB: カスタムデータセット + ノートブック（推奨）

1. `utils/` をカスタムデータセットとして登録
2. `code.ipynb` をノートブックとしてアップロード
3. ノートブック設定でカスタムデータセットをマウント

こうすれば、ローカルで開発したコードがそのまま Kaggle で動作します。

## 例：Kaggleコンペティション対応

```python
# code.ipynb の最初のセル
from utils import (
    CompetitionDataLoader,
    OutputWriter,
    download_dataset_by_id,
    LeonardoConfig,
    leonardo_cfg
)

# ローカル環境での初期セットアップ（Kaggleでは自動マウント済み）
# download_dataset_by_id("leonardo-airborne-object-recognition-challenge")

# どちらの環境でも同じコードで動作
cfg = leonardo_cfg
cfg.create_dirs()  # ローカル時はディレクトリ作成

loader = CompetitionDataLoader("leonardo-airborne-object-recognition-challenge")
train_df = loader.load_csv("train.csv")

# ... 学習・予測処理 ...

# 結果を保存
writer = OutputWriter()
writer.save_csv(submission_df, "submission.csv")
```

## ベストプラクティス

- **重いロジック（前処理、モデリング）** → `utils/` に関数化
- **実験・可視化** → `code.ipynb` に記述
- **カスタムデータセット** → `input/local/` で実験後、`input/kaggle/` で本番化
- **パス参照** → `CompetitionConfig` や `leonardo_cfg` で自動対応
- **Torch DataLoader との混同を避ける** → `CompetitionDataLoader` を使用

## トラブルシューティング

### Kaggleでインポートエラーが出る

`utils/` をカスタムデータセットとして登録し、ノートブック設定で有効にしたか確認してください。

### ローカルでデータが見つからない

```bash
# ファイルが正しく配置されているか確認
ls -la input/kaggle/
ls -la input/local/
```

### Kaggle API 認証エラー

```bash
# kaggle.json の確認
cat ~/.kaggle/kaggle.json
chmod 600 ~/.kaggle/kaggle.json
```

## ライセンス

このテンプレートは自由に使用・改変できます。

## セットアップスクリプト

`main.py` を実行してLeonardoチャレンジの環境を自動セットアップできます：

```bash
# ディレクトリ作成＆データダウンロード（Kaggle認証が必要）
python main.py

# セットアップ検証
python main.py --verify
```

### セットアップの流れ

1. **自動セットアップ**（Kaggle認証あり）
   ```bash
   python main.py
   # → ディレクトリ作成
   # → データ自動ダウンロード
   # → セットアップ検証
   ```

2. **手動セットアップ**（Kaggle認証なし）
   ```bash
   python main.py
   # → 手動セットアップ手順を表示
   # → Kaggleから手動ダウンロード
   # → 指示に従い配置
   ```

3. **検証のみ**
   ```bash
   python main.py --verify
   ```

## ノートブック内でのダウンロード

`code.ipynb` の Data Loading セクションでも、コメントを外すだけでダウンロード可能：

```python
from utils import download_competition_data, is_kaggle_authenticated

if is_kaggle_authenticated():
    download_competition_data("leonardo-airborne-object-recognition-challenge")
else:
    print("Kaggle API not available - manual setup required")
```

## トラブルシューティング

### Kaggle API で 403 Forbidden エラーが出る

これはコンペティションルールに同意していないか、トークンが無効である可能性があります。以下を確認してください：

1. **Kaggleでルール同意を確認**
   - https://www.kaggle.com/competitions/leonardo-airborne-object-recognition-challenge
   - "I understand and accept" をチェック

2. **トークンを再取得**
   - https://www.kaggle.com/settings/account
   - "Create New Token" をクリック
   - `.env` の `KAGGLE_API_TOKEN` を更新

3. **手動ダウンロード**
   ```bash
   # Kaggleから手動でダウンロード
   # 以下に配置:
   input/kaggle/leonardo-airborne-object-recognition-challenge/
   ```

