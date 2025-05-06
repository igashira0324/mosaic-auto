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
    from tkinter import ttk
    patterns = ["モザイク小", "モザイク中", "モザイク大", "ぼかし", "黒塗り"]
    selected = [patterns[0]]
    cancelled = [False]
    def on_select(event=None):
        idx = listbox.curselection()
        if idx:
            selected[0] = patterns[idx[0]]
            root.quit()
    def on_ok():
        idx = listbox.curselection()
        if idx:
            selected[0] = patterns[idx[0]]
        root.quit()
    def on_cancel():
        cancelled[0] = True
        root.quit()
    def on_enter(e):
        e.widget.config(bg="#00bfff", fg="#fff", relief="raised", bd=3)
    def on_leave(e):
        e.widget.config(bg="#23272e", fg="#fff", relief="raised", bd=3)
    root = tk.Tk()
    root.title("モザイクパターン選択")
    root.geometry("420x360")
    root.configure(bg="#23272e")
    # タイトル
    title = tk.Label(root, text="モザイクパターンを選択してください", font=("Segoe UI", 17, "bold"), bg="#23272e", fg="#fff")
    title.pack(padx=10, pady=18)
    # リストボックス
    listbox_frame = tk.Frame(root, bg="#23272e")
    listbox_frame.pack(padx=24, pady=8, fill=tk.BOTH, expand=True)
    listbox = tk.Listbox(listbox_frame, height=len(patterns), font=("Segoe UI", 15), bg="#181a20", fg="#fff", selectbackground="#00bfff", selectforeground="#fff", relief="flat", highlightthickness=0, bd=0)
    for p in patterns:
        listbox.insert(tk.END, p)
    listbox.selection_set(0)
    listbox.pack(fill=tk.BOTH, expand=True)
    listbox.bind('<Double-1>', on_select)
    # ボタン
    btn_frame = tk.Frame(root, bg="#23272e")
    btn_frame.pack(pady=18)
    btn_ok = tk.Button(btn_frame, text="OK", font=("Segoe UI", 14), width=10, height=2, bg="#23272e", fg="#fff", relief="raised", bd=3, activebackground="#00bfff", activeforeground="#fff", command=on_ok)
    btn_ok.pack(side=tk.LEFT, padx=16)
    btn_ok.bind("<Enter>", on_enter)
    btn_ok.bind("<Leave>", on_leave)
    btn_cancel = tk.Button(btn_frame, text="キャンセル", font=("Segoe UI", 14), width=10, height=2, bg="#23272e", fg="#fff", relief="raised", bd=3, activebackground="#ff5555", activeforeground="#fff", command=on_cancel)
    btn_cancel.pack(side=tk.LEFT, padx=16)
    btn_cancel.bind("<Enter>", on_enter)
    btn_cancel.bind("<Leave>", on_leave)
    root.mainloop()
    root.destroy()
    if cancelled[0]:
        return None
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
    import tkinter.messagebox as tkMessageBox
    from tkinter import ttk
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
    if pattern is None:
        print("キャンセルされました。処理を中止します。")
        return
    out_folder_created = False

    # --- 進捗バー用ウィンドウ ---
    progress_root = tk.Tk()
    progress_root.title("モザイク処理進捗")
    progress_root.geometry("440x190")
    progress_root.configure(bg="#23272e")
    style = ttk.Style(progress_root)
    style.theme_use("clam")
    style.configure("TLabel", background="#23272e", foreground="#fff", font=("Segoe UI", 14))
    style.configure("TFrame", background="#23272e")
    # かっこいいグラデーション風プログレスバー
    style.layout("Cool.Horizontal.TProgressbar",
        [('Horizontal.Progressbar.trough', {'children': [
            ('Horizontal.Progressbar.pbar', {'side': 'left', 'sticky': 'ns'})], 'sticky': 'nswe'})])
    style.configure("Cool.Horizontal.TProgressbar",
        troughcolor="#181a20", bordercolor="#23272e", background="#00bfff", lightcolor="#00bfff", darkcolor="#005f8f", thickness=22, borderwidth=2, relief="flat")
    # タイトル
    tk.Label(progress_root, text="画像を処理中...", font=("Segoe UI", 15, "bold"), bg="#23272e", fg="#fff").pack(pady=12)
    progress_var = tk.DoubleVar()
    progress = ttk.Progressbar(progress_root, variable=progress_var, maximum=len(files), length=380, style="Cool.Horizontal.TProgressbar")
    progress.pack(pady=8)
    status_label = tk.Label(progress_root, text="", font=("Segoe UI", 12), bg="#23272e", fg="#fff")
    status_label.pack(pady=2)
    percent_label = tk.Label(progress_root, text="", font=("Segoe UI", 12), bg="#23272e", fg="#fff")
    percent_label.pack(pady=2)
    progress_root.update()

    for idx, fname in enumerate(files, 1):
        in_path = os.path.join(folder, fname)
        out_path = os.path.join(out_folder, fname)
        status_label.config(text=f"{fname} ({idx}/{len(files)})")
        percent = int(idx / len(files) * 100)
        percent_label.config(text=f"進捗: {percent}%")
        progress_var.set(idx-1)
        progress_root.update()
        try:
            img = Image.open(in_path).convert("RGB")
            img = auto_apply_mosaic(img, pattern)
            if not out_folder_created:
                os.makedirs(out_folder, exist_ok=True)
                out_folder_created = True
            img.save(out_path)
        except Exception as e:
            print(f"エラー: {fname}: {e}")
    progress_var.set(len(files))
    status_label.config(text="完了")
    percent_label.config(text="進捗: 100%")
    progress_root.update()
    tkMessageBox.showinfo("完了", "全ての画像の処理が完了しました。", parent=progress_root)
    progress_root.destroy()

if __name__ == "__main__":
    main()
