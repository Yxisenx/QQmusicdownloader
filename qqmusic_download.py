#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import time
import random
import requests
import lxml.etree as le


def song_download(mid,path):
    if os.path.exists(path):
        pass
    else:
        os.makedirs(path)
    #url = 'https://i.y.qq.com/v8/playsong.html?songmid=%s'%mid
    guid = random.randint(9000000000,9999999999)
    data = '{"req_0":{"module":"vkey.GetVkeyServer","method":"CgiGetVkey","param":{"guid":"%s","songmid":["%s"],"songtype":[0],"uin":"0","loginflag":1,"platform":"20"}}}'%(guid,mid)
    url1 = 'https://u.y.qq.com/cgi-bin/musicu.fcg?data=%s '%data   #vkey获取接口
    try:
        songinfo1 = json.loads(requests.get(url1).content)
        vkey = songinfo1['req_0']['data']['midurlinfo'][0]['vkey']#QQ音乐有版权的歌曲可以直接获得vkey
        if vkey=='':
            vkey = songinfo1['req_0']['data']['testfile2g'][44:-15]#QQ音乐无版权的需要从试听链接中截取vkey
        fmid = songinfo1['req_0']['data']['midurlinfo'][0]['filename'][4:-4]
    except:
        return 0

    #songid获取接口
    try:
        songid = le.HTML(requests.get('https://y.qq.com/n/yqq/song/%s.html'%mid).content).xpath('//a[@class="mod_btn js_more"]/@data-id')[0]
    except:
        return 0
    data2 = '{"songinfo":{"method":"get_song_detail_yqq","param":{"song_type":0,"song_mid":"%s","song_id":%s},"module":"music.pf_song_detail_svr"}}'%(mid,songid)
    url2 = 'https://u.y.qq.com/cgi-bin/musicu.fcg?data=%s'%data2
    #歌曲相关信息获取接口
    try:
        songinfo2 = json.loads(requests.get(url2).content)
        songname = songinfo2['songinfo']['data']['extras']['name']#歌曲名字
        singernum = len(songinfo2['songinfo']['data']['track_info']['singer'])
        if singernum == 1:                                      #歌手名字判断是否是独唱
               singer  = songinfo2['songinfo']['data']['track_info']['singer'][0]['name']
        else:
            singer = songinfo2['songinfo']['data']['track_info']['singer'][0]['name']
            for i in range(1,singernum):
                singer = singer + '&'+ songinfo2['songinfo']['data']['track_info']['singer'][i]['name']
    except:
        return 0
    file = path +'\\'+ songname + '-' + singer
    houzhui = ['.flac','.mp3','.m4a']
    for each in houzhui:
        if os.path.exists(file+each):
            print(songname + '-' + singer + each + '\t已存在')
            return 1
    try:
        downloadlink = 'http://streamoc.music.tc.qq.com/F000%s.flac?guid=%s&vkey=%s&uin=0&fromtag=58'%(fmid,guid,vkey)
        r = requests.get(downloadlink)
        if r.status_code == 200:
            print('正在下载无损音质  %s-%s.flac'%(songname,singer))
            music = r.content
            with open(file+'.flac', 'wb') as f:
                f.write(music)
        else:
            downloadlink = 'http://streamoc.music.tc.qq.com/A000%s.ape?guid=%s&vkey=%s&uin=0&fromtag=58'%(fmid,guid,vkey)
            r = requests.get(downloadlink)
            if r.status_code == 200:
                print('正在下载无损音质  %s-%s.ape'%(songname,singer))
                music = r.content
                with open(file+'.ape', 'wb') as f:
                    f.write(music)
            else: 
                downloadlink = 'http://streamoc.music.tc.qq.com/M800%s.mp3?guid=%s&vkey=%s&uin=0&fromtag=58'%(fmid,guid,vkey)
                r = requests.get(downloadlink)
                if r.status_code == 200:
                    print('正在下载320k高品质  %s-%s.mp3'%(songname,singer))
                    music = r.content
                    with open(file+'.mp3', 'wb') as f:
                        f.write(music)
                else:
                    downloadlink = 'http://streamoc.music.tc.qq.com/M500%s.mp3?guid=%s&vkey=%s&uin=0&fromtag=58'%(fmid,guid,vkey)
                    r = requests.get(downloadlink)
                    if r.status_code == 200:
                        print('正在下载128k标准品质  %s-%s.mp3'%(songname,singer))
                        music = r.content
                        with open(file+'.mp3', 'wb') as f:
                            f.write(music)
                    else:
                        downloadlink = 'http://streamoc.music.tc.qq.com/C400%s.m4a?guid=%s&vkey=%s&uin=0&fromtag=58'%(fmid,guid,vkey)
                        r = requests.get(downloadlink)
                        if r.status_code == 200:
                            print('正在下载94k低音质  %s-%s.m4a'%(songname,singer))
                            music = r.content
                            with open(file+'.m4a', 'wb') as f:
                                f.write(music)
                        else:
                            return 0
        return 1
    except:
        return 0

#####通过api获取专辑中song_mid
    
def album_parse(url):
    api = 'https://c.y.qq.com/v8/fcg-bin/fcg_v8_album_info_cp.fcg?albummid=000QXjVc1r7NQO'
    album = json.loads(requests.get(api).content)
    print(album)


def album_download(url,path):
    if 'https' not in url:
        url = 'https' + url[4:]
    song_mid = album_parse(url)['song']
    i=0
    k=0
    for each in song_mid:
        a = song_download(each,path)
        k = k + 1
        if a==0:
            i = i + 1
    print('共下载%d首歌,其中%d首因QQ音乐无版权下载失败'%(k,i))



def playlist_parse(url):
    song_num = 1000##暂未找到好的办法直接在网页上获取歌曲数目
    listid = url[32:-5]
    nowtime = str(int(round(time.time() * 1000)))
    header = {
        'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36',
        'referer':'https://y.qq.com/portal/playlist.html'
    }
    api = 'https://c.y.qq.com/qzone/fcg-bin/fcg_ucc_getcdinfo_byids_cp.fcg?uin=0&format=json&inCharset=utf-8&outCharset=utf-8&notice=0&platform=h5&needNewCode=1&new_format=1&pic=500&disstid=%s&type=1&json=1&utf8=1&onlysong=0&picmid=1&nosign=1&song_begin=0&song_num=%s&_=%s'%(listid,song_num,nowtime)
    playlist = json.loads(requests.get(api, headers = header).content)
    ret = {}
    ret['name'] = playlist['cdlist'][0]['dissname']
    ret['song'] = []
    for each in playlist['cdlist'][0]['songlist']:
        ret['song'].append(each['mid'])
    return ret



def playlist_download(url,path):
    if 'https' not in url:
        url = 'https' + url[4:]
    if  'playsquare' in url:
        url = 'https://y.qq.com/n/yqq/playlist/' + url[34:]
    song_mid = playlist_parse(url)['song']
    i=0
    k=0
    for each in song_mid:
        a = song_download(each,path)
        k = k + 1
        if a==0:
            i = i + 1
    print('共下载%d首歌,其中%d首因QQ音乐无版权下载失败'%(k,i))

def config_load():
    try:
        with open('config.json','r',encoding = 'utf-8') as f:
            a = json.load(f)
        return a
        
    except:
        print('配置文件载入错误')

    
if __name__ == '__main__':
    config = config_load()
    if 'playsquare' in config['url'] or 'playlist' in config['url']:
        playlist_download(config['url'],config['path'])
    else:
        if 'album' in config['url']:
            album_download(config['url'],config['path'])
    '''
    song_download('000y3gHb4ZOsiq','C:\\Users\\hasee\\Desktop\\tmp')
    '''
