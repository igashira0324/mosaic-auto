# NFSW自動モザイクツール

このツールは、YOLOベースのNSFW検出モデル（EraX-NSFW-V1.0）を用いて、画像内のセンシティブな領域を自動で検出し、モザイク・ぼかし・黒塗りなどの効果を一括で適用します。

## 必要なファイル・フォルダ

- mosaic-image.py … 画像用の自動モザイクスクリプト
- mosaic-video.py … 動画用の自動モザイクスクリプト（mp4/avi/mov対応）
- nsfw-mosaic-image.bat … 画像用バッチファイル（ダブルクリックで実行）
- nsfw-mosaic-video.bat … 動画用バッチファイル（ダブルクリックで実行）
- erax_nsfw_yolo11m.pt … NSFW検出YOLOモデル（[EraX-NSFW-V1.0（HuggingFace）](https://huggingface.co/erax-ai/EraX-NSFW-V1.0) からダウンロード）
- yolov5/ … YOLOv5のコード一式（[Ultralytics YOLOv5公式](https://github.com/ultralytics/yolov5)）
- requirements.txt … 必要なPythonパッケージ
- README.md … この説明書

## インストール方法

1. コード一式をクローンします。
   ```sh
   git clone https://github.com/igashira0324/mosaic-auto.git
   cd mosaic-auto
   ```
2. モデルファイルをダウンロードします。
   - [erax_nsfw_yolo11m.pt (HuggingFace)](https://huggingface.co/erax-ai/EraX-NSFW-V1.0) よりダウンロードし、クローンしたディレクトリ直下に配置してください。
   - yolov5/ ディレクトリはリポジトリに含まれています。
3. 依存パッケージをインストールします。
   ```sh
   pip install -r requirements.txt
   ```
   ※ PyTorchのインストールでエラーが出る場合は[PyTorch公式サイト](https://pytorch.org/get-started/locally/)も参照してください。

## 使い方

### 画像の自動モザイク処理

1. `nsfw-mosaic-image.bat` をダブルクリックして実行します。
2. モザイクパターン選択ダイアログが表示されるので、希望のパターン（モザイク・ぼかし・黒塗り等）を選択します。
3. 画像フォルダ選択ダイアログが表示されるので、処理したい画像フォルダを選択します。
4. フォルダ内の画像が自動で処理され、元フォルダ名＋「_mc」の新フォルダに保存されます。
   - 例: `sample` フォルダを選択 → `sample_mc` フォルダに出力

### 動画の自動モザイク処理

1. `nsfw-mosaic-video.bat` をダブルクリックして実行します。
2. 「動画ファイルを選択」または「フォルダ内の全動画を一括処理」を選択します。
3. モザイクパターン選択ダイアログが表示されるので、希望のパターンを選択します。
4. 選択した動画またはフォルダ内の全動画（mp4/avi/mov）が自動で処理され、元ファイル名＋「_mc」の新ファイルとして保存されます。
   - 例: `sample.mp4` → `sample_mc.mp4` に出力
   - フォルダ一括処理時は、すべての動画の処理が完了した後に1回だけまとめて完了通知が表示されます。
   - すでに「_mc.mp4」「_mc.avi」「_mc.mov」で終わるファイルは自動的に処理対象外となります。

## 対応形式

- 画像: jpg, jpeg, png, gif
- 動画: mp4, avi, mov

## 注意事項（抜粋）

- モデルファイル（`erax_nsfw_yolo11m.pt`）と `yolov5/` フォルダは同じディレクトリに必要です。
- make_love, nippleクラスは自動処理対象から除外されます。
- モザイク範囲や強度は `apply_pattern` 関数で調整可能です。
- 詳細は各スクリプトのコメントやREADME全体を参照してください。

## ライセンス

本ツールはオープンソースです。
- メインスクリプト・バッチファイル等はAGPL-3.0ライセンスに従います。
- yolov5/配下のコードは[Ultralytics YOLOv5公式](https://github.com/ultralytics/yolov5)のAGPL-3.0ライセンスです。詳細は[yolov5/LICENSE](yolov5/LICENSE)をご参照ください。
- erax_nsfw_yolo11m.pt（NSFW検出モデル）は[EraX-NSFW-V1.0（HuggingFace）](https://huggingface.co/erax-ai/EraX-NSFW-V1.0)の利用条件に従ってください。

## 参考リンク

- EraX-NSFW-V1.0モデル: https://huggingface.co/erax-ai/EraX-NSFW-V1.0
- YOLOv5公式: https://github.com/ultralytics/yolov5
- Ultralytics YOLOドキュメント: https://docs.ultralytics.com/
- PyTorch公式: https://pytorch.org/get-started/locally/
