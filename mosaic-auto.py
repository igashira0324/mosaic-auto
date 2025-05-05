import os
import sys
import cv2
import numpy as np
import tkinter as tk
import tkinter.filedialog as tkFileDialog
from PIL import Image
from PIL import ImageFilter
from ultralytics import YOLO
# EraX-NSFW-V1.0のクラス名（https://huggingface.co/erax-ai/EraX-NSFW-V1.0?not-for-all-audiences=true）
names = ['anus', 'make_love', 'nipple', 'penis', 'vagina']
# モデルの初期化（https://huggingface.co/erax-ai/EraX-NSFW-V1.0/blob/main/erax_nsfw_yolo11m.pt）
yolo_model_path = os.path.join(os.path.dirname(__file__), 'erax_nsfw_yolo11m.pt')
model = YOLO(yolo_model_path)

def ask_mosaic_pattern():
    import tkinter as tk
    patterns = ["モザイク小", "モザイク中", "モザイク大", "ぼかし", "黒塗り"]
    selected = [patterns[0]]
    def on_select(event=None):
        idx = listbox.curselection()
        if idx:
            selected[0] = patterns[idx[0]]
            root.quit()
    root = tk.Tk()
    root.title("モザイクパターン選択")
    root.geometry("400x300")  # ウィンドウサイズを大きく
    tk.Label(root, text="モザイクパターンを選択してください", font=("Meiryo", 16)).pack(padx=10, pady=20)
    listbox = tk.Listbox(root, height=len(patterns), font=("Meiryo", 16))
    for p in patterns:
        listbox.insert(tk.END, p)
    listbox.selection_set(0)
    listbox.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)
    listbox.bind('<Double-1>', on_select)
    btn = tk.Button(root, text="OK", font=("Meiryo", 14), width=10, height=2, command=on_select)
    btn.pack(pady=10)
    root.mainloop()
    root.destroy()
    return selected[0]

def apply_pattern(region, pattern):
    w, h = region.size
    if pattern == "モザイク大":
        small = region.resize((max(1, w // 32), max(1, h // 32)), Image.Resampling.BICUBIC)
        return small.resize((w, h), Image.Resampling.NEAREST)
    elif pattern == "モザイク中":
        small = region.resize((max(1, w // 16), max(1, h // 16)), Image.Resampling.BICUBIC)
        return small.resize((w, h), Image.Resampling.NEAREST)
    elif pattern == "モザイク小":
        small = region.resize((max(1, w // 8), max(1, h // 8)), Image.Resampling.BICUBIC)
        return small.resize((w, h), Image.Resampling.NEAREST)
    elif pattern == "ぼかし":
        return region.filter(ImageFilter.GaussianBlur(radius=8))
    elif pattern == "黒塗り":
        return Image.new("RGB", (w, h), (0, 0, 0))
    else:
        return region

def auto_apply_mosaic(image, pattern):
    import tempfile
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
        image.save(tmp.name)
        tmp_path = tmp.name
    # オブジェクト検出モデルを実行し、結果を取得
    # conf: 信頼度閾値, iou: IoU閾値
    results = model(tmp_path, conf=0.15, iou=0.3)
    # 処理対象の画像サイズを出力
    print(f"画像サイズ: {image.width}x{image.height}")
    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
            conf = float(box.conf[0])
            cls_idx = int(box.cls[0])
            cls_name = names[cls_idx] if cls_idx < len(names) else ""
            cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
            print(f"検出: class={cls_name}, conf={conf:.2f}, box=(x1={x1}, y1={y1}, x2={x2}, y2={y2}), center=({cx}, {cy})")
            if cls_name in ["make_love", "nipple"]:
                continue
            w, h = x2 - x1, y2 - y1
            if w < 10 or h < 10:
                continue
            # --- モザイクの範囲を一回り小さく ---
            shrink_ratio_w = 0.75  # ヨコの範囲を75%ずつ内側に
            shrink_ratio_h = 0.45  # タテの範囲を45%ずつ内側に
            dx = int(w * shrink_ratio_w / 2)
            dy = int(h * shrink_ratio_h / 2)
            sx1 = x1 + dx
            sy1 = y1 + dy
            sx2 = x2 - dx
            sy2 = y2 - dy
            if sx2 <= sx1 or sy2 <= sy1:
                continue
            region = image.crop((sx1, sy1, sx2, sy2))
            mosaic = apply_pattern(region, pattern)
            image.paste(mosaic, (sx1, sy1, sx2, sy2))
    os.remove(tmp_path)
    return image

def main():
    # 引数がなければGUIでフォルダ選択
    if len(sys.argv) == 1:
        root = tk.Tk()
        root.withdraw()
        folder = tkFileDialog.askdirectory(title="画像フォルダを選択してください")
        root.destroy()
        if not folder:
            print("フォルダが選択されませんでした。処理を中止します。")
            sys.exit(1)
    elif len(sys.argv) == 2:
        folder = sys.argv[1]
    else:
        print("使い方: python mosaic-auto.py <画像フォルダ>")
        sys.exit(1)
    if not os.path.isdir(folder):
        print("指定されたパスはフォルダではありません")
        sys.exit(1)
    out_folder = folder + "_mc"
    exts = (".jpg", ".jpeg", ".png", ".gif")
    files = [f for f in sorted(os.listdir(folder)) if f.lower().endswith(exts)]
    if not files:
        print("画像ファイルが見つかりません")
        sys.exit(1)
    pattern = ask_mosaic_pattern()
    out_folder_created = False
    for fname in files:
        in_path = os.path.join(folder, fname)
        out_path = os.path.join(out_folder, fname)
        print(f"処理中: {in_path}")
        try:
            img = Image.open(in_path).convert("RGB")
            img = auto_apply_mosaic(img, pattern)
            if not out_folder_created:
                os.makedirs(out_folder, exist_ok=True)
                out_folder_created = True
            img.save(out_path)
            print(f"保存: {out_path}")
        except Exception as e:
            print(f"エラー: {fname}: {e}")
    print("全ての画像の処理が完了しました。")

if __name__ == "__main__":
    main()
