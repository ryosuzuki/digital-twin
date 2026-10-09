# digital-twin — 実装別カタログ

既存リポジトリは変更・削除せず、確定コミットのソースを追加整理した public ソース分類モノレポです。各実装は独立フォルダです。共通アプリへ統合・API互換化したものではありません。

## どこから見る？

- [scan-realistic-viewer](implementations/scan-realistic-viewer/README.md) — Gaussian の実スキャンをそのまま見る（静的表示）。起動は同フォルダの [RUN.md](implementations/scan-realistic-viewer/RUN.md)。
- [scan-spatial-ui-demo](implementations/scan-spatial-ui-demo/README.md) — 実スキャン内の空間 UI。起動は同フォルダの [RUN.md](implementations/scan-spatial-ui-demo/RUN.md)。
- [scan-interactive-twin](implementations/scan-interactive-twin/README.md) — 部屋内の対話・操作。起動は同フォルダの [RUN.md](implementations/scan-interactive-twin/RUN.md)。
- [scan-interactive-room-ryo](implementations/scan-interactive-room-ryo/README.md) — テクスチャメッシュ内で歩く・小物をつかむ・動作記録。起動は同フォルダの [RUN.md](implementations/scan-interactive-room-ryo/RUN.md)。
- [scan-quality-experiment](implementations/scan-quality-experiment/README.md) — スキャン品質比較の実験。起動は同フォルダの [RUN.md](implementations/scan-quality-experiment/RUN.md)。
- [spatial-object-memory](implementations/spatial-object-memory/README.md) — 固定俯瞰の物体記憶／ボトル移動・合成 fixture で再生可能。起動は同フォルダの [RUN.md](implementations/spatial-object-memory/RUN.md)。
- [spatial-memory-private-backup](implementations/spatial-memory-private-backup/README.md) — 初期手動版・Quest検出・room-first・stream・tracked の履歴。起動は同フォルダの [RUN.md](implementations/spatial-memory-private-backup/RUN.md)。

## 実装の区分と限界

基本は desktop WebGL／Web サーバーでのプロトタイプです。Unity/Quest 実機に移植したという意味ではありません。各 README に元の方式、起動コマンド、検証済み範囲があります。モデル推論・3D生成アルゴリズムは [3d-generation](https://github.com/ryosuzuki/3d-generation)、追跡プラットフォームは [image-tracking](https://github.com/ryosuzuki/image-tracking) に分類。アバターと部屋の一体型デモはソース重複を承知で実用単位を保持しています。

このカタログの検証はソース同一性・JS/Python構文・復元情報です。元のデモ動画は元 README のリンクを利用。新しい実機テストやAI呼び出しはしていません。

## 再現性

`source-index.json` と各 `CATEGORY-SNAPSHOT.json` にコミット、Git blob、ソースSHA-256、公開用ソース検証情報を記録。`python3 scripts/verify-snapshots.py` でコピー同一性を検査。素材はご自身で用意してください（ASSETS.md）。

完了状態: main-integrated を目標。所有者: category consolidation worker。権威あるパス: 本リポジトリの全追加ファイル。元リポジトリの作業ツリーは untouched。

## 録画・オリジナル資産の参照

- [quest-spatial-studio](https://github.com/ryosuzuki/quest-spatial-studio): Quest キャプチャー／カメラ姿勢・深度の取得。これは別の大きな収録プロジェクトで、本カテゴリでは private backup の該当 snapshot を保持。
- [scan-digital-twin-archive](https://github.com/ryosuzuki/scan-digital-twin-archive): 元スキャン・動画・復元 ZIP の private archive。巨大な archive を二重同梱しません。

## 認証

API 機能は `OPENAI_API_KEY`（OpenAI）または `TYPESAFE_API_KEY`（旧 Jev）を環境変数で設定。元の私用認証経路は公開版から外しています。個人スキャンを公開していません。
