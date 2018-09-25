#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import json
from lxml import etree as le
import time
import random
import os


def album_parse(album_mid):
    try:
        api = 'https://c.y.qq.com/v8/fcg-bin/fcg_v8_album_info_cp.fcg?albummid=%s' % album_mid
        album = json.loads(requests.get(api).content)
        song_mid = []
        for each in album['data']['list']:
            song_mid.append(each['songmid'])
        ret = {}
        ret['code'] = 1
        ret['datas'] = []
        for each in song_mid:
            try:
                ret['datas'].append(song_parse(each))
            except:
                pass
        return ret
    except:
        return {'code': -1}


def playlist_parse(playlist_mid):
    song_num = 1000
    nowtime = str(int(round(time.time() * 1000)))
    header = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36',
        'referer': 'https://y.qq.com/portal/playlist.html'
    }
    api = 'https://c.y.qq.com/qzone/fcg-bin/fcg_ucc_getcdinfo_byids_cp.fcg?uin=0&format=json&inCharset=utf-8&outCharset=utf-8&notice=0&platform=h5&needNewCode=1&new_format=1&pic=500&disstid=%s&type=1&json=1&utf8=1&onlysong=0&picmid=1&nosign=1&song_begin=0&song_num=%s&_=%s' % (playlist_mid, song_num, nowtime)
    try:
        playlist = json.loads(requests.get(api, headers=header).content)
        ret = {}
        ret['code'] = 1
        ret['datas'] = []
        for each in playlist['cdlist'][0]['songlist']:
            ret['datas'].append(song_parse(each['mid']))
        return ret
    except:
        return {'code': -1}


def song_parse(song_mid):
    guid = random.randint(9000000000, 9999999999)
    data = '{"req_0":{"module":"vkey.GetVkeyServer","method":"CgiGetVkey","param":{"guid":"%s","songmid":["%s"],"songtype":[0],"uin":"0","loginflag":1,"platform":"20"}}}' % (guid, song_mid)
    url1 = 'https://u.y.qq.com/cgi-bin/musicu.fcg?data=%s ' % data  # vkey获取接口
    try:
        songinfo1 = json.loads(requests.get(url1).content)
        vkey = songinfo1['req_0']['data']['testfile2g'].split('=')[2].split('&')[0]
        fmid = songinfo1['req_0']['data']['midurlinfo'][0]['filename'][4:-4]
    except:
        return {'code': -1}
    # songid获取接口
    try:
        songid = le.HTML(requests.get('https://y.qq.com/n/yqq/song/%s.html' % song_mid).content).xpath('//a[@class="mod_btn js_more"]/@data-id')[0]
    except:
        return {'code': -1}
    data2 = '{"songinfo":{"method":"get_song_detail_yqq","param":{"song_type":0,"song_mid":"%s","song_id":%s},"module":"music.pf_song_detail_svr"}}' % (song_mid, songid)
    url2 = 'https://u.y.qq.com/cgi-bin/musicu.fcg?data=%s' % data2
    # 歌曲相关信息获取接口
    try:
        songinfo2 = json.loads(requests.get(url2).content)
        songname = songinfo2['songinfo']['data']['extras']['name']  # 歌曲名字
        singernum = len(songinfo2['songinfo']['data']['track_info']['singer'])
        if singernum == 1:  # 歌手名字判断是否是独唱
            singer = songinfo2['songinfo']['data']['track_info']['singer'][0]['name']
        else:
            singer = songinfo2['songinfo']['data']['track_info']['singer'][0]['name']
            for i in range(1, singernum):
                singer = singer + '&' + songinfo2['songinfo']['data']['track_info']['singer'][i]['name']
        filename = songname + '-' + singer
    except:
        return {'code': -1}
    quality = songinfo2['songinfo']['data']['track_info']['file']
    ret = {}
    ret['name'] = filename
    ret['link'] = {}
    ret['link']['flac'] = 0
    ret['link']['ape'] = 0
    ret['link']['320mp3'] = 0
    ret['link']['128mp3'] = 0
    ret['link']['m4a'] = 'http://streamoc.music.tc.qq.com/C400%s.m4a?guid=%s&vkey=%s&uin=0&fromtag=58' % (fmid, guid, vkey)
    if quality['size_flac'] is not 0:
        ret['link']['flac'] = 'http://streamoc.music.tc.qq.com/F000%s.flac?guid=%s&vkey=%s&uin=0&fromtag=58' % (fmid, guid, vkey)
    if quality['size_ape'] is not 0:
        ret['link']['ape'] = 'http://streamoc.music.tc.qq.com/A000%s.ape?guid=%s&vkey=%s&uin=0&fromtag=58' % (fmid, guid, vkey)
    if quality['size_320mp3'] is not 0:
        ret['link']['320mp3'] = 'http://streamoc.music.tc.qq.com/M800%s.mp3?guid=%s&vkey=%s&uin=0&fromtag=58' % (fmid, guid, vkey)
    if quality['size_128mp3'] is not 0:
        ret['link']['128mp3'] = 'http://streamoc.music.tc.qq.com/M500%s.mp3?guid=%s&vkey=%s&uin=0&fromtag=58' % (fmid, guid, vkey)
    return ret


def parse(url):
    # 判断链接是否符合要求
    if 'album' not in url and 'playlist' not in url and 'playsquare' not in url and 'song' not in url:
        return {'code': -2}
    if url[-4:] != 'html':
        return {'code': -2}
    if 'https' not in url:
        url = 'https' + url[4:]
    mid = url.split('/')[-1].split('.')[0]
    if 'album' in url:
        ret = album_parse(mid)
    elif 'playlist' in url or 'playsquare' in url:
        ret = playlist_parse(mid)
    else:
        ret = {'code': 1, 'datas': []}
        ret['datas'].append(song_parse(mid))
    return json.dumps(ret)


def downloader(url, flag):
    song = json.loads(parse(url))
    if song['code'] == -2:
        print('链接输入错误！')
        return 0
    elif song['code'] == -1:
        print('解析失败')
        return 0
    print('########\t解析成功，正在下载\t##########')
    path = os.path.split(os.path.realpath(__file__))[0] + '\\music\\'
    if os.path.exists(path):
        pass
    else:
        os.makedirs(path)
    print(path)
    flag2 = ['flac', 'ape', '320mp3', '128mp3', 'm4a']
    i = flag2.index(flag)
    for each in song['datas']:
        k = i
        while each['link'][flag2[k]] == 0:
            k = k + 1
        try:
            if 'mp3' in flag2[k]:
                name = 'mp3'
            else:
                name = flag2[k]
            mpath = path+each['name'] + '.' + name
            if os.path.exists(mpath):
                print('%s\t已存在' % mpath.split('\\')[-1])
                continue
            else:
                print('正在下载\t%s' % mpath.split('\\')[-1])
            murl = each['link'][flag2[k]]
            try:
                with open(mpath, 'wb') as f:
                    f.write(requests.get(murl).content)
                print('%s\t下载成功'%mpath.split('\\')[-1])
            except:
                print('%s\t下载失败' % mpath.split('\\')[-1])
        except:
            pass



if __name__ == '__main__':
    print("#\n#\t链接格式：\n#\t单曲链接：https://y.qq.com/n/yqq/song/000W9uty06xVPY.html\n#\t专辑链接：https://y.qq.com/n/yqq/album/000ym9e23zZSBL.html\n#\t歌单链接：https://y.qq.com/n/yqq/playsquare/3846214337.html\n#\t或 https://y.qq.com/n/yqq/playlist/3846214337.html\n##########################################################")
    while 1:
        url = input('请输入链接：')
        while 1:
            try:
                a = int(input('\t 0 for flac\n\t 1 for ape\n\t 2 for 320Kmp3 \n\t 3 for 128kmp3 \n\t 4 for m4a\n\t请输入音质：'))
                if a in [0, 1, 2, 3, 4]:
                    flag = ['flac', 'ape', '320mp3', '128mp3', 'm4a'][a]
                    print('########\t正在解析，请稍候\t##########')
                    downloader(url, flag)
                    break
                else:
                    print('########\t音质选择有误\t##########')
                    continue
            except:
                print('########\t音质选择有误\t##########')
                continue
        print('Press Ctrl + C to exit.')
    #downloader('https://y.qq.com/n/yqq/song/004MEvgU248YjJ.html', 'flac')