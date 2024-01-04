# クイックソートって基準値と同じ値だったらどうすんの？？？　基準値より小さいデータ、とあるから無視ってコト？！

### 試験用クイックソート初期設定
array = [18, 37, 21, 14, 7, 12, 19, 6] # 操作する配列（リストだけど）
standard = int(input("基準値を入力して下さい => ")) # 基準値


times = 1
for r in reversed(array): 
    if r < standard:
        std_idx = array.index(standard)
        r_idx = array.index(r)
        array[r_idx] = standard # 6の場所に14を   
    
        array[std_idx] = r      # 14の場所に6を
        print(f"【{times}回目】ソート結果")
        print(array)
        print()
        times += 1
        break

r_std = None
l_std = None
while True:
    # 先頭に戻るとrightとleftは初期化される
    right = len(array) - 1
    left = 0     

    while True:
        # 基準値よりも右側の値が小さくなった場合
        if array[right] < standard:
            r_std = array[right] # 基準値をより小さく更新
            break
        right -= 1
        
    while True:
        # 基準値よりも左側の値が大きくなった場合
        if array[left] > standard:
            l_std = array[left] # 左側の数を保存
            break
        left += 1
        
    # 終了条件
    if right <= left:
        # 右端の基準値と入れ替える
        array[array.index(standard)] = l_std
        array[array.index(l_std)] = standard
        print(f"【{times}回目】ソート結果")
        print(array)
        print("🏮 Complete the Quick-Sort 🏮")
        break
        
    # 入れ替える
    array[array.index(r_std)] = l_std
    array[array.index(l_std)] = r_std
    
    print(f"【{times}回目】ソート結果")
    print(array)
    print()
    times += 1
    
