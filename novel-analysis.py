# 注意，以下适用版本为python 3.6.4，其他版本可能会出现语法兼容问题
# 由于大量测试的需要，我关闭了大部分print，有需要的话可以重新打开
# 程序主干在最下方

__author__ = '1038761793@qq.com'

import re
import jieba
import os
import time


def indexOf(parent, child):
    # 由于自带的index匹配失败会抛出ValueError，因此写了这么个语法糖
    # 匹配成功返回index, 失败返回-1

    try:
        i = parent.index(child)
    except ValueError:
        i = -1
    return i


def get_all_file_path(f_dir):
    # 注意，输入必须为目录名字符串
    # 注意，目录名不得含有.字符，否则会错误识别为文件
    # 注意，后代文件必须带有后缀名，否则无法识别
    # 仅适用windows，因linux分隔符与windows不同
    # 返回值为该目录下所有后代文件的地址组成的列表[ path, ... ]

    # print('正在获取 %s 目录下所有文件路径...' % f_dir)
    paths = []
    f_items = os.listdir(f_dir)
    for f_name in f_items:
        f_path = f_dir + '/' + f_name
        if re.search(r'\.[a-zA-Z0-9]+$', f_name, flags=0):
            paths.append(f_path)
        else:
            paths.extend(get_all_file_path(f_path))
    return paths


def read_file(file_path):
    # 输入文件路径
    # 返回utf8字符串

    # print('读取文件 %s 中...' % file_path)
    f = open(file_path, mode='r', encoding='utf-8')
    txt = f.read()
    f.close()
    return txt


def redup(word_list, freq_list):
    # 对jieba.lcut分词得到的列表list进行去重，去掉词语的所有子集
    # 返回值格式为[ [词, 词频], ... ]
    # 原则上仅用于fenci()函数中处理数据

    # print('对分好的词去重中...')
    total = len(word_list)
    for fir in word_list:
        for sec in word_list:
            if fir == sec:  # 过滤掉自己跟自己匹配（注意，这里由于函数fenci()中已执行了去重，所以才能这么比较，如果存在重复数据，那整个函数都要改动
                continue
            if indexOf(fir, sec) >= 0:
                i = word_list.index(sec)
                word_list.remove(sec)
                freq_list.remove(freq_list[i])
                break
            elif indexOf(sec, fir) >= 0:
                i = word_list.index(fir)
                word_list.remove(fir)
                freq_list.remove(freq_list[i])
                break
    return [[word_list[i], freq_list[i]] for i in range(len(word_list))]


def get_freq(jieba_list):
    # 输入jieba.lcut得到的list，返回{词: 词频, ...}格式的dict
    # 之所以返回dict, 是便于计算词频
    # 原则上仅用于fenci()函数中处理数据

    # print('获取词频中...')
    temp = {}
    for word in jieba_list:
        if not word:
            continue
        if word in temp:
            temp[word] += 1
        else:
            temp[word] = 1
    return temp


def fenci(txt, reverse=False, limit=0, filter=[]):
    # 返回一个列表 [ [词, 词频], ...]

    # print('分词中，根据文本多寡，可能需要较长时间...')
    pieces = jieba.lcut(txt, cut_all=True)

    word_list = []
    freq_list = []
    freq_dict = get_freq(pieces)
    for piece in freq_dict:  # 保存到另一个数组
        if freq_dict[piece] >= limit and piece not in filter:
            word_list.append(piece)
            freq_list.append(freq_dict[piece])

    result_list =redup(word_list, freq_list)
    result_list = sorted(result_list, key=lambda i: i[1], reverse=reverse)
    return result_list


def paint(data_list):
    # 输入[ [词, 词频], ...]格式的数据（由fenci()生成），生成canvas图

    # print('画画中...')
    global root
    canvas_width = 800
    canvas_height = 800
    max_h = max(data_list, key=lambda item: item[1])[1]
    w = canvas_width/len(data_list)
    h = canvas_height/max_h
    canvas = tkinter.Canvas(root,width=canvas_width, height=canvas_height, background='white')
    canvas.pack()
    for i in range(len(data_list)-1):
        x_0 = w * i
        y_0 = canvas_height - h * data_list[i][1]
        x_1 = w * (i + 1)
        y_1 = canvas_height - h * data_list[i+1][1]
        canvas.create_line(x_0, y_0, x_1, y_1, fill='red')


def analysis(sentence, words):
    # 输入一个句子和[ [词, 词频], ... ]列表（由fenci()生成）
    # 返回按位置升序排列的[ [词, 位置], ...]列表（此处位置是该词处于该句子中的位置）

    result_list = []
    for word in words:
        i = indexOf(sentence, word[0])
        if(i >= 0):
            result_list.append([word[0], i])
    return sorted(result_list, key=lambda a: a[1])


def split_to_sentence(txt, limit=7):
    # 将文本字符串分割为句子
    # 返回长度超过 limit 的句子组成的列表[ sentence, ... ]

    # 这儿有个坑，不能直接return filter(...)，这样返回的是一个filter Object，不是list...
    return list(filter(lambda a: len(a)>=limit, re.split('[ +,+\.+\'+\"+!+\?+\xa0+\t+\r+\n+，+。+‘+’+“+”+！+？+]', txt)))


def get_pattern(txt, filter=[]):
    '''
        输入文本字符串，返回一个模式列表，模式为：
        [
            [ [词, 位置], ... ],  # 这是一个句子中高频词位置排列信息列表
            ...
        ]
    '''

    words = fenci(txt, limit=400, filter=filter)
    sentences = split_to_sentence(txt)
    result_list = []
    # print('获取语句模式中...')
    flag = 1  # 纯粹为了提示<程序处于运行状态>，下面每循环1000次给一个print
    for sentence in sentences:
        flag += 1
        if flag%1000 == 0:
            pass  # print('%d 分析文本结构中...' % int(flag/1000))
        temp = analysis(sentence, words)
        if len(temp) > 1:
            result_list.append(temp)
    return result_list


def match_sentence(sentence, pattern):
    '''
    :param sentence: 待分析的句子
    :param pattern: get_pattern返回的模式的子项（即 某一种句型 的模板）
    :return: Boolean 该句子是否符合该模式
    '''

    flag = True
    prev = -1
    for p in pattern:
        cur = indexOf(sentence, p[0])
        if cur < 0 or cur < prev:
            flag = False
            break
        else:
            flag = True
            prev = cur
    return flag


def match_pattern(txt, patterns):
    # 将所有待检测文本分割成句子，依次执行模式match_sentence()匹配
    # 返回 成功匹配句子数 与 句子总数 的商

    # print('文本匹配中...')
    sentences = split_to_sentence(txt)
    matched = 0
    total = len(sentences)
    for sentence in sentences:
        for pattern in patterns:
            if match_sentence(sentence, pattern):
                matched += 1
                # print('句子已成功匹配：%d/%d （匹配失败无提示）' % (matched, total))
                break
    return matched/total


def is_continue(tips=''):
    c = input('请输入 %s：\n1.直接回车将返回True\n2.输入小数点.将返回False\n3.输入其他则将返回您所输入...\n' % tips)
    if c == '':
        return True
    elif c == '.':
        return False
    else:
        return c


print('程序开始：', time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
paths = get_all_file_path('./books')
origin_paths = paths[0:-1]
test_paths = paths[-1:]

for op in origin_paths:
    for tp in (test_paths + [op]):
        origin_txt = read_file(op)[0:100000]
        filters = []
        ''' 
        print(fenci(origin_txt, limit=1000, filter=[]))
        c = is_continue('您希望过滤的词，一个词一个Enter')
        while c:
            filters.append(c)
            c = is_continue('您希望过滤的词，一个词一个Enter')
        '''
        origin_patterns = get_pattern(origin_txt, filter=filters)

        test_txt = read_file(tp)[400000:410000]
        try:  # 我在大量测试（100本源文本）时发现，出现了某一本小说在模式匹配时会抛出错误，暂时没找到原因，因此先用try.except.块包裹着
            print('{\'origin_txt\': \'%s\',\'test_txt\': \'%s\',\'result\':%.4f},' % (op, tp, match_pattern(test_txt, origin_patterns)))
        except:
            print('{\'origin_txt\': \'%s\',\'test_txt\': \'%s\',\'result\':\'error\'},' % (op, tp)))

print('程序结束：', time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
