#!/usr/bin/python
# -*- coding: utf8 -*-

# Copyright 2013 Kostyantyn Ovechko <fastinetserver@gmail.com>
#
# Author: Kostyantyn Ovechko <fastinetserver@gmail.com>

# This program is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License version 3, as published by the Free Software Foundation.
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranties of MERCHANTABILITY, SATISFACTORY QUALITY, 
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with this program.
# If not, see <http://www.gnu.org/licenses/>.

import time
import random
import pycurl
import settings
import re
import StringIO
import sys
import datetime
import os
import urllib

#ERRORS
STATUS_OK=0
ERROR_DURING_OS_WALK_TMP_DIR=105
ERROR_DURING_OS_UNLINK_TMP_FILE=106
ERROR_DURING_GET_PAGE=107

def debug(text):
    if settings.DEBUG_ON:
        print text

def show(text):
    if settings.SHOW_ON:
        print text

def close_connection(tmp_dir):
    """
    Close connection
    """
    try:
        for root, dirs, files in os.walk(tmp_dir):
            try:
                for f in files:
                    debug(os.path.join(root,f))                
                    os.unlink(os.path.join(root,f))
                debug("Connection closed")
            except:
                return ERROR_DURING_OS_UNLINK_TMP_FILE
    except:
        return ERROR_DURING_OS_WALK_TMP_DIR
    return STATUS_OK

def get_page(url, tmp_dir, stage, save_file=None, save_file_bool=False, post_fields=None, print_data_bool=False, do_not_return_content=True, desc=''):
        """ 
        Get http-page content from url
        """
        show( "Stage: "+stage+" - "+desc+" STARTED")
        debug("URL_before_encode: "+url)
        try:
            url=str(url)
        except Exception:
            url=urllib.urlencode({ 'url' : url.encode('utf-8')})[4:]

#        show("URL_after_encode: "+url)

        ck_file=tmp_dir+'/cookie.txt'
        page_buffer = StringIO.StringIO()
        curl_conn = pycurl.Curl()
        curl_conn.setopt(pycurl.FOLLOWLOCATION, 1)
        curl_conn.setopt(pycurl.TIMEOUT, settings.FETCH_TIMEOUT_SECS)
        curl_conn.setopt(pycurl.URL, url)
        curl_conn.setopt(pycurl.HTTPHEADER, [ \
            "User-Agent: Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.46 Safari/536.5", \
            "Host: www.linkvana.com"])
        curl_conn.setopt(pycurl.SSL_VERIFYHOST, False)
        curl_conn.setopt(pycurl.SSL_VERIFYPEER, False)
        curl_conn.setopt(pycurl.SSLVERSION, pycurl.SSLVERSION_SSLv3)
        curl_conn.setopt(pycurl.COOKIEFILE, ck_file) 
        curl_conn.setopt(pycurl.COOKIEJAR, ck_file)
        if settings.proxy!=None:
            curl_conn.setopt(pycurl.PROXY, settings.proxy)
        if post_fields!=None:
            curl_conn.setopt(pycurl.POSTFIELDS, post_fields)        
        curl_conn.setopt(pycurl.WRITEFUNCTION, page_buffer.write) 

        try:
            curl_conn.perform()   
        except Exception:
            return None, ERROR_DURING_GET_PAGE

        curl_conn.close()
        page_content=page_buffer.getvalue()
        page_content=page_content.decode('unicode-escape')
        page_content=page_content.encode('utf-8', 'ignore')
        page_buffer.close()
        if save_file_bool:
            if save_file==None: 
                save_file=tmp_dir+"/"+stage+"_html.html"
            save_file_handler = open(save_file, 'w')
            save_file_handler.write(page_content)
            save_file_handler.close()
        return page_content, STATUS_OK