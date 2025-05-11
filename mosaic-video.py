import os
import sys
import cv2
import numpy as np
from PIL import Image
from ultralytics import YOLO
import tkinter as tk

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
    root = tk.Tk()
    root.title("モザイクパターン選択")
    root.geometry("420x360")
    root.configure(bg="#23272e")
    title = tk.Label(root, text="モザイクパターンを選択してください", font=("Segoe UI", 17, "bold"), bg="#23272e", fg="#fff")
    title.pack(padx=10, pady=18)
    listbox_frame = tk.Frame(root, bg="#23272e")
    listbox_frame.pack(padx=24, pady=8, fill=tk.BOTH, expand=True)
    listbox = tk.Listbox(listbox_frame, height=len(patterns), font=("Segoe UI", 15), bg="#181a20", fg="#fff", selectbackground="#00bfff", selectforeground="#fff", relief="flat", highlightthickness=0, bd=0)
    for p in patterns:
        listbox.insert(tk.END, p)
    listbox.selection_set(0)
    listbox.pack(fill=tk.BOTH, expand=True)
    listbox.bind('<Double-1>', on_select)
    btn_frame = tk.Frame(root, bg="#23272e")
    btn_frame.pack(pady=18)
    btn_ok = tk.Button(btn_frame, text="OK", font=("Segoe UI", 14), width=10, height=2, bg="#23272e", fg="#fff", relief="raised", bd=3, activebackground="#00bfff", activeforeground="#fff", command=on_ok)
    btn_ok.pack(side=tk.LEFT, padx=16)
    btn_ok.bind("<Enter>", lambda e: e.widget.config(bg="#00bfff", fg="#fff", relief="raised", bd=3))
    btn_ok.bind("<Leave>", lambda e: e.widget.config(bg="#23272e", fg="#fff", relief="raised", bd=3))
    btn_cancel = tk.Button(btn_frame, text="キャンセル", font=("Segoe UI", 14), width=10, height=2, bg="#23272e", fg="#fff", relief="raised", bd=3, activebackground="#ff5555", activeforeground="#fff", command=on_cancel)
    btn_cancel.pack(side=tk.LEFT, padx=16)
    btn_cancel.bind("<Enter>", lambda e: e.widget.config(bg="#ff5555", fg="#fff", relief="raised", bd=3))
    btn_cancel.bind("<Leave>", lambda e: e.widget.config(bg="#23272e", fg="#fff", relief="raised", bd=3))
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
        from PIL import ImageFilter
        return region.filter(ImageFilter.GaussianBlur(radius=8))
    elif pattern == "黒塗り":
        return Image.new("RGB", (w, h), (0, 0, 0))
    else:
        return region

def auto_apply_mosaic(image, pattern, model, names):
    import tempfile
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
        image.save(tmp.name)
        tmp_path = tmp.name
    results = model(tmp_path, conf=0.15, iou=0.3)
    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
            conf = float(box.conf[0])
            cls_idx = int(box.cls[0])
            cls_name = names[cls_idx] if cls_idx < len(names) else ""
            if cls_name in ["make_love", "nipple"]:
                continue
            w, h = x2 - x1, y2 - y1
            if w < 10 or h < 10:
                continue
            shrink_ratio_w = 0.75
            shrink_ratio_h = 0.45
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

def ask_video_mode():
    import tkinter as tk
    mode = {'value': None}
    def select_file():
        mode['value'] = 'file'
        root.quit()
    def select_folder():
        mode['value'] = 'folder'
        root.quit()
    root = tk.Tk()
    root.title("動画処理モード選択")
    root.geometry("480x260")
    root.configure(bg="#23272e")
    tk.Label(root, text="処理方法を選択してください", font=("Segoe UI", 18, "bold"), bg="#23272e", fg="#fff").pack(pady=32)
    btn_file = tk.Button(root, text="動画ファイルを選択", font=("Segoe UI", 15), width=22, height=2, bg="#23272e", fg="#fff", relief="raised", bd=3, activebackground="#00bfff", activeforeground="#fff", command=select_file)
    btn_file.pack(pady=12)
    btn_folder = tk.Button(root, text="フォルダ内の全動画を一括処理", font=("Segoe UI", 15), width=28, height=2, bg="#23272e", fg="#fff", relief="raised", bd=3, activebackground="#00bfff", activeforeground="#fff", command=select_folder)
    btn_folder.pack(pady=12)
    root.mainloop()
    root.destroy()
    return mode['value']

def main():
    import tkinter.filedialog as tkFileDialog
    import tkinter.messagebox as tkMessageBox
    from tkinter import ttk
    # モデル・クラス名
    names = ['anus', 'make_love', 'nipple', 'penis', 'vagina']
    yolo_model_path = os.path.join(os.path.dirname(__file__), 'erax_nsfw_yolo11m.pt')
    model = YOLO(yolo_model_path)
    # --- 新モード選択 ---
    mode = ask_video_mode()
    if mode == 'file':
        root = tk.Tk(); root.withdraw()
        video_paths = [tkFileDialog.askopenfilename(
            title="動画ファイルを選択してください",
            filetypes=[
                ("動画ファイル", "*.mp4;*.avi;*.mov;*.wav"),
                ("MP4 files", "*.mp4"),
                ("AVI files", "*.avi"),
                ("MOV files", "*.mov"),
                ("WAV files", "*.wav"),
                ("All files", "*.*")
            ])]
        root.destroy()
    elif mode == 'folder':
        root = tk.Tk(); root.withdraw()
        folder = tkFileDialog.askdirectory(title="動画フォルダを選択してください")
        root.destroy()
        if not folder:
            print("フォルダが選択されませんでした。処理を中止します。")
            return
        video_paths = [os.path.join(folder, f) for f in os.listdir(folder)
                      if f.lower().endswith((".mp4", ".avi", ".mov"))
                      and not (f.lower().endswith("_mc.mp4") or f.lower().endswith("_mc.avi") or f.lower().endswith("_mc.mov"))]
        if not video_paths:
            tkMessageBox.showinfo("動画なし", "選択フォルダに対応動画がありません。", parent=None)
            return
    else:
        print("キャンセルされました。処理を中止します。")
        return
    pattern = ask_mosaic_pattern()
    if pattern is None:
        print("キャンセルされました。処理を中止します。")
        return
    processed_outputs = []  # 追加: 出力ファイルパスを格納
    for video_path in video_paths:
        ext = os.path.splitext(video_path)[1].lower()
        if ext == ".mp4":
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out_path = os.path.splitext(video_path)[0] + "_mc.mp4"
        elif ext == ".avi":
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            out_path = os.path.splitext(video_path)[0] + "_mc.avi"
        elif ext == ".mov":
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out_path = os.path.splitext(video_path)[0] + "_mc.mov"
        elif ext == ".wav":
            tkMessageBox.showinfo("未対応", "WAVファイル（音声）はモザイク処理できません。", parent=None)
            print("WAVファイルは未対応です。処理を中止します。")
            continue
        else:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out_path = os.path.splitext(video_path)[0] + "_mc.mp4"
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        out = cv2.VideoWriter(out_path, fourcc, fps, (width, height))
        # 進捗バー
        progress_root = tk.Tk()
        progress_root.title(f"動画モザイク処理進捗: {os.path.basename(video_path)}")
        progress_root.geometry("440x170")
        progress_root.configure(bg="#23272e")
        style = ttk.Style(progress_root)
        style.theme_use("clam")
        style.layout("Cool.Horizontal.TProgressbar",
            [('Horizontal.Progressbar.trough', {'children': [
                ('Horizontal.Progressbar.pbar', {'side': 'left', 'sticky': 'ns'})], 'sticky': 'nswe'})])
        style.configure("Cool.Horizontal.TProgressbar",
            troughcolor="#181a20", bordercolor="#23272e", background="#00bfff", lightcolor="#00bfff", darkcolor="#005f8f", thickness=22, borderwidth=2, relief="flat")
        tk.Label(progress_root, text=f"動画を処理中...", font=("Segoe UI", 15, "bold"), bg="#23272e", fg="#fff").pack(pady=12)
        progress_var = tk.DoubleVar()
        progress = ttk.Progressbar(progress_root, variable=progress_var, maximum=total, length=380, style="Cool.Horizontal.TProgressbar")
        progress.pack(pady=8)
        status_label = tk.Label(progress_root, text="", font=("Segoe UI", 12), bg="#23272e", fg="#fff")
        status_label.pack(pady=2)
        percent_label = tk.Label(progress_root, text="", font=("Segoe UI", 12), bg="#23272e", fg="#fff")
        percent_label.pack(pady=2)
        progress_root.update()
        idx = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            idx += 1
            status_label.config(text=f"{idx}/{total} フレーム")
            percent = int(idx / total * 100)
            percent_label.config(text=f"進捗: {percent}%")
            progress_var.set(idx)
            progress_root.update()
            img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            img = auto_apply_mosaic(img, pattern, model, names)
            out_frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
            out.write(out_frame)
        cap.release()
        out.release()
        progress_var.set(total)
        status_label.config(text="完了")
        percent_label.config(text="進捗: 100%")
        progress_root.update()
        progress_root.destroy()
        processed_outputs.append(out_path)  # 追加: 出力ファイルパスを記録
    # 通知処理
    if mode == 'file' and processed_outputs:
        tkMessageBox.showinfo("完了", f"全てのフレームの処理が完了しました。\n出力: {processed_outputs[0]}")
    elif mode == 'folder' and processed_outputs:
        outlist = '\n'.join(processed_outputs)
        tkMessageBox.showinfo("完了", f"全ての動画の処理が完了しました。\n出力:\n{outlist}")

if __name__ == "__main__":
    main()
