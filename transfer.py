#!/usr/bin/env python

import os
import xml.dom.minidom as xmldom

def visit_all_dirs_and_files(directory, convert_list):
    for root, dirs, files in os.walk(directory):
        for filename in files:
            if '@eaDir' in root:
                continue
            _, ext = os.path.splitext(filename)
            #设置视频文件格式后缀，缺少的自行增加
            if ext.lower() in ['.mkv', '.mp4', '.rmvb', '.avi', '.wmv']:
                vsmeta_path = os.path.join(root, filename + '.vsmeta')
                if not os.path.exists(vsmeta_path):
                    nfo_path = os.path.join(root, os.path.splitext(filename)[0] + '.nfo')
                    convert_list.append(nfo_path)
                    if os.path.exists(nfo_path):
                        try:
                            action(nfo_path, vsmeta_path)
                        except Exception as e:
                            print(e)
            #用于检查缺少的视频文件格式后缀。需要忽略的文件格式后缀自行增加
            elif ext.lower() not in ['.vsmeta', '.jpg', '.nfo', '.srt', '.ass', '.png']:
                print('Unrecognized file:', os.path.join(root, filename))

def action(nfo_path, target_path):
    doc = xmldom.parse(nfo_path)
    title = doc.getElementsByTagName('title')[0].firstChild.nodeValue
    plot = doc.getElementsByTagName('plot')[0].firstChild.nodeValue if doc.getElementsByTagName('plot') else ''
    level = '9+'
    date = doc.getElementsByTagName('premiered')[0].firstChild.nodeValue if doc.getElementsByTagName('premiered') else '2023-01-01'
    rate = doc.getElementsByTagName('rating')[0].firstChild.nodeValue if doc.getElementsByTagName('rating') else '0'
    cla = [node.firstChild.nodeValue for node in doc.getElementsByTagName('genre')]
    act = [node.firstChild.nodeValue for node in doc.getElementsByTagName('name')]
    direc = [node.firstChild.nodeValue for node in doc.getElementsByTagName('director')]

    with open(target_path, 'wb') as output:
        output.write(bytes([8, 1, 18]))
        output.write(bytes([lenOfEncode(title)]))
        output.write(title.encode('utf-8'))
        output.write(bytes([26, lenOfEncode(title)]))
        output.write(title.encode('utf-8'))
        output.write(bytes([34, lenOfEncode(title)]))
        output.write(title.encode('utf-8'))
        output.write(bytes([40, 220, 15, 50]))

        output.write(bytes([lenOfEncode(date)]))
        output.write(date.encode('utf-8'))
        output.write(bytes([56, 1, 66]))
        plotlen = lenOfEncode(plot)
        if plotlen < 80:
            output.write(bytes([plotlen]))
        else:
            output.write(bytes([plotlen % 128 + 128]))
            output.write(bytes([plotlen // 128]))
        output.write(plot.encode('utf-8'))
        output.write('J'.encode('utf-8'))
        output.write(bytes([4]))
        output.write('null'.encode('utf-8'))

        cals = 0
        for c in cla:
            cals += 2 + lenOfEncode(c)

        for a in act:
            cals += 2 + lenOfEncode(a)

        for d in direc:
            cals += 2 + lenOfEncode(d)

        output.write('R'.encode('utf-8'))
        if cals < 80:
            output.write(bytes([cals]))
        else:
            output.write(bytes([cals % 128 + 128]))
            output.write(bytes([cals // 128]))

        for a in act:
            output.write(bytes([10]))
            output.write(bytes([lenOfEncode(a)]))
            output.write(a.encode('utf-8'))

        for d in direc:
            output.write(bytes([18]))
            output.write(bytes([lenOfEncode(d)]))
            output.write(d.encode('utf-8'))

        for c in cla:
            output.write(bytes([26]))
            output.write(bytes([lenOfEncode(c)]))
            output.write(c.encode('utf-8'))

        output.write('Z'.encode('utf-8'))
        output.write(bytes([lenOfEncode(level)]))
        output.write(level.encode('utf-8'))
        output.write(bytes([96]))
        output.write(bytes([int(float(rate) * 10)]))

def lenOfEncode(string):
    return len(string.encode('utf-8'))

if __name__ == '__main__':
    #电影、电视文件路径。如果有NasTools配合，建议设置为硬链根目录
    directory = r'/volume1/video/Links/'
    convert_list = []
    visit_all_dirs_and_files(directory, convert_list)

    print('success ' + str(len(convert_list)) + ' files')
    #for item in convert_list:
    #    print(item)
