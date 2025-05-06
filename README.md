# NFSW自動モザイクツール

このツールは、YOLOベースのNSFW検出モデル（EraX-NSFW-V1.0）を用いて、画像内のセンシティブな領域を自動で検出し、モザイク・ぼかし・黒塗りなどの効果を一括で適用します。

## 必要なファイル・フォルダ

- mosaic-auto.py … メインの自動モザイクスクリプト
- nfsw-mosaic-auto.bat … Windows用バッチファイル（ダブルクリックで実行）
- erax_nsfw_yolo11m.pt … NSFW検出YOLOモデル（同じフォルダに配置）
- yolov5/ … YOLOv5のコード一式（サブフォルダ）
- requirements.txt … 必要なPythonパッケージ
- README.md … この説明書

## 必要な環境

- Python 3.8 以上
- Windows（バッチファイル利用時）
- pipでrequirements.txtの内容をインストール

## インストール方法

1. 必要なファイル・フォルダを同じディレクトリに配置
2. コマンドプロンプトで以下を実行
   pip install -r requirements.txt

## 使い方

### 1. バッチファイルから実行（推奨）

- nfsw-mosaic-auto.bat をダブルクリック
- モザイクパターン選択ダイアログが表示されるので、希望のパターンを選択
- 画像フォルダ選択ダイアログが表示されるので、処理したい画像フォルダを選択
- フォルダ内の画像が自動で処理され、元フォルダ名＋「_mc」の新フォルダに保存されます

### 2. コマンドラインから実行

python mosaic-auto.py <画像フォルダのパス>

- フォルダパスを省略すると、GUIでフォルダ選択ダイアログが表示されます

## 注意事項

- モデルファイル（erax_nsfw_yolo11m.pt）は同じフォルダに必要です
- yolov5/ フォルダも同じ階層に必要です
- make_love, nippleクラスは自動処理対象から除外されます
- モザイク範囲や強度はapply_pattern関数で調整可能です
