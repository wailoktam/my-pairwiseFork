# coding: utf-8

import pickle
import os
import sys

reload(sys)
sys.setdefaultencoding("utf-8")

dataSet = ['train', 'dev', 'test'] # pickleされているquestionデータの名前。train/dev/testがおすすめです。
answer = pickle.load(open('answers')) # pickleされているanswerデータの名前。
vocaDic = pickle.load(open('word')) #　pickleされているvoca dictionaryデータの名前。
revVocaDic = pickle.load(open('revWord')) # pickleされているreversed voca dictionaryデータの名前。

targets = ['who', 'when', 'where']
cand = {'who':'william', 'when':'1923', 'where':'florida'} # targetsに合わせて、自動的に置換する単語を入れてください。

def process(target, targetNum):
    voca = {'unk'} # GloVeを使う場合、unknownトークンを処理するため、unkを初めから入れておきます。
    # また、この変数はpairwiseで使われる辞典を作るために使われます。重複処理のためにsetを使います。

    os.mkdir(target) # targetの名前でわかるように、targetを名前にした新しいdirectoryを作ります。

    for data in dataSet:
        question = pickle.load(open(data))

        os.mkdir(target + '/' + data) # pairwiseで使うデータはtrain, dev, testのデータが別々のdirectoryに入っていなければならないので、こちらでその処理をします。
        
        atok = [] # question文のデータがここに入ります。
        btok = [] # answer文のデータがここに入ります。
        boundary = ['0',] # どこまでが一つのquestion, answerのセットなのかに関してのデータです。0から始まるので、最初から0を入れておきます。
        id = [] # question, answerのセットを識別するためのidが入ります。
        numrels = [] # 一つのセットに正解が何個あるのか、についてのデータが入ります。
        sim = [] # 同じラインにあるbtokの文が正解かどうかに関してのデータが入ります。

        b = 0 # boundaryは累積値、accumulate valueなので、それを計算するための変数を作っておきます。

        for q in question:
            if targetNum != q['question'][0]: # 下にありますが、targetNumはtargetのdictionary indexになります。
                continue # 特定のquetsion term, つまりwho, whereといったものだけのデータセットを作るためのif文です。
                # このif文を削除することだけで、fullのデータセットが作れます。

            text = [] # 後で、ここに自然言語の原文が入ります。

            b += len(q['good'] + q['bad']) # boundaryの計算です。

            boundary.append(str(b)) # 計算した結果を入れます。
            numrels.append(str(len(q['good']))) # 正解の数だけ計算すればnumrelのデータになります。

            for qText in q['question']:
                if qText == targetNum and 'Orig' not in target:
                    # 下でまた説明しますけど、一度でcandを使ったデータ、使わなかったデータを同時に作るために、
                    # whoOrig, whereOrig, whenOrigというtargetデータも使っています。ここはそれを処理するためのif文です。
                    voca.add(cand[target])
                    # who/when/whereのどれで、またOrigがない、つまりcandを使う場合なので原文の代わりにcandの単語を入れておきます。
                    text.append(cand[target])
                    # そしてそのcandの単語の原文をそのままtextにも入れておきます。
                else:
                    voca.add(vocaDic[qText])
                    # Origがあるか、または他の単語なので原文を探し出して、辞典に入れておきます。
                    text.append(vocaDic[qText])
                    # そしてそのままtextにも入れておきます。
                # このfor文はquestion文全体にかけられているので、この処理だけでquestionの原文をtextに入れておくことができます。

            text = ' '.join(text).strip() # listだったtextをstringに変えておきます。

            order = q['good'] + q['bad'] # answerのidのlistを全部足します。
            order.sort() # そしてsortします。これはエラーの可能性を事前に防ぐためです。

            for i, o in enumerate(order):
                atok.append(text) # answerの数だけquestionは繰り返されます。そのため、a.toksとb.toksのラインの数は同じでなければなりません。

                aText = [] # answerの原文がここに入ります。
                for a in answer:
                    if a['id'] == o: # 全部のanswerデータの中で、idが一致するものを探します。もっと早い方法があるはずだとは思いますが…
                        for t in a['text']:
                            voca.add(vocaDic[t])
                            aText.append(vocaDic[t])
                        break # 欲しいanswerが見つかったら、原文を取り出してbreakします。

                btok.append(' '.join(aText).strip()) # answerをb.toksに入れておきます。

                tempId = 'Q' + str(q['question_id']) + '-D' + str(q['question_id']) + '-' + str(i)
                # idの形式がどんな基準で決められていたかは記述されてなかったので、とりあえず形を似せて作りました。とりあえずバグなくこれでも起動します。
                if o in q['good']:
                    sim.append('1') # 正解だったら1を入れます。
                else:
                    sim.append('0') # 不正解なら0を入れます。
                id.append(tempId) # idも忘れずに入れておきます。
            # 今までの処理を、データ全体で行います。


        # ループが終わると、変数に入っているデータをファイルに出力します。
        # 下のファイルはtrain, dev, testのdirectoryごとに作られることになります。

        writer = open('./' + target + '/' + data + '/a.toks', 'w')
        writer.write('\n'.join(atok))
        writer.close()

        writer = open('./' + target + '/' + data + '/b.toks', 'w')
        writer.write('\n'.join(btok))
        writer.close()

        writer = open('./' + target + '/' + data + '/boundary.txt', 'w')
        writer.write('\n'.join(boundary))
        writer.close()

        writer = open('./' + target + '/' + data + '/id.txt', 'w')
        writer.write('\n'.join(id))
        writer.close()

        writer = open('./' + target + '/' + data + '/numrels.txt', 'w')
        writer.write('\n'.join(numrels))
        writer.close()

        writer = open('./' + target + '/' + data + '/sim.txt', 'w')
        writer.write('\n'.join(sim))
        writer.close()

    # voca、つまり辞典はtrain, dev, test全部で使われるので、一人だけ最後に処理されます。
    voca = list(voca)

    writer = open('./' + target + '/vocab.txt', 'w')
    writer.write('\n'.join(voca))
    writer.close()

if __name__ == '__main__':
    for target in targets:
        targetNum = revVocaDic[target] # targetNumの計算はここでやっておきます。

        process(target + 'Orig' , targetNum) # これを省略すると、candを使ったデータだけが作られます。
        process(target, targetNum) # これを省略すると、candを使わない、つまりオリジナルのデータだけが作られます。
