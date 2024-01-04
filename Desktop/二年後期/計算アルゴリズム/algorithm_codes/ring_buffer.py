class RingBuffer:
    def __init__(self, size):
        self.buffer = [None for i in range(0, size)]
        self.head = 0
        self.tail = 0
        self.size = size
        # self.adjust = 1

    def __len__(self):
        return (self.tail - self.head + self.size) % self.size

    # エンキュー
    def add(self, value):
        self.buffer[self.tail] = value
        self.tail = (self.tail + 1) % self.size  

    # デキュー
    def get(self, index=None):
        if index is not None:
            return self.buffer[index]

        value = self.buffer[self.head]
        self.head = (self.head + 1) % self.size 
        # self.adjust = 0 # 初回のみ0で以降は1

        return value


# 最初キュ(配列)ーは空なので、初期配列の設定をする必要がある。
# 終了処理を作っていないので、終了時はCtr + Cで終了。
if __name__ == "__main__":
    rbuf = RingBuffer(5)

    times = 1
    while True:
        act = int(input(f"【{times}回目】INPUT：enqueue = 1, dequeue = 0, => "))
        if act not in [0, 1]:
            print("値が適切ではありません。再入力を求めます。")
            continue
        
        if act:
            enqueue = int(input("エンキューする値を入力=> "))
            rbuf.add(enqueue)
            print(f"🐍 enqueue = {enqueue}")
            
        else:
            print(f"🚩dequeue = {rbuf.get()}")
            rbuf.buffer[rbuf.head-1] = None

            
        times += 1
        print(rbuf.buffer)  # 配列の中身を出力
        print()
