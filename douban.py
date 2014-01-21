#coding=utf8
import urllib2
import os
from BeautifulSoup import BeautifulSoup
import time
import datetime
from dateutil.relativedelta import relativedelta
import re

folder = 'html'
if not os.path.exists(folder):
    os.makedirs(folder)

def crawl(start = 1, end = 0, user = 'cwyalpha'):
    if not os.path.exists(os.path.join(folder, user)):
        os.makedirs(os.path.join(folder, user))
    if end == 0:
        content = urllib2.urlopen('http://movie.douban.com/people/'+user+'/collect').read()
        soup = BeautifulSoup(content)
        end = int(soup.find('span', {'class':'thispage'})['data-total-page'])
    for index in xrange(start, end+1):
        content = urllib2.urlopen('http://movie.douban.com/people/'
                                  +user+'/collect?start='
                                  +str(15*(index-1))
                                  +'&sort=time&rating=all&filter=all&mode=grid').read()
        with open(os.path.join(folder, user, str(index)+'.html'), 'w') as output:
            output.write(content)
        print user, index, 'done'
        time.sleep(5)

def drawHTML(dates, rates, tag_count, user):
    dates = sorted(dates)
    start_month = datetime.datetime.strptime(dates[0][0][:-3], '%Y-%m')
    end_month = datetime.datetime.strptime(dates[-1][0][:-3], '%Y-%m')
    dates_count = {}
    for date in dates:
        if date[0][:-3] not in dates_count:
            dates_count[date[0][:-3]] = 0
        dates_count[date[0][:-3]] += 1
    month = start_month
    month_count = []
    month_name = []
    while month <= end_month:
        m = month.strftime('%Y-%m')
        if m in dates_count:
            month_count.append(dates_count[m])
        else:
            month_count.append(0)
        if int(month.strftime('%m'))%3 == 0:
            month_name.append(month.strftime('%y-%m'))
        else:
            month_name.append('')
        month = month + relativedelta(months=1)
    rates1 = '''[
	{name : '1星',value : %(n1)s,color:'#a5c2d5'},
        {name : '2星',value : %(n2)s,color:'#cbab4f'},
        {name : '3星',value : %(n3)s,color:'#76a871'},
        {name : '4星',value : %(n4)s,color:'#9f7961'},
        {name : '5星',value : %(n5)s,color:'#a56f8f'}
];
''' % {'n1':rates[1],
       'n2':rates[2],
       'n3':rates[3],
       'n4':rates[4],
       'n5':rates[5]}
    tags = [(tag,[float(sum(count[4:]))/sum(count),float(count[5])/sum(count),
                  count[5], count[4], count[3], count[2], count[1]])
            for tag,count in tag_count.iteritems() if sum(count) > 3 and len(tag.strip()) > 0]
    tags = sorted(tags, key = lambda x:x[1], reverse = True)
    tag_data = '['
    tag_data += ','.join("{name:'" + tag[0] + "',value:"+str(tag[1][0])+",color:'#006666'}" for tag in tags)
    tag_data += ']'
    table = ''
    for tag in tags:
        table += '<tr>\n'
        table += '<td>'+tag[0]+'</td>\n'
        table += '<td>'+str(tag[1][0])[:5]+'</td>\n'
        for i in xrange(5):
            table += '<td>'+str(tag[1][2+i])+'</td>\n'
        table += '</tr>\n'
    content = '''<!DOCTYPE html>
<html>
    <head>
        <meta charset="UTF-8" />
        <title>%(user)s Douban</title>
        <script type="text/javascript" src="../ichart.1.2.min.js"></script>
        <script type="text/javascript">
        $(function(){
            var rates1 = %(rates1)s;
            var month_data = [
                {
                    name : '次数',
                    value:%(month_count)s,
                    color:'#1f7e92',
                    line_width:2
                }
            ];
            new iChart.Area2D({
                render : 'canvasRatingMonth',
                data: month_data,
                title : '每月看片数',
                width : %(monthwidth)s,
                height : 400,
                coordinate:{background_color:'#edf8fa'},
                sub_option:{
                        smooth : true,
                        hollow_inside:false,
                        point_size:10
                },
                tip:{
		    enable:true,
		    shadow:true
		},
                labels:%(month_name)s
            }).draw();
            new iChart.Column2D({
                render : 'canvasRatingBar',
                data: rates1,
                title : '%(user)s的豆瓣评分',
                width : 800,
                height : 400,
                animation : true,
                animation_duration:800,
                shadow : true,
                shadow_blur : 2,
                shadow_color : '#aaaaaa',
                shadow_offsetx : 1,
                shadow_offsety : 0,
                coordinate:{
                    background_color:'#fefefe',
                    scale:[{
                        position:'left'
                    }]
                }
            }).draw();
            new iChart.Pie2D({
                render : 'canvasRatingPie',
                data: rates1,
                title : '%(user)s的豆瓣评分',
                legend : {
                    enable : true
                },
                sub_option : {
                    label : {
                        background_color:null,
                        sign:false,
                        padding:'0 4',
                        border:{
                            enable:false,
                            color:'#666666'
                        },
                        fontsize:11,
                        fontweight:600,
                        color : '#4572a7'
                    },
                    border : {
                        width : 2,
                        color : '#ffffff'
                    }
                },
                animation:true,
                showpercent:true,
                decimalsnum:2,
                width : 800,
                height : 400,
                radius:140
            }).draw(); 
        });
        </script>
    </head>
    <body>
        <div id='canvasRatingBar'></div>
        <div id='canvasRatingPie'></div>
        <div id='canvasRatingMonth'></div>
        <h4>%(user)s喜欢的标签</h4>
        <table border="1">
        <tr>
          <td>标签</td>
          <td>4，5星占比</td>
          <td>5星</td>
          <td>4星</td>
          <td>3星</td>
          <td>2星</td>
          <td>1星</td>
        </tr>
        %(table)s
        </table>
    </body>
</html>
''' % {'user':user,
       'rates1':rates1,
       'month_count':str(month_count),
       'month_name':str(month_name),
       'monthwidth':str(len(month_name)*20),
       'table':table}
    with open(os.path.join(folder, user+'.html'), 'w') as output:
        output.write(content)

def analyze(user = 'cwyalpha'):
    tag_count = {}
    dates = []
    rates = [0 for i in xrange(6)]
    for fn in os.listdir(os.path.join(folder, user)):
        with open(os.path.join(folder, user, fn), 'r') as f:
            content = f.read()
            soup = BeautifulSoup(content.decode('utf8', 'ignore'))
            for item in soup.findAll('div', {'class':'item'}):
                intro = str(item.find('li', {'class':'intro'}).string.encode('utf8','ignore'))
                intro = set(word.strip() for word in intro.split('/') if '分钟' not in word)
                rate = item.find('span', {'class':re.compile('rating[1-5].*')})
                if rate:
                    rate = re.search('rating([1-5]).*', str(rate['class'])).group(1)
                else:
                    rate = '0'
                date = str(item.find('span', {'class':'date'}).string.encode('utf8','ignore'))
                tags = item.find('span', {'class':'tags'})
                if tags:
                    tags = str(tags.string.encode('utf8', 'ignore'))
                    tags = set([tag for tag in tags.split()
                                if '标签' not in tag
                                and '标签'.decode('utf8').encode('gbk') not in tag])
                else:
                    tags = set()
                tags = intro.union(tags)
                dates.append((date, rate))
                rates[int(rate)] += 1
                for tag in tags:
                    if tag not in tag_count:
                        tag_count[tag] = [0 for i in xrange(6)]
                    tag_count[tag][int(rate)] += 1
    drawHTML(dates, rates, tag_count, user)
##    with open('dates.txt', 'w') as f:
##        dates = sorted(dates)
##        f.write('\n'.join(['\t'.join(date) for date in dates])+'\n')
##    with open('rates.txt', 'w') as f:
##        for i in xrange(6):
##            f.write(str(i) + '\t' + str(rates[i]) + '\n')
##    with open('tags.txt', 'w') as f:
##        tags = [(tag,[float(sum(count[4:]))/sum(count),float(count[5])/sum(count),
##                 count[5], count[4], count[3], count[2], count[1]])
##                for tag,count in tag_count.iteritems() if sum(count) > 3 and len(tag.strip()) > 0]
##        tags = sorted(tags, key = lambda x:x[1], reverse = True)
##        for tag in tags:
##            f.write(tag[0]+'\t'+'\t'.join(str(i) for i in tag[1])+'\n')


crawl(start = 1, end = 0, user = 'seafans')
analyze(user = 'seafans')
