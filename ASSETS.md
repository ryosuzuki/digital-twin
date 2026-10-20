# Bring your own assets

公開リポジトリには個人の部屋・録画・人物モデル・スクリーンショット・private logs は含みません。元の絶対パスは `/path/to/local-assets` に置換しています。各 server / viewer の asset URL をご自身のメッシュ、Gaussian、人物モデルまたはキャプチャーへ設定してください。

`implementations/spatial-object-memory` があるカテゴリでは `npm ci && npm run fixture && npm start` で純粋な合成 fixture を生成・実行できます。この合成データは実際の部屋・人物ではありません。他の実装は asset 未提供なので clone だけで元の個人デモが再現するとは主張しません。既存公開動画へのリンクは元 README に残しています。元資産への正確な復元情報は公開Gitには置かず、private の作業記録に保存しています。


## Current Home / Lab twins

`implementations/spatial-home-lab` connects to the recent, separately running private Spatial Home and Lab applications. Its public fixture is synthetic. The real scans, room coordinates, camera identities/endpoints and calibration are not copied here. Keep its runtime config outside the public checkout. The gateway forwards the existing private app rather than rebuilding it from the archived scan snapshots.
