# Quest本体でYOLO — WebXR / Unity授業用サンプル

外部GPU・推論サーバーなしで、同じYOLOv9モデルを動かす2つの実装です。
**Quest 3 / 3S向け**。Quest 2 / ProのカメラAPI対応を意味しません。

- **Web**: ONNX Runtime WebのWASM CPU推論。読み取れるカメラ／ローカル画像・動画に検出枠を表示し、WebXRではそのプレビューをヘッドセット内パネルに表示します。
- **Unity native**: MetaのPassthrough Camera APIから実カメラを取得し、Unity Inference Engineで本体GPU（GPUCompute）／CPU推論。**一人称パススルー**に、カメラ校正＋環境深度で投影した検出枠・ラベルだけを重ねます。カメラプレビューパネルは表示しません。
- YOLO自体の出力は物体の種類と2D矩形です。Unity版は矩形の中心を実環境の深度へレイキャストし、その深さの平面へ四隅を投影します。正確な3D物体形状・永続アンカー・Digital Twinの完成を主張しません。

## 図で学ぶ / Illustrated walkthrough

[授業用チュートリアル](TUTORIAL.md) · [ブラウザ版HTML](tutorial/index.html) · [全体構成図](tutorial/pipeline.svg) · [中心raycast図](tutorial/center-raycast.svg)

「検出した物体の中心を深度へraycastする」実装を、ソース抜粋・位置合わせの近似・検出と追跡の違い・再現手順と一緒に説明しています。

## まずどちらを使う？

授業でQuestの実カメラを確実に扱う入口は**Unity native**です。WebXRパススルー背景は、JavaScriptがその画素を読めることを意味しません。Web版は`getUserMedia`の実際の許可結果を確認し、失敗は画面に表示します。未対応端末でダミーの検出を表示したり、テスト画像をライブ映像と呼んだりしません。WebXRセッション中のカメラ継続可否もブラウザ依存です。

## Web版

```bash
cd implementations/quest-ondevice-yolo/web
npm ci
npm run prepare-assets
npm test
npm run dev
```

PCでは表示されたlocalhost URLを開き、①Load model → ②Start camera。別のカメラへ変更する場合はプルダウン選択後にStart cameraを押します。カメラがない場合はローカル画像／動画でも実モデル推論を試せます。

Questに配るときは`npm run build`で作成した`dist/`を**信頼されたHTTPS**の静的ホストへ置きます。HTTPのLANアドレスではcamera / WebXRは使えません。ローカル開発サーバーは推論サーバーではなく、モデルとJSを配るだけです。初回セットアップはモデルのダウンロードにネット接続が必要です。ページを閉じた後のオフライン再起動保証やPWAキャッシュは未実装です。

1. Quest BrowserでHTTPS URLを開く。
2. Load model。WASM CPUという実行方式を確認。
3. Start cameraで許可し、選択されたカメラと画像を自分で確認。
4. 入力が読めた場合にEnter WebXR。検出映像はパネル表示です。現実物体に貼りつくラベルではありません。
5. Stopでカメラを停止。Save metricsで推論時間を保存。
6. Record previewで最大60秒のプレビュー動画を保存。これはOSコンポジタ録画ではありません。

ブラウザカメラが使えなければ、Unity版へ進んでください。Raw Camera Access仕様の対応を勝手に仮定しません。

### Web検証の再実行

```bash
npm exec playwright install chromium
# 自分で用意した検証画像・保存先を指定
YOLO_TEST_IMAGE=/absolute/test.jpg YOLO_EVIDENCE=/absolute/output node verify-demo.mjs
```

テストスクリプトの期待値は、[Ultralytics公開bus.jpg](https://github.com/ultralytics/assets/blob/main/im/bus.jpg)に対するpersonとbusです。画像そのものはこのリポジトリには再配布しません。`CHROME_PATH`で専用テスト実行のChromeバイナリを指定できます。既存ユーザープロファイルには接続しません。

## Unity native版

SDK・シーン・モデルのコピーをこのリポジトリへ重複保存せず、Meta公式プロジェクトの**正確なコミット**から授業用シーンを生成します。

```bash
python3 implementations/quest-ondevice-yolo/scripts/prepare-unity.py /absolute/new/quest-yolo-unity
```

既存フォルダの上書きは拒否します。Git LFSとUnity HubのAndroid Build Support（SDK/NDK/OpenJDK）が必要です。

1. 出力されたプロジェクトを**Unity 6000.4.5f1**で開く（今回ビルドしたバージョン）。公式ソースのProjectVersionは6000.0.66f2ですが、授業版は確認済みの6000.4.5f1へ明示的に設定します。
2. `Classroom > Prepare YOLO scene`を実行。
3. 必要に応じMeta > Tools > Project Setup Toolの指摘を確認。実機のカメラ権限が必要です。
4. `Classroom > Build Android APK`で`Builds/classroom-yolo.apk`を生成。
5. 本サンプル専用の`org.openclaw.classroom.yolo`にインストール。現在の実機確認版は**0.2.0/code3（一人称版）**です。既存アプリは変更しません。
6. Questのライブラリ → 提供元不明（Unknown Sources） → **Classroom Local YOLO**を開きます。
7. カメラ・空間データ許可後、通常のパススルー視界に検出枠。Aボタンで一時停止／再開。

```bash
# 例: インストール済みUnityの実パスを使用
/path/to/Unity -batchmode -nographics -quit -projectPath /absolute/new/quest-yolo-unity \
  -buildTarget Android -executeMethod ClassroomBuild.Build -logFile /absolute/build.log
```

既定は**内蔵GPU**。CPU版は`YOLO_CPU=1`をビルド環境へ指定するか、生成シーンのQuestYoloコンポーネントでbackendをCPUに変更します。メニューのBuildはPrepareも実行するので、Inspectorで変更した場合は通常のBuild Settingsで生成シーンをビルドしてください。

- 推論要求は既定最大5Hz、同時に1件だけ。推論FPSとXR描画FPSは別です。
- `QUEST_YOLO backend=... inference_ms=... count=... source=headset_camera`をログ出力。
- Permission / focus / camera / positional tracking待機中は検出枠を消します。深度が取得できない検出は描画せず、0.85秒以上更新されない枠も消します。
- GPUの性能・熱・メモリ状況で速度は変わります。Quest上の速度実測は[検証状態](VERIFICATION.md)に別記します。
- シーンはカメラビューアーを基にしますが、そのCanvasを無効にしてプレビューを廃止し、環境レイキャストPrefabを追加します。露光時のカメラ姿勢と校正済みViewportPointToRayを使用。矩形は中心深度のカメラ平行平面に描かれるため、物体の正確な3D境界ではありません。Scene Meshや永続アンカーの保存は必須ではありません。推論遅延・中心が背景へ外れる場合・深度誤差によるずれは残ります。

## 授業での短い実験

1. 人・椅子・ボトルなどモデルが知る80クラスを見せる。
2. 閾値0.35→0.6で誤検出と見落としの変化を見る。
3. 推論1Hz / 5Hzで応答・描画の違いを見る。
4. 同じカメラ入力でCPU / 内蔵GPUのログを比較する。
5. 2D認識単独と、環境深度を加えた近似位置の違いを見る。

## 出典・ライセンス

- [Meta公式プロジェクト固定版](https://github.com/oculus-samples/Unity-PassthroughCameraApiSamples/tree/3baac1a1a53aa00af3f639425914f14238a97f84)
- [Meta PCA概要](https://developers.meta.com/horizon/documentation/unity/unity-pca-overview)
- [Unity推論統合](https://developers.meta.com/horizon/documentation/unity/unity-pca-sentis)
- [WebXR Raw Camera Access仕様](https://immersive-web.github.io/raw-camera-access/) — 仕様の存在とQuest Browserでの利用可能性は別です。
- Meta公式記載: Quest 3/3S、OS v74以上、`horizonos.permission.HEADSET_CAMERA`、MRUK v81以上。
- 固定ソースのmanifest: MRUK85.0.0、Inference Engine2.2.1。授業版の生成スクリプトは、確認済みのInference Engine2.6.1・OpenXR1.16.1へ明示的に設定します。
- モデルSHA256: `189ed26d273423b02243ce7f0a7795acc7da8049f879f8b73a0684d25d1138fd`。
- SDK・公式シーンの元ライセンスを保持します。モデルはMetaのREADMEでMITとして案内されています。別のYOLOモデルへ差し替える際はそのモデルのライセンスを別途確認してください。
- カメラ画像・部屋の録画・APK・SDK本体・重みはGitに入れません。ソースとモデル取得手順のみ公開します。
