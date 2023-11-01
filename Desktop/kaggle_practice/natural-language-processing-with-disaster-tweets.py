# This Python 3 environment comes with many helpful analytics libraries installed
# It is defined by the kaggle/python Docker image: https://github.com/kaggle/docker-python
# For example, here's several helpful packages to load

import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)

import re
print("Processing <処理中>...")
# Input data files are available in the read-only "../input/" directory
# For example, running this (by clicking run or pressing Shift+Enter) will list all files under the input directory
train = pd.read_csv("../input/nlp-getting-started/train.csv")
test = pd.read_csv("../input/nlp-getting-started/test.csv")

## kwの欠損値対処
train = train.fillna({"keyword":0,
                     "location":0})
test = test.fillna({"keyword":0,
                   "location":0})
                   
# train_id = train["id"]
# train_kw = train["keyword"]
# train_loc = train["location"]
# train_txt = train["text"]
# train_tgt = train["target"]

# test_id = train["id"]
# test_kw = train["keyword"]
# test_loc = train["location"]
# test_txt = train["text"]

test_id = test["id"]
test_kw = test["keyword"]
# test_loc = test["location"] # 使用しなかった
# test_txt = test["text"] # 使用しなかった
                   

# print("freq : \n", keyword_df.value_counts())
keyword_dic = {}
kw_total_dic = {}
num = 1
for word, id_, add_score in zip(train["keyword"], train["id"], train["target"]):
    ## 割合計算のための総数（分母）
    if word != 0: # 欠損値Nanを0にしたので、それをカウントされないようにする
        try:
            kw_total_dic[word] += num
        except KeyError:
            kw_total_dic[word] = num

        ## 割合計算のための出現回数（分子）
        if add_score == 1:
            try:
                keyword_dic[word] += add_score
            except KeyError:
                keyword_dic[word] = add_score

# kw_digital_dic = {key: 0 for key in kw_total_dic.keys()}
kw_digital_dic = {}
for word in train["keyword"]:
    if word != 0:
        ## keyword_dic[word]には存在しないがkw_total_dic[num]に存在するもの同士の演算　という矛盾の例外処理
        try:
            kw_digital_dic[word] = round(keyword_dic[word] / kw_total_dic[word], 3) # 割合を求める
    #         kw_debug_dic = kw_digital_dic.copy() # このブロック間のifとelseをコメントアウトすれば割合を見れられる。
            ## 正解率30%以上のキーワードのみ保存 or 未満は0扱い
            if round(keyword_dic[word] / kw_total_dic[word], 3) < 0.4:
                kw_digital_dic[word] = -1
    #           del kw_digital_dic[word] #消したら後で書き込むときに不便かも
            else:
                kw_digital_dic[word] = 1 # 任意の割合を越えた場合、バリューを1にする。

        except KeyError:
            kw_digital_dic[word] = -1


# print("digital:\n", kw_digital_dic)
# print("kw_debug_dic: \n", kw_debug_dic)


# 内包表記は左側のforから処理される。ただし、一番左は最後なのに注意。
# remove_lst = ["the", "that", "this", "with", "like", "from", "have", "&amp;", ] # その他、5h1hなど.正規表現で大文字を全部小文字にする🚩
# word = [word for sentence in train["text"] for word in sentence.split() if (len(word)) >= 4 and (word not in remove_lst)] # 4文字以上を取り出す。
# attention_lst = ["disaster", "catastrophe"]
# とりあえず形態素解析で名詞だけ抽出してみる。次は感情、動詞とか？


## 🚩target=1のとき頻度が大きい単語を災害指定単語とする。locationなどと共通集合となったらデータ除去の下限を緩和する。
loc_num_dic = {} # locは文字列型
id_loc_dic = {} # locはリスト型
# 区切り文字をリストに追加
separators_lst = [",", "-", "|", "||", "&", "/", "!", "?"]
num = 0
for loc, id_, add_score in zip(train["location"], test_id, train["target"]):
    if (loc != 0) and (add_score == 1) and (loc != re.search("\d+", loc)):
        loc = loc.lower().replace(".", "")
    
        # 括弧で囲まれた文字列を削除
        loc = re.sub(r'\([^)]*\)', '', loc)

        ## 正規表現のパターンを作成
        pattern = "|".join(map(re.escape, separators_lst))
        # re.escape(文字列)はエスケープシーケンスを文字列として取り扱うための処理。separatorsはリストなので直接は使えない。
        # map(関数, リストorイテラブル)で、関数をリスト等に適用させた新しいリストを生成。
        
        ## 正規表現で区切り文字が含まれているかチェック
        if re.search(pattern, loc):
            parts_lst = re.split(pattern, loc)
            for loc_part in parts_lst:
                
                ## loc_partが全て数字の場合を除くための例外処理。
                try:
                    if int(loc_part):
                        pass
                    
                except ValueError:
                    ## 文頭と文末のスペース削除
                    if loc_part != "":
                        if loc_part[0] == " ":
                            loc_part = loc_part[1:]
                    if len(loc_part) > 1:
                        if loc_part[-1] == " ":
                            loc_part = loc_part[:-1]
                            
                    ## "場所（リストではない）"・"場所の数"のペアで保存する辞書にキーがすでにある場合とない場合での例外処理
                    try:
                        loc_num_dic[loc_part] += add_score
                    except KeyError:
                        loc_num_dic[loc_part] = add_score
                        
                    if loc_part != '': # なんかloc_partが''になることがあるので除去
                        ## "id"・"場所（リスト）"のペアで保存する辞書にキーがすでにある場合とない場合での例外処理
                        try:
                                id_loc_dic[id_].append(loc_part)
                        except KeyError:
                            id_loc_dic[id_] = [] # バリュー（個々のloc）を格納するためのリスト
                            id_loc_dic[id_].append(loc_part)
        else:
            try:    
                loc_num_dic[loc] += add_score
            except KeyError:
                loc_num_dic[loc] = add_score                            
            try:
                id_loc_dic[id_].append(loc)
            except KeyError:
                id_loc_dic[id_] = []
                id_loc_dic[id_].append(loc)

# print("loc_num_dic:\n", loc_num_dic)
# print("id_loc_dic: ", id_loc_dic)

loc_num_dic = {loc: 1 if num >= 2 else -1 for loc, num in loc_num_dic.items()} # 指定回数以上出現したら,numを1に更新。そうじゃなかったら-1に更新。今は2回以上出現している場所(location)に限っている。
        
id_loc_digital_dic = dict.fromkeys(test_id, 0) # キーだけ（idだけ）キーを流用した辞書作成。初期バリューは第二引数0に設定。    
## idと0,1値を対応させる
for id_, loc_lst in id_loc_dic.items():
    for loc in loc_lst:
        if loc_num_dic[loc] == 1:
            ## idとそのnumをペアに持つ辞書に1を保存。id_loc_digital_dicにはデフォルトバリューを0に設定したので、含まれていたら1に更新するだけで良い。
            id_loc_digital_dic[id_] = 1 
        elif loc_num_dic[loc] == -1:
            id_loc_digital_dic[id_] = -1 # 頻度が小さくて切り捨てられた場所(loc)を格納。

# print("id_loc_dic(digital):", id_loc_dic)
# print("id_num_dic:", id_num_dic)
# print("id_len: ", len(test_id))
# print("dic_len: ", len(id_loc_dic))
# print("id_loc_digital_dic:", id_loc_digital_dic)


import nltk
from nltk.tokenize import word_tokenize

text_noun_dic = {}
id_word_dic = {id_: [] for id_ in test_id} # あらかじめ空リストを初期値として作っておいた
# print("###", id_word_dic)
no_need_lst = ["http", "https", "amp", "@"] # 🚩
for id_, sentence, add_score in zip(test_id, train["text"], train["target"]):
    tokens = nltk.word_tokenize(sentence)
    tagged_lst = nltk.pos_tag(tokens)
    
    for word, pos in tagged_lst:
        # 名詞,つまりNNのみ取得
        if (pos == "NN") and (word not in no_need_lst) and (add_score != 0):
            try:
                text_noun_dic[word] += add_score # row_idxとwordを紐づけたい...辞書型にするとか？
            except KeyError:
                text_noun_dic[word] = add_score
                
            ## idと単語の組み合わせを保存
            id_word_dic[id_].append(word)

text_noun_dic = {word: 1 if num >= 2 else -1 for word, num in text_noun_dic.items()} # 頻度の小さい単語の切り捨て.今は取り合えず2以上にしてる

id_word_digital_dic = dict.fromkeys(test_id, 0)
## idと0,1とを対応させる
for id_, word_lst in id_word_dic.items():
# for id_, word_lst in zip(test_id, id_word_dic.values()):
    for word in word_lst:
        if text_noun_dic[word] == 1:
            id_word_digital_dic[id_] = 1
        elif text_noun_dic[word] == -1:
            id_word_digital_dic[id_] = -1


## 前処理後のリスト
kw_digital_lst = [kw_digital_dic.get(kw, 0) for kw in test_kw] # kwが存在すればその値を返し、存在しなければ欠損値として0を返している。-1は切り捨てられたキーワード。
loc_digital_lst = list(id_loc_digital_dic.values())
word_digital_lst = list(id_word_digital_dic.values())
# print("id: ", len(test_id))
# print("kw: ", len(kw_digital_lst))
# print("loc: ", len(loc_digital_lst))
# print("text: ", len(word_digital_lst))


## 確認debug用データフレーム
# preprocessing = pd.DataFrame(
#                     data = {"<id>": test_id,
#                             "<keyword>": kw_digital_lst,
#                            "<location>": loc_digital_lst,
#                            "<text>": word_digital_lst,
#                             "true_target":train_tgt
#                            }
# )
# print("🚩preprocessing_dataFrame:\n", preprocessing[30:50])

prepared_lst = []

for kw, loc, word in zip(kw_digital_lst, loc_digital_lst, word_digital_lst):
    ## kwの判定
    if kw != -1 and word != -1 and (kw != 0 or word != 0): # kwとwordが切り捨て値ではないかつ欠損値でもない場合
        prepared_lst.append(1)
    ## locの判定
    elif loc: # loc=1のとき
        prepared_lst.append(1)
    ## wordの判定
    elif kw == 0 and loc == 0 and word == 1: # 両方とも欠損値のとき、wordが1ならば
        prepared_lst.append(1)
    else:
        prepared_lst.append(0)

finalize_df = pd.DataFrame({
                    "id":test_id,
                    "target":prepared_lst
})
print("finalize_df:", finalize_df)

finalize_df.to_csv("disaster_tweet.csv", index = False)


import os
for dirname, _, filenames in os.walk('/kaggle/input'):
    for filename in filenames:
        print(os.path.join(dirname, filename))
## 32番目からキーワードと場所
## targetは0から14行(id=20)以降0
## 🚩text反省　精度が悪い。名詞のみでやってみたが、flood,floodedやfloodingは何判定？動詞？ 形態素解析に追加した方が良いかも。
### 重み付け基準：　location > keyword > text
### locationがあったら問答無用でtrue, keywordはtextも1ならtrue, textはそれ単体のときのみ(kw,locが0のとき)採用
print("Process complete <プログラム終了>")

# You can write up to 20GB to the current directory (/kaggle/working/) that gets preserved as output when you create a version using "Save & Run All" 
# You can also write temporary files to /kaggle/temp/, but they won't be saved outside of the current session