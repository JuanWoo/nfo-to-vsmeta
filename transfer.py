#!/usr/bin/env python

import os
import xml.dom.minidom as xmldom
import base64
import hashlib
import time
import io
from PIL import Image

def checkAllFiles(directory, convertList, poster, fanart):
    for root, dirs, files in os.walk(directory):
        for filename in files:
            if '@eaDir' in root:
                continue
            _, ext = os.path.splitext(filename)
            if ext.lower() in ['.mkv', '.mp4', '.rmvb', '.avi', '.wmv', '.ts']:  #设置视频文件格式后缀，缺少的自行增加
                vsmetaPath = os.path.join(root, filename + '.vsmeta')
                #以下两行代码用于删除已有vsmeta文件
                #if os.path.exists(vsmetaPath):
                #    os.remove(vsmetaPath)
                posterPath = os.path.join(root, poster)
                fanartPath = os.path.join(root, fanart)
                if not os.path.exists(vsmetaPath):
                    nfoPath = os.path.join(root, os.path.splitext(filename)[0] + '.nfo')
                    convertList.append(nfoPath)
                    if os.path.exists(nfoPath):
                        try:
                            action(nfoPath, vsmetaPath, posterPath, fanartPath)
                        except Exception as e:
                            print(e)
            elif ext.lower() not in ['.vsmeta', '.jpg', '.nfo', '.srt', '.ass', '.ssa', '.png', '.db']:  #用于检查缺少的视频文件格式后缀。需要忽略的文件格式后缀自行增加
                print('Unrecognized file:', os.path.join(root, filename))

def action(nfoPath, target_path, posterPath, fanartPath):
    
    doc = xmldom.parse(nfoPath)
    title = getNode(doc, 'title', '无标题')
    sorttitle = getNode(doc, 'sorttitle', title)
    tagline = getNode(doc, 'tagline', title)
    plot = getNode(doc, 'plot')
    year = getNode(doc, 'year', '1900')
    level = getNode(doc, 'mpaa', 'G')
    date = getNode(doc, 'premiered', '1900-01-01')
    rate = getNode(doc, 'rating', '0')
    genre = getNodeList(doc, 'genre')
    act = getNodeList(doc, 'actor', 'name')
    direc = getNodeList(doc, 'director')
    writ = getNodeList(doc, 'writer')
#    stu = getNodeList(doc, 'studio')

    buf, group = bytearray(), bytearray()
    writeByte(buf, 0x08)
    writeByte(buf, 0x01)

    writeByte(buf, 0x12)
    writeString(buf, title)

    writeByte(buf, 0x1A)
    writeString(buf, sorttitle)

    writeByte(buf, 0x22)
    writeString(buf, tagline)

    writeByte(buf, 0x28)
    writeInt(buf, int(year))

    writeByte(buf, 0x32)
    writeString(buf, date)

    writeByte(buf, 0x38)
    writeByte(buf, 0x01)

    writeByte(buf, 0x42)
    writeString(buf, plot)

    writeByte(buf, 0x4A)
    writeString(buf, 'null')

    for a in act:
        writeByte(group, 0x0A)
        writeString(group, a)

    for d in direc:
        writeByte(group, 0x12)
        writeString(group, d)

    for g in genre:
        writeByte(group, 0x1A)
        writeString(group, g)

    for w in writ:
        writeByte(group, 0x22)
        writeString(group, w)

    writeByte(buf, 0x52)
    writeInt(buf, len(group))
    buf.extend(group)
    group.clear()

    writeByte(buf, 0x5A)
    writeString(buf, level)

    writeByte(buf, 0x60)
    writeInt(buf, int(float(rate) * 10))

    if os.path.exists(posterPath):
        writeByte(buf, 0x8A)
        writeByte(buf, 0x01)

        posterFinal = toBase64(posterPath)
        posterMd5 = toMd5(posterFinal)

        writeString(buf, posterFinal)
        writeByte(buf, 0x92)
        writeByte(buf, 0x01)
        writeString(buf, posterMd5)

    if os.path.exists(fanartPath):
        writeByte(buf, 0xAA)
        writeByte(buf, 0x01)

        fanartFinal = toBase64(fanartPath)
        fanartMd5 = toMd5(fanartFinal)

        writeByte(group, 0x0A)
        writeString(group, fanartFinal)
        writeByte(group, 0x12)
        writeString(group, fanartMd5)
        writeByte(group, 0x18)
        writeInt(group, int(time.time()))

        writeInt(buf, len(group))
        buf.extend(group)
        group.clear()

    with open(target_path, 'wb') as op:
        op.write(buf)


def writeByte(ba, t):
    ba.extend(bytes([int(str(t))]))

def writeString(ba, string):
    byte = string.encode('utf-8')
    length = len(byte)
    writeInt(ba, length)
    ba.extend(byte)

def writeInt(ba, len):
    while len > 128:
        writeByte(ba, len % 128 + 128)
        len = len // 128
    writeByte(ba, len)

def getNode(doc, tag, default = ' '):
    nd = doc.getElementsByTagName(tag)
    if len(nd) < 1 or not nd[0].hasChildNodes() :
        return default
    return nd[0].firstChild.nodeValue

def getNodeList(doc, tag, childTag = '', default = []):
    nds = doc.getElementsByTagName(tag)
    if len(nds) < 1 or not nds[0].hasChildNodes() :
        return default
    if len(childTag) == 0:
        return [nd.firstChild.nodeValue for nd in nds]
    else:
        return [getNode(nd, childTag, '') for nd in nds]

def toBase64(picPath):
    splitleng = 76
    with open(picPath, "rb") as p:
        picBytes = p.read()
    picBase64 = compressPic(picBytes).decode('utf-8')
    picList = [picBase64[i:i+splitleng] for i in range(0, len(picBase64), splitleng)]
    return '\n'.join(picList)

def compressPic(bytes, kb = 200, k = 0.8):
    with io.BytesIO(bytes) as im:
        picSize = len(im.getvalue()) // 1024
        if picSize <= kb:
            return base64.b64encode(bytes)
        imTemp = im
        while picSize > kb:
            img = Image.open(imTemp)
            x, y = img.size
            out = img.resize((int(x * k), int(y * k)), Image.LANCZOS)
            imTemp.close()
            imTemp = io.BytesIO()
            out.save(imTemp, 'jpeg')
            picSize = len(imTemp.getvalue()) // 1024
        b64 = base64.b64encode(imTemp.getvalue())
        imTemp.close()
        return b64

def toMd5(picFinal):
    return hashlib.md5(picFinal.encode("utf-8")).hexdigest()

if __name__ == '__main__':
    poster = 'poster.jpg'#封面图默认名
    fanart = 'fanart.jpg'#背景图默认名
    directory = r'/volume1/video/Links/Movie/'
    convertList = []
    checkAllFiles(directory, convertList, poster, fanart)

    print('success ' + str(len(convertList)) + ' files')
    #for item in convertList:
    #    print(item)
