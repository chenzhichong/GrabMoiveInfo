#!/usr/bin/python
#coding:utf8
import os
import urllib
import urllib2
import cookielib
import re
import sys
import socket  
import time  


def login_CHD():
    cookie = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
    postdata=urllib.urlencode({  
        'username':'mcchinese',  
        'password':'chong26419811', 
    })
    req = urllib2.Request(  
        url = 'http://chdbits.org/takelogin.php',  
        data = postdata  
    ) 
    try:
        response = opener.open(req)
        # for item in cookie:  
            # print 'Name = '+item.name  
            # print 'Value = '+item.value            
    except urllib2.HTTPError, e:
        print e.code
    return opener
    


file_path = r"1.txt"
fo = open(file_path, "r+")

# type = sys.getfilesystemencoding()
reload(sys) 
sys.setdefaultencoding("utf-8") # 设置系统的编码
timeout = 60   
socket.setdefaulttimeout(timeout)# 这里对整个socket层设置超时时间。后续文件中如果再使用到socket，不必再设置  

opener = login_CHD()
root = r'http://chdbits.org/'
chdurl = r'http://chdbits.org/torrents.php'
douban_subject_search = r'http://movie.douban.com/subject_search'
douban_post_url_prefix = r'http://img3.douban.com/view/photo/photo/public/'
# 当前目录新建post文件夹
post_folder = r'%s/%s'%(os.getcwd(),r'post')
# print post_folder
for line in fo:
    line=line.strip('\n')
    print '===================================================='
    # print line
    data = {}
    data['incldead'] = '1'
    data['spstate'] = '0'
    data['inclbookmarked'] = '0'
    data['search'] = line
    data['search_area'] = '0'
    data['search_mode'] = '0'
    # str_para = "incldead=" + str(incldead) + "&spstate=" + str(spstate) + "&inclbookmarked=" + str(inclbookmarked) + "&search=" + search + "&search_area=" + str(search_area) + "&search_mode=" + str(search_mode)
    str_para = urllib.urlencode(data)
    # print str_para
    url = chdurl + '?' + str_para
    # print url
    # 读取url内容 
    content = opener.open(url).read()
    # 转换编码  
    # content = content.decode("UTF-8").encode(type) 
    # print content
    result = re.findall(r'没有种子', content)
    if result:
        print url
        print result[0] + ':' + line
        continue
    # rule = r'<a title="' + line +r'" href="(.*?)">'
    # print rule
    result = re.findall(r'<a title="(.*?)" href="(.*?)"><b>(.*?)</b></a>', content)
    # print result
    if not result:        
        print '无法找到电影:[' + line + ']链接页面'
        continue
    torrent_url = root + result[0][1]
    # print torrent_url
    # 进入种子页面抓取imdb号
    content = opener.open(torrent_url).read()
    # 抓取imdb
    rule = r'http://www.imdb.com/title/(tt[0-9]*)'
    result = re.findall(rule, content)
    # print result
    if not result:
        print torrent_url
        print '无法找到电影:[' + line + ']imdb号'
        continue
    imdb = result[0]
    print imdb + ':[' + line + ']'
    
    # 由imdb号在豆瓣电影下载海报和电影相关资讯
    douban_serch_para = {}
    douban_serch_para['search_text'] = imdb
    douban_serch_para['cat'] = '1002'
    str_para = urllib.urlencode(douban_serch_para)
    url = douban_subject_search + '?' + str_para
    content = opener.open(url).read()
    # 抓取电影介绍界面url
    rule = r'http://movie.douban.com/subject/[0-9]*/'
    result = re.findall(rule, content)
    if not result:
        print '无法找到电影:[' + line + ']的豆瓣简介页面'
        continue
    douban_subject_url = result[0]
    # print douban_subject_url
    # 读取电影介绍界面
    content = opener.open(douban_subject_url).read()
    # 抓取海报文件名
    # rule = r'http://img3.douban.com/view/movie_poster_cover/spst/public/(p[0-9]*.jpg)'
    rule = r'<img src="http://img[0-9].douban.com/view/movie_poster_cover/spst/public/(p[0-9]*.jpg)" title="点击看更多海报"'
    result = re.findall(rule, content)
    if not result:
        print '无法抓取海报文件名'
        continue
    post_filename = result[0]
    douban_post_url = douban_post_url_prefix + post_filename
    print douban_post_url
    '''
    # 海报url
    douban_photos_para = {}
    douban_photos_para['type'] = 'R'
    douban_photos_para['start'] = '0'
    douban_photos_para['sortby'] = 'size'
    douban_photos_para['size'] = 'a'
    douban_photos_para['subtype'] = 'o'
    str_para = urllib.urlencode(douban_photos_para)
    url = douban_subject_url + 'photos' + '?' + str_para
    content = opener.open(url).read()
    # 抓取电影海报
    rule = r'http://img3.douban.com/view/photo/thumb/public/p[0-9]*.jpg'
    result = re.findall(rule, content)
    if not result:
        print '无法找到电影:[' + line + ']的海报'
        continue
    post_url = result[0].replace('thumb', 'photo')
    post_name = re.findall(r'http://img3.douban.com/view/photo/photo/public/(p[0-9]*.jpg)', post_url)[0]
    '''
    # 保存海报
    if not os.path.exists(post_folder):
        os.makedirs(post_folder)
    old_path = os.getcwd()
    os.chdir(post_folder)
    f = open(post_filename,'wb+')
    request = urllib2.urlopen(douban_post_url)
    post_content = request.read()  
    f.write(post_content)  
    request.close()
    f.close()
    os.chdir(old_path)
    print '===================================================='

# 关闭打开的文件
fo.close()