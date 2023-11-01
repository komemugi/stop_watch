import tkinter as tk
import time
from tkinter import filedialog
from PIL import ImageTk, Image, UnidentifiedImageError

import os
import pyautogui # 使ってないけど、インポートしたら画質良くなった(でも画像は小さくなってしまった)


class Application(tk.Frame): # frameとはbuttonやlabelなど複数のウィジットを配置できる入れ物のようなウィジェット
    initialize_flag = 0 # 背景画像削除の前後で分岐させるためのフラグ
    
    ## imageButton_clicked()内で使用
    RESIZE_RATIO = 1 # 縮小倍率の規定
    
    def __init__(self, matrix, master=None):
        super().__init__(master)
        
        # ウィンドウ設定
        self.background = None
                
        master.geometry("800x400")
        
        width = 800
        height = 400
        
        # 変数定義
        self.matrix = matrix
        self.master = master
        self.startTime = 0.0
        self.elapsedTime = 0.0 # 経過時間を保存するための変数
        self.after_id = 0
        self.image_label = tk.Label(master)
        self.timeText_x = width / 4  # 00:00:00のx座標
        self.timeText_y = height / 5  # 00:00:00のy座標
        self.count_color = "black" # 時間カウントの初期色
        self.original_img = None # 背景画像を保存するための変数
        
        self.seconds = 0.0 # 時間カウントの秒数を保存するための変数
        self.minutes = 0
        self.hours = 0
        
        # self.clicked_entry_num = 0 # エンターを押されずにクリックされているエントリ数
        self.active_entry = None
        self.active_text_var = tk.StringVar()  # StringVarを使用してエントリのテキストを監視
        self.active_text_var.trace("w", self.on_text_change)  # テキスト変更を監視してon_text_change関数を呼び出す

        
        button_x = 0
        button_y = 135
        canvas_x = 5
        canvas_y = 0
        self.moveNum_x = 400
        self.moveNum_y = 200
        
        ## imageButton_clicked()内で呼び出される関数などで使用する
        self.img_resized = None
        self.canvas1 = None # 画像トリミングする際の新しいウィンドウでのキャンバス
        self.trimming_img = None
        
        # 画像をトリミングした座標
        self.x, self.y, self.w, self.h = 0, 0, 0, 0
        

        # 以下左半分
        if matrix == "00":
            self.background = "khaki"
          
        elif matrix == "10":
            canvas_y += self.moveNum_y
            button_y += self.moveNum_y
            self.background = "pink" # 背景は、キャンバスの大きさに等しい
            
        # 以下右半分
        elif matrix == "01":
            canvas_x = self.moveNum_x
            button_x = self.moveNum_x-5 # canvas_xを5にしたから、その分中心からずれるのを防ぐため
            self.background = "lightgreen"
          
        elif matrix == "11":
            canvas_x = self.moveNum_x
            canvas_y += self.moveNum_y
            button_x = self.moveNum_x-5
            button_y += self.moveNum_y
            self.background = "lightblue"
    
        self.canvas_position = [(canvas_x, canvas_y)] # 引用する際、xとy座標が視覚的に分かりやすくするためにタプルにした。しなくても良かった。
        
        self.button_position = [
            (5+100+(200/5)*1 + button_x, button_y), # start　白い半透明長方形のx座標=100とxの長さ=200の五等分を基準にした要素になっている
            (5+100+(200/5)*3 + button_x, button_y), # reset
            (5+100+(200/5)*5+(25*1) + button_x, button_y+15),  # count_color +25はcount_colorボタンの大きさ　+15はstart・resetのボタンとの差
            (5+100+(200/5)*5+(25*2) + button_x, button_y+15),  # image(background)
            (5+(25*1)+(0)*5+(0) + button_x, button_y+15)   # initialization_image
        ]

        # Canvasウィジェットを作成
        self.canvas = tk.Canvas(self.master, width=250, height=250)

        self.create_widget() # <--このため、起動直後から背景色等が付いている。       
        self.create_entry()
        
        # 実行内容
        self.pack()
        self.read_image()
        
        
    def read_image(self):   
        with open("imageFile.txt", "r", encoding="UTF-8") as f:
            with open("textFile.txt", "r", encoding="UTF-8") as rf:
                imagePath_lst = f.readlines()
                
                if self.matrix == "00":
                    destinationPath = imagePath_lst[0]
                    
                elif self.matrix == "10":
                    destinationPath = imagePath_lst[1]
                elif self.matrix == "01":
                    destinationPath = imagePath_lst[2]
                elif self.matrix == "11":
                    destinationPath = imagePath_lst[3]
                    
                if destinationPath and destinationPath != "Null" and destinationPath != "Null\n": # 既にimageパス情報が書き込まれているならば
                    if "\n" in destinationPath:
                        destinationPath = destinationPath.rstrip('\n')
                    
                    try:
                        img = Image.open(destinationPath)
                        img = img.resize((400, 200), Image.BILINEAR)
                        self.original_img = img
                        img = self.transparent_label(img)
                        
                        self.image = ImageTk.PhotoImage(img)
                        self.canvas.create_image(0, 0, anchor='nw', image=self.image)
                        self.create_texts()
                          
                    except FileNotFoundError:
                        # 画像の読み込みに失敗したらテキスト表示
                        self.canvas.create_text(self.timeText_x-10, self.timeText_y-32, fill = self.count_color, text="Fail to read the image:", font=("MSゴシック体", "20"), tag="Time", anchor="c") 
                        # self.canvas.create_text(self.timeText_x-10, self.timeText_y-32, fill = self.count_color, text="Fail to read the image:", font=("MSゴシック体", "24", "bold"), tag="Time", anchor="c")
                        self.create_texts()
                    
                    except UnidentifiedImageError:
                        # 画像が見つからなかったらテキストを表示
                        self.canvas.create_text(self.timeText_x-10, self.timeText_y-32, fill = self.count_color, text="Failed. Click to the \U0001F5D1.", font=("MSゴシック体", "20"), tag="Time", anchor="c") # \U0001F5D1 is 🗑️
                        # self.canvas.create_text(self.timeText_x-10, self.timeText_y-32, fill = self.count_color, text="Failed. Click to the \U0001F5D1.", font=("MSゴシック体", "24", "bold"), tag="Time", anchor="c") # \U0001F5D1 is 🗑️
                        self.create_texts()              
                        

    def create_entry(self):
        entry_width = 0
        entry_height = 0
        
        self.entry_idx = 0
        self.entry = tk.Entry(self.master, font=("MSゴシック体", 9))
        
        if self.matrix == "00":
            pass    
        elif self.matrix == "10":
            entry_height += self.moveNum_y
            self.entry_idx = 1
        elif self.matrix == "01":
            entry_width += self.moveNum_x-5
            self.entry_idx = 2
        elif self.matrix == "11":
            entry_width += self.moveNum_x-5
            entry_height += self.moveNum_y
            self.entry_idx = 3  
                    
        self.entry.place(x = 10 + entry_width, y = 5 + entry_height) # 旧yは15
        # print(f"width, height = {entry_width}, {entry_height}")
        with open("textFile.txt", "r", encoding="utf-8") as rf:
            line_lst = rf.readlines() # ファイルから読み込んでリストにしたエントリ名たち
            # エントリのデフォルト値（最初にエントリに書かれているテキスト）を決定する
            try:                 
                initial_text = line_lst[self.entry_idx].strip()
                self.active_text_var.set(initial_text)  # StringVarを設定（stringvarの更新はsetメソッドを使う）
                
            except IndexError:
                pass

        # エントリの作成コード
        self.entry.config(textvariable=self.active_text_var)  # StringVarをエントリに設定
        self.entry.bind("<FocusIn>", self.on_entry_focus_in)

    # 後続のコードでアクティブなentryにアクセスできるようにするための関数
    def on_entry_focus_in(self, event):
        self.active_entry = event.widget # イベントが発生したentryウィジェットを特定

    def on_text_change(self, *args):
        if self.active_entry is not None:
            txtSentence = self.active_text_var.get()  # アクティブなエントリのテキストを取得
            with open("textFile.txt", encoding="utf-8") as rf:
                line_lst = rf.readlines()
                with open("textFile.txt", "w", encoding="utf-8") as wf:
                    del line_lst[self.entry_idx] # 古いエントリ名を削除
                    line_lst.insert(self.entry_idx, txtSentence + "\n")
                    wf.writelines(line_lst)
        
        
    def start_button_clicked(self):
        self.start_stopButton = tk.Button(self.master, text=" II ", font=("MSゴシック", "16", "bold"), command=self.stop_button_clicked)
        self.start_stopButton.place(x=self.button_position[0][0], y=self.button_position[0][1], width=40, height=40)
        self.startTime = time.time() - self.elapsedTime # startTime変数に開始時間を代入
        self.update_time()
        Application.initialize_flag = 1 # スタートボタンが押されている最中に画像が除去されると、create_widgetが呼び出されることにより、ストップボタンが消滅するため
        

    # ストップボタンが押された時の処理
    def stop_button_clicked(self):
        self.start_stopButton = tk.Button(self.master, text=" ▶ ", font=("MSゴシック", "16", "bold"), command=self.start_button_clicked)
        self.start_stopButton.place(x=self.button_position[0][0], y=self.button_position[0][1], width=40, height=40)
        self.after_cancel(self.after_id)
        Application.initialize_flag = 0 


    # リセットボタンが押された時の処理
    def reset_button_clicked(self):
        self.startTime = time.time()
        self.elapsedTime = 0.0 # 経過時間を初期化
        self.canvas.delete("Time") # 表示時間を消去
        ## self.create_texts() # create_texts()は経過時間elapsedTimeの表示なので、リセットは出来ない
        self.canvas.create_text(self.timeText_x, self.timeText_y, fill = self.count_color, text=f"00:00:0{round(self.elapsedTime, 1)}", font=("MSゴシック", "20"), tag="Time", anchor="c") # 時間0.0を表示
        # self.canvas.create_text(self.timeText_x, self.timeText_y, fill = self.count_color, text=f"00:00:0{round(self.elapsedTime, 1)}", font=("MSゴシック", "24", "bold"), tag="Time", anchor="c") # 時間0.0を表示


    def create_texts(self):
        # 時間を表示
        # 経過時間が一桁と二桁の時とで二桁目の0をどう表示するかの処理
        if (self.elapsedTime // 60) < 10:
            seconds_format = "0" if self.seconds < 10 else ""
            self.canvas.create_text(self.timeText_x, self.timeText_y, fill=self.count_color, text=f"{self.hours:02d}:{self.minutes:02d}:{seconds_format}{round(self.seconds, 1)}", font=("MSゴシック", "20"), tag="Time", anchor="c") # 経過時間を表示
            # self.canvas.create_text(self.timeText_x, self.timeText_y, fill=self.count_color, text=f"{self.hours:02d}:{self.minutes:02d}:{seconds_format}{round(self.seconds, 1)}", font=("MSゴシック", "24", "bold"), tag="Time", anchor="c") # 経過時間を表示
        else:
            self.canvas.create_text(self.timeText_x, self.timeText_y, fill=self.count_color, text=f"{self.hours:02d}:{self.minutes:02d}:{round(self.seconds, 1)}", font=("MSゴシック", "20"), tag="Time", anchor="c") # 経過時間を表示
            # self.canvas.create_text(self.timeText_x, self.timeText_y, fill=self.count_color, text=f"{self.hours:02d}:{self.minutes:02d}:{round(self.seconds, 1)}", font=("MSゴシック", "24", "bold"), tag="Time", anchor="c") # 経過時間を表示


    # 文字色変更ボタンが押された時の処理
    def count_color_button_clicked(self):
        if self.count_color == "black":
            self.count_color = "white"
        else:
            self.count_color = "black"

        self.read_image()
        self.create_texts()

   
   ## カウント数を見やすくするために、カウントの下に半透明な長方形を設置する関数
    def transparent_label(self, img=None): 
        if img != None:
            img_x, img_y = img.size
            if self.count_color == "black": # 文字色が黒ならば白い長方形を付与する
                white_label = Image.new("RGBA", (200, 40), (255, 255, 255, 115)) # 白い半透明な長方形
                img_with_label = Image.new("RGB", img.size)  # 元画像と同じサイズの透明な画像を作成

                # 透明な画像に白い長方形を貼り付け(透け防止)
                img_with_label.paste(img, (0, 0))
                img_with_label.paste(white_label, (img_x // 4, (img_y // 4) + 10), white_label) # 第三引数に半透明な画像を渡すことで、合成後も半透明をキープ
                
                return img_with_label
            else:
                black_label = Image.new("RGBA", (200, 40), (0, 0, 0, 115)) # 黒い半透明な長方形
                img_with_label = Image.new("RGB", img.size)  # 元画像と同じサイズの透明な画像を作成

                # 透明な画像に黒い長方形を貼り付け
                img_with_label.paste(img, (0, 0))
                img_with_label.paste(black_label, (img_x // 4, (img_y // 4) + 10), black_label)

                return img_with_label
            
        else: # 第二引数として画像が与えられていなかったら
            img_x, img_y = self.original_img.size
            if self.count_color == "black": # 文字色が黒ならば白い長方形を付与する
                white_label = Image.new("RGBA", (200, 40), (255, 255, 255, 115)) # 白い半透明な長方形
                img_with_label = Image.new("RGB", self.original_img.size)  # 元画像と同じサイズの透明な画像を作成

                # 透明な画像に白い長方形を貼り付け(背景色の透け防止)
                img_with_label.paste(self.original_img, (0, 0))
                img_with_label.paste(white_label, (img_x // 4, (img_y // 4) + 10), white_label) # 第三引数に半透明な画像を渡すことで、合成後も半透明をキープ
                
                return img_with_label
            else:
                black_label = Image.new("RGBA", (200, 40), (0, 0, 0, 115)) # 黒い半透明な長方形
                img_with_label = Image.new("RGB", self.original_img.size)  # 元画像と同じサイズの透明な画像を作成

                # 透明な画像に黒い長方形を貼り付け
                img_with_label.paste(self.original_img, (0, 0))
                img_with_label.paste(black_label, (img_x // 4, (img_y // 4) + 10), black_label)

                return img_with_label    
            

    # 画像の縦横大きい方で長さを調整する関数（短い側は透明なので考えなくて良い）
    def biggerImageEdge_resizeTo_fourHundred(self, img):
        cimg_width, cimg_height = img.size

        # 画像のリサイズ
        if cimg_width >= cimg_height:
            new_width = 400 # 長い方を400にする
            new_height = cimg_height * 400 // cimg_width # 長い方の400に合わせて、元の画像と割合をあまり変えない大きさに変換
        else:
            new_height = 400
            new_width =cimg_width * 400 // cimg_height

        img = img.resize((new_width, new_height), Image.BILINEAR)
        
        return img, new_width, new_height
        
    
    def start_point_get(self, event):
        self.canvas1.delete("rect1") # 既に"rect1"のタグの図形があれば削除
        
        # canvas1上に四角形を描画
        self.canvas1.create_rectangle(event.x,
                                    event.y,
                                    event.x + 1,
                                    event.y + 1,  # 高さを1に設定
                                    outline="red",
                                    tag="rect1"
                                    )
        
        # 変数に座標を格納
        self.start_x, self.start_y = event.x, event.y
        self.end_x, self.end_y = event.x, event.y  # 新たに end_x と end_y を初期化

    def rect_drawing(self, event):
        # ドラッグ中のマウスポインタが領域外に出た時の対処
        if event.x < 0:
            end_x = 0
        else:
            end_x = min(self.img_resized.width, event.x)
        
        if event.y < 0:
            end_y = 0
        else:
            end_y = min(self.img_resized.height, event.y)
        
        # 縦横比を固定して長方形を描画
        width = end_x - self.start_x
        height = width * (1/2)  # 縦横比を固定する場合、高さは幅の1/2倍に設定（400*200の比を維持）
        self.canvas1.coords("rect1", self.start_x, self.start_y, self.start_x + width, self.start_y + height)

        # 新たに end_x と end_y を更新
        self.end_x, self.end_y = end_x, end_y


    def release_action(self, event):
        # "rect1"タグの画像の座標を元の縮尺に戻して取得
        start_x, start_y, end_x, end_y = [
            round(n * Application.RESIZE_RATIO) for n in self.canvas1.coords("rect1")
        ]
        
        self.x, self.y, self.w, self.h = start_x, start_y, end_x, end_y
        
        self.joint_imageButton_clicked()

 
    # ドラッグ開始時のイベント（画像切り取りの範囲を指定する長方形の作成）を設定する関数
    # RESIZE_RETIO = 1 # 縮小倍率の規定
    def make_rectangle(self, new_window):
        self.img_resized = self.trimming_img.resize(size=(int(self.trimming_img.width / Application.RESIZE_RATIO),
                               int(self.trimming_img.height / Application.RESIZE_RATIO)),
                         resample=Image.BILINEAR) # 長方形を描画できる（描画する用ではない）

        img_tk = ImageTk.PhotoImage(self.trimming_img) # 画像をtkinter内で表示できる形式に変換
        # self.canvas1 = tk.Canvas(self.master, bg="black", width=self.trimming_img.width, height=self.trimming_img.height)
        self.canvas1 = tk.Canvas(new_window, bg="gray", width=self.trimming_img.width, height=self.trimming_img.height)
        self.canvas1.pack()
        
        self.canvas1.create_image(0, 0, image=img_tk, anchor=tk.NW)
        
        # canvasウィジェットを配置し、各種イベントを設定
        self.canvas1.bind("<ButtonPress-1>", lambda event: self.start_point_get(event))
        self.canvas1.bind("<B1-Motion>", lambda event: self.rect_drawing(event))
        self.canvas1.bind("<ButtonRelease-1>", lambda event: self.release_action(event))
        
        self.master.mainloop()
        
        
    def make_new_window(self): # img):
        # 新しいウィンドウを作成して画像を表示
        new_window = tk.Toplevel(self.master)
        new_window.geometry("500x500")  # 新しいウィンドウのサイズを設定
        
        self.make_rectangle(new_window)
        new_window.title("Image Preview")  # タイトルを設定
        
        new_window.mainloop()
    
        
    def joint_imageButton_clicked(self):        
        img = self.trimming_img.crop((self.x, self.y, self.w, self.h))
        img = img.resize((400, 200), Image.BILINEAR) # はみ出て画像を取得していた場合含めての処理
        self.original_img = img
        img = self.transparent_label() # テキスト下の半透明な長方形を設置する関数
                
        self.image = ImageTk.PhotoImage(img)
        self.canvas.create_image(0, 0, anchor='nw', image=self.image)
        
        cropped_img = self.trimming_img.crop((self.x, self.y, self.w, self.h))
        cropped_img = cropped_img.resize((400, 200), Image.BILINEAR)

        temp_path = f"cropped_img{self.matrix}.png"  # 一時ファイルのパス
        cropped_img.save(temp_path) # temp_pathを用いて、一時ファイルを作成
        
        ## cropped_imgがあるディレクトリのパスを求める
        current_directory = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(current_directory, f"cropped_img{self.matrix}.png")

        with open("imageFile.txt", "r", encoding="UTF-8") as f:
            pathInfo_lst = f.readlines()
            if self.matrix == "00":
                del pathInfo_lst[0]

                pathInfo_lst.insert(0, image_path+"\n")
                
            if self.matrix == "10":
                del pathInfo_lst[1]
                pathInfo_lst.insert(1, image_path+"\n")
                
            if self.matrix == "01":
                del pathInfo_lst[2]
                pathInfo_lst.insert(2, image_path+"\n")
                
            if self.matrix == "11":
                del pathInfo_lst[3]
                pathInfo_lst.insert(3, image_path+"\n")

            with open("imageFile.txt", "w", encoding="UTF-8") as f:
                f.writelines(pathInfo_lst)
                self.create_texts()   

    # 背景画像挿入ボタンがクリックされたときの処理
    def imageButton_clicked(self):
        imageFile_path = filedialog.askopenfilename()    
        if imageFile_path: # ファイルパスが存在するならば、という分岐
            img = Image.open(imageFile_path)

            base = Image.new("RGBA", (500, 500), (255, 255, 255, 0)) # 空いているスペースを透明な画像で埋めるため
            base_img, base_width, base_height = self.biggerImageEdge_resizeTo_fourHundred(img) # 画像を400*400の背景が透明な正方形に変換し、規格を統一する。
            base.paste(base_img, (250-base_width//2, 250-base_height//2)) # baseの中心にペースト
            
            self.trimming_img = base # original_imgtと統一できるかも？
            try:
                self.make_new_window() # crop()の引数をselfで渡す
            except: # _tkinter.TclError: can't invoke "wm" command: application has been destroyed
                pass
                

    # 背景画像の初期化処理
    def initialization_imageButton_clicked(self):
        with open("imageFile.txt", "r", encoding="UTF-8") as f:
            pathInfo_lst = f.readlines()
            if self.matrix == "00":
                del pathInfo_lst[0]
                pathInfo_lst.insert(0, "Null\n")
            if self.matrix == "10":
                del pathInfo_lst[1]
                pathInfo_lst.insert(1, "Null\n")
            if self.matrix == "01":
                del pathInfo_lst[2]
                pathInfo_lst.insert(2, "Null\n")
            if self.matrix == "11":
                del pathInfo_lst[3]
                pathInfo_lst.insert(3, "Null\n")
            with open("imageFile.txt", "w", encoding="UTF-8") as f:
                f.writelines(pathInfo_lst)
        self.create_widget()
        self.create_entry()
                

    # 表示時間の更新処理
    def update_time(self):        
        self.canvas.delete("Time") # 表示時間を削除
        self.elapsedTime = time.time() - self.startTime # 経過時間を代入

        # 経過時間を計算
        self.hours = int(self.elapsedTime // 3600)
        self.minutes = int((self.elapsedTime - self.hours*3600) // 60)
        self.seconds = round(self.elapsedTime - self.hours*3600 - self.minutes*60, 1)

        self.create_texts()
        self.after_id = self.after(50, self.update_time)
        
    # ストップウォッチ全体の基となるウィジェット作成
    def create_widget(self):
        # canvasウィジット作成
        self.canvas = tk.Canvas(self.master, width=390, height=190, bg=self.background) # 背景の大きさとその色の決定
        self.canvas.place(x=self.canvas_position[0][0], y=self.canvas_position[0][1])

        # 経過時間表示
        self.canvas.create_text(self.timeText_x, self.timeText_y, fill="black", text=f"{self.hours:02d}:{self.minutes:02d}:0{round(self.elapsedTime, 1)}", font=("MSゴシック体", "20"), tag="Time", anchor="c")
        # self.canvas.create_text(self.timeText_x, self.timeText_y, fill="black", text=f"{self.hours:02d}:{self.minutes:02d}:0{round(self.elapsedTime, 1)}", font=("MSゴシック体", "24", "bold"), tag="Time", anchor="c")

        # スタートボタン
        if Application.initialize_flag == 0:# initializedButtonClicked()で画像が除去された場合、ストップボタンがスタートボタンになり停止できなくなるのを防ぐ
            startButton = tk.Button(self.master, text=" ▶ ", font=("MSゴシック体", "16"), command=self.start_button_clicked)
            startButton.place(x=self.button_position[0][0], y=self.button_position[0][1], width=40, height=40)
        else:
            self.stop_button_clicked() # ストップすることで一応解決

        # リセットボタン \u21BA = '↺'
        resetButton = tk.Button(self.master, text="\u21BA", font=("MSゴシック体", "16"), command=self.reset_button_clicked)
        resetButton.place(x=self.button_position[1][0], y=self.button_position[1][1], width=40, height=40)

        # 文字色変更ボタン 
        count_color_button = tk.Button(self.master, text="🔳", command=self.count_color_button_clicked)
        count_color_button.place(x=self.button_position[2][0], y=self.button_position[2][1], width=25, height=25)

        # 画像を選択するためのボタン \U0001F4C4 = '📄'
        imageButton = tk.Button(self.master, text="\U0001F4C4", command=self.imageButton_clicked)
        imageButton.place(x=self.button_position[3][0], y=self.button_position[3][1], width=25, height=25)

        # 背景画像の初期化用ボタン \U0001F5D1 = '　 🗑️'
        initializationImgButton = tk.Button(self.master, text="\U0001F5D1", command=self.initialization_imageButton_clicked)
        initializationImgButton.place(x=self.button_position[4][0], y=self.button_position[4][1], width=25, height=25)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Stop Watch")
    matrix_00 = Application("00", master=root)
    matrix_01 = Application("01", master=root)
    matrix_10 = Application("10", master=root)
    matrix_11 = Application("11", master=root)
    
    root.resizable(width=False, height=False) # ウィンドウサイズを固定
    root.mainloop()