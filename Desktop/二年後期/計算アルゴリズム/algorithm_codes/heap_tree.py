import heapq


# ヒープheapへの数値の追加を行う関数
def add_heap(heap: list, element: int):
    heapq.heappush(heap, element)
    

# ヒープheapから最大値の取り出しを行う関数
def delete_heap(heap: list):
    return heapq.heappop(heap)

# 終了処理は無いのでCtr + Cで終了すること
if __name__ == "__main__":
    # 初期キューの設定
    first_q = [6, 3, 1, 1]
    # heapqの組み込み関数heappop()は最小の要素を返すので、-1倍して最大の要素を取り出すようにする
    hq = [-1*e for e in first_q] 
    # hq = heapq.heapify(hq) # ヒープに変換=> なんか変換しなくても出来た。そもそもheappop等はリストを引数とするからなにこれ
    
    # ヒープの操作
    times = 1
    while True:
        # 1入力で要素追加、0入力で要素削除
        act = int(input(f"【{times}回目】：add = 1, delete = 0, => "))
        
        # 要素を追加
        if act:
            add = int(input("追加する数値を入力して下さい=> "))*-1
            print(f"🐍 add = {add*-1}") # 出力の時は-1倍して元に戻す
            add_heap(hq, add)

        # 要素を削除
        else:
            del_element = delete_heap(hq)
            print(f"🚩 delete = {del_element*-1}") # 出力の時は-1倍して元に戻す
            
        print(f"heap = {[-1*e for e in hq]}") # 出力の時は-1倍して元に戻す
        times += 1
        
        print()
            
 