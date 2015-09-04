# -*- coding: UTF-8 -*-
import os
import codecs
import re
import json
import time
import sys
vowels = u"уеыаоэяиюё"
delete_trash = re.compile(u'[…()",\.?!*:;\-—»«0123456789]') 
user_dictionary_dir = u"accent1.dic"
user_dictionary_codec = "cp1251"

def write_data (path, data):
    json_data = json.dumps(data, ensure_ascii=False, indent=1)  
    json_file = codecs.open (path, 'w', 'cp1251')
    json_file.write (json_data)
    json_file.close()

def read_data (path):
    data_file = codecs.open(path, 'r', 'utf-8')
    data = json.load(data_file)
    data_file.close()
    return data

def return_paths(name):
    return os.listdir(name)

def read_file(path):
    f = codecs.open(path, "r", "utf-8")
    

def main():

    open_dict = codecs.open(user_dictionary_dir, "r", user_dictionary_codec)
    dictionary = complect_dict(open_dict)
    open_dict.close()
    new_dictionary = u""
    scanned = {}
    interesting = {}
    
    f_type, name = input_info()
    files = []

    is_author = re.compile(u"<author.*?")
    is_div = re.compile(u"<div.*?")
    is_not_div = re.compile(u"</div>")
    is_title = re.compile(u"<title.*?")
    is_string = re.compile(u"[А-Яа-я]\t")
    is_tab = re.compile(u"\t")
    
    author = re.compile(u"author=\".*\"?")
    nick = re.compile(u"nick=\".*\"?")
    s_id = re.compile(u'id="[0-9]*"?')
    url = re.compile(u"url=\".*\"?")
    title = re.compile(u"title=\".*\"?")
    quotes = re.compile(u"\".*\"?")

    curr_author = u""
    curr_nick = u""
    curr_id = u""
    curr_url = u""
    curr_title = u""

    direct_num = 1
    splitter = u""
    if f_type == u"dir":
        files = return_paths(name)
        splitter = u"\\"
    elif f_type == u"file":
        files = [u""]
    direct_num = len(files)
    counter = 0
    counted = 0
    start = time.time()
    print "Started at ", time.ctime(), '\n\n'
    for i in files:
        counter += 1
        counted += 1
        if counter == 100:
            counter = 0
            n_sec = ((time.time() - start)/counted)*(direct_num - counted)
            n_min = n_sec/60.0
            n_hr = n_min/60.0
            sys.stdout.write(str(n_hr) + ' hr ||'+ str(n_min) + ' min ||' + str(n_sec) + ' sec || >> ' + str(direct_num - counted) + ' files' + '\n')
            
        text_file = codecs.open(name + splitter + i, "r", "utf-8")
        stanza_info = {}
        div = False
        for j in text_file:
            if is_author.search(j):
                curr_author = author.findall(j)[0].strip(u"\"")
                curr_nick = nick.findall(j)[0].strip(u"\"")
            elif is_div.search(j):
                div = True
                curr_id = quotes.findall(s_id.findall(j)[0])[0].strip(u"\"")
                curr_url = url.findall(j)[0].strip(u"\"")
            elif is_title.search(j):
                curr_title = title.findall(j)[0].strip(u"\"")
            elif is_not_div.search(j):
                div = False
            elif div and is_string.search(j):
                string = scan_string(j)

                
                for word in string:
                    if  word[0]:
                        if word[0] not in scanned:
                            scanned.update({word[0]:[[word[1]], [word[2]], [curr_id]]})
                        else:
                            if word[1] not in scanned[word[0]][0]:
                                scanned[word[0]][0].append(word[1])
                                scanned[word[0]][1].append(word[2])
                                scanned[word[0]][2].append(curr_id)

    print "\n\nSaving started at ", time.ctime(), "\n\n"
    for i in scanned:
        if len(scanned[i][0]) == 1:
            if i not in dictionary: 
                new_dictionary += constr_dict_string(i, scanned[i])
        else:
            interesting.update({i:scanned[i]})


    write_data(name+u"_quest.json", interesting)   

    open_dict = codecs.open(user_dictionary_dir, "r", user_dictionary_codec)
    dictionary = open_dict.read()
    open_dict.close()
    res_dict = dictionary + new_dictionary
    open_dict = codecs.open(user_dictionary_dir, "w", user_dictionary_codec)
    open_dict.write(res_dict)
    open_dict.close()

    print "Completed at ", time.ctime()

def constr_dict_string(word, info):
    res = u""
    #print info
    res = res + u"\r\n" + word + u"\t" + info[0][0] + info[1][0]
    return res
            
def input_info():
    print u"Инструкция!"
    print u"Введите путь к файлу или папке (используя \\)."
    print u"Если введен путь к папке, будет предпринята попытка обработать все файлы из нее."
    print u"Конец инструкции!\n"
    is_end = False
    new = input_path()
    if file_type(new) == u"file":
        return u"file", new
    elif file_type(new) == u"dir":
        return u"dir", new
    else: return False
    
def input_path():
    line = raw_input(u"Введите путь к файлу: ")#.decode('cp1251')
    #line = u"c:\\daniil\\stihi_ru_clean_m2"#u"test1"
    return line.lower()
def file_type(path):
    split_path = path.split(u"\\")
    if u"." in split_path[-1]:
        return u"file"
    else:
        return u"dir"

def scan_string(string): ###Правильность
    string_info = []
    string = string.split(u"\t")[0]
    words = string.split()
    is_capital = None
    for i in words:
        word = clear_word(i)
        stress = stress_syll(word)
        if word and word[0] != word[0].lower():
            is_capital = u"!"
        else:
            is_capital = u""
        word = word.replace(u"`", u"")
        string_info.append([word.lower(), unicode(stress), is_capital])
    return string_info
            
        
def clear_word(word):
    global symbs
    return delete_trash.sub(u"", word)
    

def stress_syll(word):
    global vowels
    parts = word.split(u"`")
    if len(parts) < 2:
        return 0
    syll_num = 0
    for i in parts[0]:
        if i in vowels:
            syll_num += 1
    if not syll_num:
        return 1
    return syll_num
    
def complect_dict(path):
    dictionary = {}
    for i in path:
        is_upper = u""
        if len(i) > 2 and i[0] != u"#" and len(i.split()) > 1 and not u"(" in i and not u")" in i: #потому что информативная строка словаря содержит слово из >0 букв, таб и номер ударного слога
            parts = i.split()
            if u"!" in parts[1]:
                is_upper = u"!"
            dictionary.update({parts[0]:[parts[1].split(u","), is_upper]})
            
        elif len(i) > 2 and i[0] != u"#" and len(i.split()) > 1 and u"(" in i and u")" in i:
            parts = i.split()
            if u"!" in parts[1]:
                is_upper = u"!"
            pr_string = parts[0].split(u"(")
            pr_string[1] = pr_string[1].replace(u")", u"")
            ends = pr_string[1].split(u"|")
            for j in ends:
                for k in j.split(u"/"):
                    dictionary.update({pr_string[0]+k : [parts[1].split(u","), is_upper]})
    return dictionary

if __name__ == '__main__':
    main()
