# Kaggle Template Quickstart

このテンプレートは**ローカル開発とKaggle環境で同じコードが動作**するように設計されています。

## 最小限の使い方

### 1. Leonardo チャレンジの場合

```python
from utils import leonardo_cfg, CompetitionDataLoader, OutputWriter

# Config（ローカル/Kaggle自動対応）
cfg = leonardo_cfg
cfg.create_dirs()

# データ読み込み
loader = CompetitionDataLoader("leonardo-airborne-object-recognition-challenge")
train_df = loader.load_csv("train.csv")

# 結果保存
writer = OutputWriter()
writer.save_csv(results_df, "submission.csv")
```

### 2. 他のコンペティション

```python
from utils import CompetitionConfig, CompetitionDataLoader

cfg = CompetitionConfig(
    comp_name="titanic",
    classes=["Survived", "Not Survived"]
)

loader = CompetitionDataLoader("titanic")
df = loader.load_csv("train.csv")
```

## ローカル開発 → Kaggle移行

1. **ローカルで開発**
   ```bash
   # ローカルで code.ipynb を実行
   jupyter notebook code.ipynb
   ```

2. **Kaggleにアップロード**
   - `code.ipynb` をそのままアップロード
   - `utils/` をカスタムデータセット化（推奨）

3. **Kaggleで実行**
   - コード変更なし！自動的にKaggleパスに切り替わる

## ディレクトリ構成

```
input/
├── kaggle/          ← Kaggleコンペデータ
└── local/           ← ローカル実験用データ

output/              ← 結果出力

utils/               ← ヘルパーモジュール
├── config.py        ← CompetitionConfig, LeonardoConfig
├── data_loader.py   ← CompetitionDataLoader, OutputWriter
├── paths.py         ← 環境自動検出
└── kaggle_api.py    ← Kaggle API ラッパー
```

## 主な API

### CompetitionConfig（汎用）
```python
cfg = CompetitionConfig(comp_name="...", classes=[...])
cfg.train_dir       # 訓練データディレクトリ
cfg.test_dir        # テストデータディレクトリ
cfg.work_dir        # 出力ディレクトリ
```

### LeonardoConfig（Leonardo専用）
```python
cfg = leonardo_cfg
cfg.images_dir      # 画像ディレクトリ
cfg.annotations_dir # アノテーション
cfg.classes         # ['Aircraft', 'Helicopter', ...]
```

### CompetitionDataLoader
```python
loader = CompetitionDataLoader("dataset-name")
df = loader.load_csv("file.csv")
loader.load_parquet("file.parquet")
loader.load_json("file.json")
loader.list_files("*.png")
```

### OutputWriter
```python
writer = OutputWriter()
writer.save_csv(df, "predictions.csv")
writer.save_parquet(df, "results.parquet")
writer.save_json(data, "metadata.json")
```

## Tips

- **ローカルパス** → 自動的に `./input/`, `./output/` を使用
- **Kaggleパス** → 自動的に `/kaggle/input/`, `/kaggle/working/` に切り替わり
- **Torch DataLoader との混同を避ける** → `CompetitionDataLoader` を使用
- **重いロジック** → `utils/` に関数化する

詳細は `README.md` を参照してください。
