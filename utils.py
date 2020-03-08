import os
import shelve


def time_convert(m):
    """
    将offset转化为 hh:mm:ss,ms 格式
    :param m:
    :return:
    """
    hh, mm, ss, ms = 0, 0, 0, m
    ss, ms = divmod(ms, 1000)
    mm, ss = divmod(ss, 60)
    hh, mm = divmod(mm, 60)
    return '%02d:%02d:%02d,%d' % (hh, mm, ss, ms)


def gen_srt(file_name):
    # 生成srt字幕文件
    path, name = os.path.split(file_name)
    with shelve.open('lines.db') as db, open('Srt/' + name + '.srt', 'w+', encoding='utf-8') as srt:
        # 每个字典提取一行, 获取开始时间, 结束时间和行号
        for i, record in enumerate(db[file_name]['lines']):
            # 写行号
            bg = record['bg'] + db[file_name]['start']
            ed = record['ed'] + db[file_name]['start']
            index = str(i + 1)
            timeline = time_convert(bg) + ' --> ' + time_convert(ed)
            words = record['words']
            s = ''.join(index + '\n' + timeline + '\n' + words + '\n\n')
            print(s)
            srt.write(s)


def merge_srts(filenames):
    """
    合并多个字幕分段文件到一个文件中
    :param filenames:
    :return:
    """
    with open('Video/main.srt', 'w', encoding='utf-8') as full:
        for file in filenames:
            with open(file, 'r', encoding='utf-8') as part:
                data = part.read()
                full.write(data)


audios = [f'Srt/part_sound_{i}.wav.srt' for i in range(15)]
# for audio in audios:
#     gen_srt(audio)

merge_srts(audios)