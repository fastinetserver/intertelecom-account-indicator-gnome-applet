#!/usr/bin/python
# -*- coding: utf8 -*-
import appindicator
import gtk
import gobject

from tools import *
from lxml import html, etree

COLOR_DICT={
            'white':(255,255,255),
            'red':(255,0,0),
            'green':(0,255,0)
}

TRAFFIC_LEFT_BEFORE_SESSION_SEARCH = re.compile('<td style="color:#000000;">(\d+\.\d+) &#208;&#191;&#208;&#190;')


def get_text(tag):
    return tag.text_content().encode('utf-8','ignore').strip()
#    return tag.text.encode('utf-8', 'ignore').strip()

class Inter():    
    def __init__(self):
        self.last_left="n_a" 
        self.current_dir=os.path.dirname(os.path.abspath(__file__))+'/'
        print self.current_dir 
        self.tmp_dir=self.current_dir+'tmp/'
    
        self.indicator = appindicator.Indicator('inter_indicator', self.current_dir+'n_a_white.png', appindicator.CATEGORY_APPLICATION_STATUS)
        self.indicator.set_status( appindicator.STATUS_ACTIVE )
        self.indicator.set_icon_theme_path(self.tmp_dir)
        self.set_label('n_a')
        m = gtk.Menu()
        group = None
        time_1min_item = gtk.RadioMenuItem(group,'1 min')
        group = time_1min_item
        time_2min_item = gtk.RadioMenuItem(group,'2 min')
        time_5min_item = gtk.RadioMenuItem(group,'5 min')
        time_10min_item = gtk.RadioMenuItem(group,'10 min')
        time_15min_item = gtk.RadioMenuItem(group,'15 min')
        time_30min_item = gtk.RadioMenuItem(group,'30 min')
        time_60min_item = gtk.RadioMenuItem(group,'60 min')
        refresh_now_item = gtk.MenuItem( 'Refresh NOW' )
        
        self.ip_label = gtk.MenuItem('Ip: N/A')
        self.money_left_label = gtk.MenuItem('Money: N/A')
#         self.traffic_consumed_label = gtk.MenuItem("Total: %s Mb, Tx: N/A Mb, Rx: N/A Mb")
#         self.traffic_left_before_session = gtk.MenuItem('IP: N/A')
        self.traffic_left_label = gtk.MenuItem('Traffic Left: N/A')
        qi = gtk.MenuItem( 'Quit' )
        
        m.append(self.traffic_left_label)
        m.append(self.ip_label)
        m.append(self.money_left_label)
#         m.append(self.traffic_consumed_label)
#         m.append(self.traffuc_left_before_session_label)

        m.append(gtk.SeparatorMenuItem())
        
        m.append(time_1min_item)
        m.append(time_2min_item)
        m.append(time_5min_item)
        m.append(time_10min_item)
        m.append(time_15min_item)
        m.append(time_30min_item)
        m.append(time_60min_item)

        m.append(gtk.SeparatorMenuItem())
        m.append(refresh_now_item)
        m.append(qi)
        
        self.indicator.set_menu(m)
        m.show_all()
#        time_1min_item.show()
#        time_2min_item.show()
#        time_5min_item.show()
#        time_10min_item.show()
#        time_15min_item.show()
#        time_30min_item.show()
#        time_60min_item.show()
#        qi.show()
        
        self.timeout=settings.UPDATE_DELAY_SECONDS
        
        time_1min_item.connect('activate', self.time_1min_handler)
        time_2min_item.connect('activate', self.time_2min_handler)
        time_5min_item.connect('activate', self.time_5min_handler)
        time_10min_item.connect('activate', self.time_10min_handler)
        time_15min_item.connect('activate', self.time_15min_handler)
        time_30min_item.connect('activate', self.time_30min_handler)
        time_60min_item.connect('activate', self.time_60min_handler)
        
        refresh_now_item.connect('activate', self.update)
        qi.connect('activate', quit)
    
        self.source_id = gobject.timeout_add(1000, self.update)
    
    def set_timeout(self, mins):
        self.timeout=mins*60*1000
        gobject.source_remove(self.source_id)
        self.source_id = gobject.timeout_add(self.timeout, self.update)
        
    def time_1min_handler(self, action):
        self.set_timeout(1)

    def time_2min_handler(self, action):
        self.set_timeout(2)

    def time_5min_handler(self, action):
        self.set_timeout(5)

    def time_10min_handler(self, action):
        self.set_timeout(10)

    def time_15min_handler(self, action):
        self.set_timeout(15)

    def time_30min_handler(self, action):
        self.set_timeout(30)

    def time_60min_handler(self, action):
        self.set_timeout(60)

    def get_stats(self):    
            stage='1'
            post_fields='phone='+settings.PHONE+'&pass='+settings.PASS+'&ref_link=&js=1'
            content, code=get_page('https://assa.intertelecom.ua/ru/login', self.tmp_dir, stage, None, False, post_fields, False, True,'Get projects list')
#             print content
            tree = html.fromstring(content)
            # we don't know the td_num for these 3 yet, setting None so id doesn't match unless we find the num
            traffic_consumed_td_num = None 
            td_money_left_td_num = None
            td_ip_td_num = None
            ip = "N/A"
            
            td_num = 0
            for td in tree.cssselect("td"):
                td_num+=1
                try:
                    td_content = etree.tostring(td)
#                     print td_num,")", td_content 
                except Exception:
                    continue

                if td_content.find('<td>IP</td>&#13;') > -1:
                    td_ip_td_num = td_num +1
                if td_ip_td_num == td_num:
                    ip = get_text(td)
                    
                if td_content.find('<td>&#208;&#161;&#208;&#176;&#208;&#187;&#209;&#140;&#208;&#180;&#208;&#190;</td>&#13;') > -1:
                    td_money_left_td_num = td_num + 1
                if td_money_left_td_num == td_num:
                    money_left_str = get_text(td)

                if td_content.find('<td>&#208;&#162;&#209;&#128;&#208;&#176;&#209;&#132;&#208;&#184;&#208;&#186; &#208;&#156;&#208;&#145;</td>&#13;') > -1:
                    traffic_consumed_td_num = td_num + 1
                if td_num == traffic_consumed_td_num:
                    try:
                        traffic_consumed_str = td.cssselect('strong')[0].text.strip()
                    except Exception:
                        pass

                try:
                    match = TRAFFIC_LEFT_BEFORE_SESSION_SEARCH.search(td_content)
                    if match:
                        traffic_left_before_session_str = match.group(1) 
                except Exception as err:
                    print td_num,")","error:\n", err
            try:
                money_left=float(money_left_str)
            except Exception:
                money_left = "N/A"
            try:
                traffic_consumed=float(traffic_consumed_str)
            except Exception:
                traffic_consumed = "N/A"
            try:
                traffic_left_before_session=float(traffic_left_before_session_str)
            except Exception:
                traffic_left_before_session = "N/A"
            try:
                traffic_left=traffic_left_before_session-traffic_consumed
            except Exception:
                traffic_left = "N/A"
            
            result={
                        'ip':ip,
                        'money_left':money_left,
                        'traffic_consumed':traffic_consumed,
                        'traffic_left_before_session':traffic_left_before_session,
                        'traffic_left':traffic_left
                    }
            print result
            return result
    
    def quit(self, item):
            gtk.main_quit()
    
    def set_label_old(self, value, text_color='white'):
        print "set_label: %s" % value
        text=str(value)
        font = ImageFont.truetype("Arial_Bold.ttf",14)
        img=Image.new("RGBA", (25,25),(0,0,0))
        draw = ImageDraw.Draw(img)
        if value=="n_a":
            draw.text((1, 5),"N/A",COLOR_DICT[text_color],font=font)
        else:
            draw.text((1, 5),text,COLOR_DICT[text_color],font=font)
        draw = ImageDraw.Draw(img)
        img_path=self.tmp_dir+text+'_'+text_color+'.png'
        print img_path
        img.save(img_path)
        self.indicator.set_icon(text)
    
    def set_label(self, value, text_color='white'):
        print "set_label: %s of color %s" % (value, text_color)
        if value=="n_a":
            text="N/A"
        else:
            text=str(value)
        STATUS_DICT={
            'white':'T',
            'green':'?',
            'red':'?!'
        }
        text = STATUS_DICT[text_color]+":"+text
        self.indicator.set_label(text)
        while gtk.events_pending():
            gtk.main_iteration()
    
    def update(self, action=None):
        self.set_label(self.last_left, text_color='green')
        time.sleep(3)
	timeout = self.timeout
        try:
            stats=self.get_stats()
            self.last_left=int(stats['traffic_left'])
        except Exception:
            print "Update problem ... Last Left: %s" % self.last_left            
            self.set_label(self.last_left, text_color='red')
            self.traffic_left_label.set_label("Traffic Left: N/A")
            self.money_left_label.set_label("Money:  N/A")
            self.ip_label.set_label("IP: N/A")
	    timeout = 10*60*1000 #10 minutes
        else:
            print "Updating... Left: %s" % self.last_left
            self.set_label(self.last_left)
            self.traffic_left_label.set_label("Traffic Left: %s Mb" % self.last_left)
            self.money_left_label.set_label("Money: %s" % stats['money_left'])
            self.ip_label.set_label("IP: %s" % stats['ip'])
        try:
            gobject.source_remove(self.source_id)
        except Exception:
            pass
        self.source_id = gobject.timeout_add(timeout, self.update)

if __name__ ==  '__main__':
    inter=Inter()
    gtk.main()