import tkinter as tk
import tkinter.filedialog as tkFileDialog
import tkinter.messagebox
from PIL import Image, ImageTk
from PIL.PngImagePlugin import PngInfo
import os
import sys

def snap_position(x, ceil=False):
    # グリッドに吸着
    step = 10 #グリッドの吸着サイズを変更したい場合は左記の数値を変更してください。2023/05/13 20→10 に変更

    x = int(x)
    m = x % step

    if m != 0:
        x -= m
        if ceil:
            x += step

    return x

#Undo情報を保有するクラス
class Undo:
    def __init__(self, region, x1, y1, x2, y2):
        self.region = region
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

class App(tk.Frame):

    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        #処理モード
#        self.applist = ['モザイク大','モザイク小','ぼかし','黒塗り','切抜','縮小']
        self.applist = ['モザイク大','モザイク小','ぼかし','黒塗り']
        self.mode = 1  #モザイクサイズの初期値を変更したい場合は左記の数値を変更してください。（0:モザイク大 1:モザイク小 2:ぼかし 3:黒塗り）2023/05/13 0→1 に変更
        root.title(self.applist[self.mode])

        # 画像ファイルリストの配列変数
        self.image_file_list = []
        self.image_file_index = 0

        if (len(sys.argv[1:])==1):
            arguments = sys.argv[1]
            print(arguments)

            #引数がフォルダの時
            if os.path.isdir(arguments):
                #フォルダ内の画像ファイルを名前順でソートし画像ファイルリストにすべて追加する
                folder_path = arguments
                for file_name in sorted(os.listdir(folder_path)):
                    if file_name.endswith('.jpg') or file_name.endswith('.jpeg') or file_name.endswith('.png') or file_name.endswith('.gif'):
                        self.image_file_list.append(os.path.join(folder_path, file_name))

                #画像ファイルリストにデータが存在する時
                if (len(self.image_file_list) > self.image_file_index):
                    # 画像ファイルリストから先頭のファイルを取得する
                    image_file = self.image_file_list[self.image_file_index]
                    self.load_image(image_file)
                #画像ファイルリストにデータが存在しない時
                else:
                    print('引数で指定されたフォルダ内に、画像ファイルが見つかりませんでした。')
                    tkinter.messagebox.showinfo("終了", "引数で指定されたフォルダ内に、画像ファイルが見つかりませんでした。")
                    sys.exit(1)
                    
            #引数がファイルの時
            else:
                self.load_image(arguments)

        else:
            self.load_image()

        self.create_canvas()

        self.pack()

        # キーボードイベントを登録する
        self.master.bind_all("<Control-z>", self.on_undo)
        self.master.bind_all("<Control-n>", self.on_next)
        self.master.bind_all("<Right>", self.on_next)
        self.master.bind_all("<Control-b>", self.on_back)
        self.master.bind_all("<Left>", self.on_back)

    #画像系のオブジェクトの開放
    def del_image(self):
        del self.write_path
        self.image.close()
        del self.image
        del self.parameters
        del self.image_width
        del self.image_height
        self.image_tk.__del__()
        del self.image_tk

    #キャンバス系のオブジェクトの開放
    def del_canvas(self):
        # フレームを削除する
        self.frame.pack_forget()
        self.frame = None

        # スクロールバーを削除する
        self.canvas.config(yscrollcommand=None)
        self.canvas.config(xscrollcommand=None)
        self.scrollbar_vertical.pack_forget()
        self.scrollbar_horizontal.pack_forget()
        self.scrollbar_vertical.destroy()
        self.scrollbar_horizontal.destroy()
        self.scrollbar_vertical = None
        self.scrollbar_horizontal = None

        # 画像を削除する
        self.canvas.delete(self.image_on_canvas)
        self.image_on_canvas = None

        # マウスイベントを解除する
        self.canvas.unbind("<ButtonPress-1>")
        self.canvas.unbind("<B1-Motion>")
        self.canvas.unbind("<ButtonRelease-1>")
        self.canvas.unbind_all("<MouseWheel>")
        self.canvas.unbind_all("<ButtonPress-3>")
        self.canvas.unbind_all("<Double-1>")

        # 矩形描画用の変数を初期化する
        self.start_x = None
        self.start_y = None
        self.end_x = None
        self.end_y = None
        self.rect = None

        # Undo用の配列変数を初期化する
        self.undo_list = []

        # キャンバスを削除する
        self.canvas.destroy()
        self.canvas = None

    def create_canvas(self):
        # キャンバスを作成する
        self.frame = tk.Frame(self)
        self.frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        canX=self.image_width
        canY=self.image_height

        if canX >2048:
            canX = 2048
        if canY >2048:
            canY = 2048

        self.canvas = tk.Canvas(self.frame, width=canX, height=canY)
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.canvas.configure(scrollregion=(0, 0, self.image_width, self.image_height))
        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)

        # スクロールバーを作成する
        self.scrollbar_vertical = tk.Scrollbar(self, orient=tk.VERTICAL)
        self.scrollbar_vertical.pack(side=tk.RIGHT, fill=tk.Y)
        self.scrollbar_vertical.config(command=self.canvas.yview)
        self.canvas.config(yscrollcommand=self.scrollbar_vertical.set)
        # 横方向のスクロールバーを作成する
        self.scrollbar_horizontal = tk.Scrollbar(self.frame, orient=tk.HORIZONTAL)
        self.scrollbar_horizontal.pack(side=tk.BOTTOM, fill=tk.X)
        self.scrollbar_horizontal.config(command=self.canvas.xview)
        self.canvas.config(xscrollcommand=self.scrollbar_horizontal.set)
        # 画像をキャンバスに表示する
        self.image_on_canvas = self.canvas.create_image(0, 0, anchor=tk.NW, image=self.image_tk)

        # マウスイベントを登録する
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_move_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)
        self.canvas.bind_all("<MouseWheel>", self.on_mouse_wheel)
        self.canvas.bind_all("<ButtonPress-3>", self.on_right_button_press)
        self.canvas.bind_all("<Double-1>", self.on_right_button_double)

        # 矩形を描画するための変数
        self.start_x = None
        self.start_y = None
        self.end_x = None
        self.end_y = None
        self.rect = None

        # Undo用の配列変数
        self.undo_list = []

    def load_image(self, file=None):

        if file is None:
            # ファイルを選択する
            filepath = tkFileDialog.askopenfilename(filetypes=[("画像ファイル", "*.jpg;*.jpeg;*.png;*.gif")])
        else:
            filepath = file

        # ファイル名、拡張子、フルパスを取得する
        basename = os.path.basename(filepath)
        name, ext = os.path.splitext(basename)
        dirname = os.path.dirname(filepath)

        #フォルダ指定モードの時（ファイルリストが存在する）時
        if (len(self.image_file_list) > 0):
            # フルパスを組み立てる（フォルダ名に "_mc" を追加する。ファイル名はそのまま。）
            new_filepath = os.path.join(dirname + "_mc", name + ext)
        else:
            # フルパスを組み立てる（ファイル名に "_mc" を追加する）
            new_filepath = os.path.join(dirname, name + "_mc" + ext)

        self.write_path=new_filepath
        self.image = Image.open(filepath)
        try:
            parameters =self.image.text['parameters']
        except:
            parameters =''
        self.parameters=parameters
        self.image_width, self.image_height = self.image.size
        self.image_tk = ImageTk.PhotoImage(self.image)

    def on_undo(self, event):
        #Undoリストに復元用データが存在する時
        if (len(self.undo_list) > 0):
            # 範囲をUndoリストから復元する
            undo = self.undo_list.pop()

            #切り抜きと縮小のUndo処理の時（すべての座標が-1）
            if undo.x1 == -1 and undo.y1 == -1 and undo.x2 == -1 and undo.y2 == -1:
                # 画像（全体）を更新する
                self.image = undo.region
            else:
                # 画像（差分）を更新する
                self.image.paste(undo.region, (undo.x1, undo.y1, undo.x2, undo.y2))

            # キャンバスに表示する画像を更新する
            self.image_tk = ImageTk.PhotoImage(self.image)
            self.canvas.itemconfig(self.image_on_canvas, image=self.image_tk)
            self.image_width, self.image_height = self.image.size

    #指定されたフォルダパスが存在しない場合は、再帰的にフォルダを作成する処理
    def create_folder_if_not_exist(self, path):
        if not os.path.exists(path):
            os.makedirs(path)

    #次の画像ファイルを開く処理（フォルダ指定モード用の処理）
    def on_next(self, event):
        #フォルダ指定モードではない（ファイルリストが存在しない）時、何も処理せず終了する
        if (len(self.image_file_list) == 0): return

        #画像イメージのインデックスを加算する
        self.image_file_index += 1
        #画像ファイルリストのインデックスが有効な時
        if (len(self.image_file_list) > self.image_file_index):
            #画像をセーブする
            self.save_image()

            # 画像ファイルリストから該当インデックスの画像ファイルを取得する
            image_file = self.image_file_list[self.image_file_index]

            self.del_image()
            self.del_canvas()
            self.pack_forget()

            self.load_image(image_file)
            self.create_canvas()
            self.pack()

        #画像ファイルリストのインデックスが無効な時
        else:
            result = tkinter.messagebox.askyesno("終了", "現在開いている画像はフォルダ内の最後の画像です。次の画像ファイルはありません。終了しますか？")
            if result:
                #画像をセーブする
                self.save_image()
                root.destroy()
            #画像イメージのインデックスを戻す
            self.image_file_index -= 1

    #前の画像ファイルを開く処理（フォルダ指定モード用の処理）
    def on_back(self, event):
        #フォルダ指定モードではない（ファイルリストが存在しない）時、何も処理せず終了する
        if (len(self.image_file_list) == 0): return

        #画像イメージのインデックスを減算する
        self.image_file_index -= 1
        #画像ファイルリストのインデックスが有効な時
        if (0 <= self.image_file_index):
            #画像をセーブする
            self.save_image()

            # 画像ファイルリストから該当インデックスの画像ファイルを取得する
            image_file = self.image_file_list[self.image_file_index]

            self.del_image()
            self.del_canvas()
            self.pack_forget()

            self.load_image(image_file)
            self.create_canvas()
            self.pack()

        #画像ファイルリストのインデックスが無効な時
        else:
            result = tkinter.messagebox.askyesno("終了", "現在開いている画像はフォルダ内の先頭の画像です。前の画像ファイルはありません。終了しますか？")
            if result:
                #画像をセーブする
                self.save_image()
                root.destroy()
            #画像イメージのインデックスを戻す
            self.image_file_index += 1

    def on_right_button_press(self, event):
        self.mode=self.mode+1
        if (self.mode>=len(self.applist)):
            self.mode=0
        root.title(self.applist[self.mode])

    def on_right_button_double(self, event):
        result = tkinter.messagebox.askyesno("終了", "保存せずに終了しますか？")
        if result:
            root.destroy()

    def snap_coords_of_event(self, x, y, ceil=False):
        return snap_position(self.canvas.canvasx(x)), snap_position(self.canvas.canvasy(y))

    def on_button_press(self, event):
        # マウスの左ボタンが押されたときに呼び出されるコールバック関数
        self.start_x, self.start_y = self.snap_coords_of_event(event.x, event.y)

        # 矩形を描画するためのオブジェクトを作成する
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, fill="", outline="red")

    def on_move_press(self, event):
        # マウスの左ボタンが押されている状態でマウスが移動したときに呼び出されるコールバック関数
        cur_x, cur_y = self.snap_coords_of_event(event.x, event.y, ceil=True)

        # 矩形を描画するためのオブジェクトを更新する
        self.canvas.coords(self.rect, self.start_x, self.start_y, cur_x, cur_y)

    def on_button_release(self, event):
        # マウスの左ボタンが離されたときに呼び出されるコールバック関数
        self.end_x, self.end_y = self.snap_coords_of_event(event.x, event.y, ceil=True)

        if ((self.start_y==self.end_y) or (self.start_x== self.end_x)):
            return "not select"

        # 矩形を描画するためのオブジェクトを削除する
        self.canvas.delete(self.rect)

        # 矩形の範囲内の画素をモザイク化する
        self.apply_mosaic()

    def apply_mosaic(self):
        # 矩形の範囲内の画素をモザイク化する
        # 矩形の左上と右下の座標を取得する
        x1, y1 = min(self.start_x, self.end_x), min(self.start_y, self.end_y)
        x2, y2 = max(self.start_x, self.end_x), max(self.start_y, self.end_y)

        # 範囲を取得する
        region = self.image.crop((x1, y1, x2, y2))

        if (self.applist[self.mode]=='モザイク大'):
            # 範囲をUndoリストに追加する
            self.undo_list.append(Undo(self.image.crop((x1, y1, x2, y2)), x1, y1, x2, y2))

            # モザイクをかける
            width = (x2 - x1) // 20
            height = (y2 - y1) // 20
            if width == 0:
                width = 1
            if height == 0:
                height = 1
            region = region.resize((width, height), Image.Resampling.BICUBIC)
            region = region.resize((x2 - x1, y2 - y1), Image.Resampling.NEAREST)

        elif (self.applist[self.mode]=='モザイク小'):
            # 範囲をUndoリストに追加する
            self.undo_list.append(Undo(self.image.crop((x1, y1, x2, y2)), x1, y1, x2, y2))

            # モザイクをかける
            width = (x2 - x1) // 10
            height = (y2 - y1) // 10
            if width == 0:
                width = 1
            if height == 0:
                height = 1
            region = region.resize((width, height), Image.Resampling.BICUBIC)
            region = region.resize((x2 - x1, y2 - y1), Image.Resampling.NEAREST)

        elif (self.applist[self.mode]=='ぼかし'):
            # 範囲をUndoリストに追加する
            self.undo_list.append(Undo(self.image.crop((x1, y1, x2, y2)), x1, y1, x2, y2))

            # ぼかしをかける
            width = (x2 - x1) // 10
            height = (y2 - y1) // 10
            if width == 0:
                width = 1
            if height == 0:
                height = 1
            region = region.resize((width, height), Image.Resampling.BICUBIC)
            region = region.resize((x2 - x1, y2 - y1), Image.Resampling.LANCZOS)

        elif (self.applist[self.mode]=='黒塗り'):
            # 範囲をUndoリストに追加する
            self.undo_list.append(Undo(self.image.crop((x1, y1, x2, y2)), x1, y1, x2, y2))

            # 黒塗りにする
            region = Image.new("RGB", (x2 - x1, y2 - y1), (0, 0, 0))

        elif (self.applist[self.mode]=='切抜'):
            # 全体をUndoリストに追加する
            self.undo_list.append(Undo(self.image, -1, -1, -1, -1))

            # キャンバスに表示する画像を更新する（選択範囲のみに切り抜き）
            self.image = region
            self.image_tk = ImageTk.PhotoImage(self.image)
            self.canvas.itemconfig(self.image_on_canvas, image=self.image_tk)
            self.image_width, self.image_height = self.image.size
            return

        elif (self.applist[self.mode]=='縮小'):
            # 全体をUndoリストに追加する
            self.undo_list.append(Undo(self.image, -1, -1, -1, -1))

            # キャンバスに表示する画像を更新する（選択範囲のサイズに縮小）
            self.image =  self.image.resize((int(self.image_width*((y2 - y1)/self.image_height)),(y2 - y1)), Image.Resampling.BICUBIC)

            self.image_tk = ImageTk.PhotoImage(self.image)
            self.canvas.itemconfig(self.image_on_canvas, image=self.image_tk)
            self.image_width, self.image_height = self.image.size
            return

        # 画像を更新する
        self.image.paste(region, (x1, y1, x2, y2))

        # キャンバスに表示する画像を更新する
        self.image_tk = ImageTk.PhotoImage(self.image)
        self.canvas.itemconfig(self.image_on_canvas, image=self.image_tk)

    def on_mouse_wheel(self, event):
        # マウスホイールを使用してスクロールする
        self.canvas.yview_scroll(int(-0.05*event.delta), "units")

    def save_image(self):
        #フォルダ指定モードかつ、モザイク処理の履歴がなにもない時、保存せずスキップする
        if len(self.image_file_list) > 0 and len(self.undo_list) == 0: return

        # 画像を保存する
        metadata = PngInfo()
        if self.parameters != '':
            metadata.add_text("parameters", self.parameters)

        #出力先の親フォルダが存在しない場合は作成する
        self.create_folder_if_not_exist(os.path.dirname(self.write_path))
        self.image.save(self.write_path, pnginfo=metadata)

    def click_close(self):
        self.save_image()
        root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = App(master=root)
    root.protocol("WM_DELETE_WINDOW", app.click_close)
    app.mainloop()
