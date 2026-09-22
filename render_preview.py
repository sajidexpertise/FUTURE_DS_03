"""Render a shareable PNG of the default April dashboard from validated report.

Optional dependency: Pillow. The interactive dashboard itself needs no packages.
"""
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
report = json.loads((ROOT / 'reports' / 'analysis.json').read_text(encoding='utf-8'))
now = report['current']
sources = report['sources']
W, H = 1680, 945
im = Image.new('RGB', (W, H), '#10112a')
d = ImageDraw.Draw(im)
fontfile = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
boldfile = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def f(size, bold=False): return ImageFont.truetype(boldfile if bold else fontfile, size)
def txt(x,y,s,size=16,fill='#f4f4ff',bold=False): d.text((x,y),str(s),font=f(size,bold),fill=fill)
def box(rect, bg='#181936', border='#464577', radius=12, width=2): d.rounded_rectangle(rect,radius=radius,fill=bg,outline=border,width=width)
def p(a,b,dec=1): return 100*a/b if b else 0
def fmt(v):return f'{int(v):,}'

d.ellipse((-200,-320,550,430),fill='#1d1437')
d.ellipse((1190,570,2020,1410),fill='#102b3f')
txt(35,17,'FUTURE INTERNS   ·   DATA SCIENCE & ANALYTICS   ·   TASK 03',13,'#bec4e8',True)
txt(35,43,'CONVERT',45,'#ffffff',True)
txt(285,53,'/ Marketing Intelligence',37,'#e4e1fb')
txt(36,101,'Marketing Funnel & Conversion Performance Analysis   •   Simulated campaign data',15,'#b1b8d5')
for x,w,h,t in [(930,215,'Date Range','Apr 1 – 30, 2024'),(1159,184,'Source','All Sources'),(1357,140,'Device','All Devices')]:
    txt(x,19,h,11,'#b8bad2',True);box((x,40,x+w,81),'#191b3b','#4e5180',7,1);txt(x+10,52,t,13)
box((1511,40,1650,81),'#133853','#2bc9ff',7);txt(1524,51,'↓ Export CSV',13,'#ffffff',True)

cards=[('Impressions','◉',now['impressions'],'#3ebfff',p(now['clicks'],now['impressions'])),('Clicks','➤',now['clicks'],'#36e9e3',p(now['leads'],now['clicks'])),('Qualified leads','✦',now['qualified_leads'],'#c893ff',p(now['qualified_leads'],now['leads'])),('Customers','★',now['customers'],'#beff94',p(now['customers'],now['qualified_leads']))]
for i,(name,symbol,count,color,step) in enumerate(cards):
    x=34+i*324;box((x,137,x+311,254),'#14213b',color,12,2);d.ellipse((x+17,155,x+83,221),fill='#214267');txt(x+37,168,symbol,28,color,True);txt(x+101,156,fmt(count),28,'#ffffff',True);txt(x+102,194,name,15,'#ffffff',True);txt(x+102,224,f'{step:.1f}% stage conversion',12,'#83dec8')
box((1340,137,1645,912),'#201832','#714a90',14)
txt(1362,159,'⚠  Biggest Volume Loss',20,'#ffffff',True)
loss=max(report['stage_losses'],key=lambda item:item['lost'])
txt(1362,195,f"{loss['drop_off_pct']:.0f}%",62,'#ff8197',True)
txt(1362,272,'drop between',14,'#dedcf1')
txt(1362,295,loss['from'].replace('_',' ').title(),17,'#ffffff',True)
txt(1362,319,'and '+loss['to'].replace('_',' ').title(),17,'#ffffff',True)
txt(1362,356,f"{loss['lost']:,} lost at this stage",13,'#ffabb1')
d.line((1364,393,1624,393),fill='#544165',width=2)
txt(1362,420,'✦  Actions to Test',21,'#ffffff',True)
actions=[('Creative and targeting','Test ad variants for click-through','and eventual customers.'),('Landing page friction','Audit speed, copy and forms;','measure qualified leads.'),('Lead follow-up','Experiment with contact timing','and qualification rules.')]
for i,(a,b,c) in enumerate(actions):
    y=470+i*133;d.ellipse((1363,y,1397,y+34),fill=['#4bd1fb','#bf95ff','#c5f47f'][i]);txt(1374,y+7,i+1,16,'#182039',True);txt(1409,y,a,13,'#ffffff',True);txt(1409,y+27,b,11,'#c2bfd5');txt(1409,y+44,c,11,'#c2bfd5')
txt(1360,883,'SIMULATED DATA · TEST IDEAS',11,'#9c9cb7')

box((34,270,1325,604),'#171837','#674495',14)
txt(59,285,'Customer Journey Flow',26,'#ffffff',True)
txt(59,320,'From impression to customer — where do people drop?',15,'#b8c2e8')
txt(1118,285,f"{report['overall_conversion_pct']:.2f}%",39,'#beff99',True)
txt(1120,333,'overall conversion',12,'#aebadd')
stage_keys=['impressions','clicks','leads','qualified_leads','customers']
stage_names=['Impressions','Clicks','Leads','Qualified','Customers']
colors=['#30c0ff','#2ce8e4','#b983ff','#adf77e','#ff8899']
symbols=['◉','➤','▤','✦','★']
for i,key in enumerate(stage_keys):
    x=53+i*252;box((x,381,x+227,554),'#142441',colors[i],13,3)
    txt(x+94,391,symbols[i],25,colors[i],True)
    txt(x+17,430,stage_names[i],17,'#ffffff',True)
    txt(x+17,458,fmt(now[key]),27,'#ffffff',True)
    txt(x+17,497,f"{p(now[key],now['impressions']):.2f}% of impressions",12,colors[i],True)
    if i:txt(x+17,530,f"↓ {p(now[stage_keys[i-1]]-now[key],now[stage_keys[i-1]]):.0f}% stage drop",12,'#ff9195',True)
    if i<4:txt(x+229,446,'›',19,'#ffc2b8',True)
txt(57,570,'Each stage is a subset of the preceding stage. All figures are computed from the included synthetic CSV.',12,'#a9aecb')

box((34,619,669,912),'#172039','#3d4e8b',13)
txt(56,639,'▮  Channel Conversion Comparison',21,'#ffffff',True)
txt(56,671,'Customers and impression-to-customer conversion by source',12,'#b5bee0')
names=sorted(sources,key=lambda s:sources[s]['customers'],reverse=True)
cc=['#37d7f1','#ad80fb','#fc7ebb','#c2f078','#fda269']
maxc=max(sources[s]['customers'] for s in names)
for i,name in enumerate(names):
    y=715+i*37;r=sources[name];txt(57,y,name,13);d.rounded_rectangle((203,y+5,432,y+19),radius=3,fill='#293255');d.rounded_rectangle((203,y+5,203+round(229*r['customers']/maxc),y+19),radius=3,fill=cc[i]);txt(466,y,fmt(r['customers']),13,'#ffffff',True);txt(561,y,f"{p(r['customers'],r['impressions']):.2f}%",13,'#d6fa99',True)

box((685,619,1325,912),'#182039','#53418e',13)
txt(707,639,'◎  Campaign Efficiency',21,'#ffffff',True)
txt(707,671,'Reach vs. conversion rate · bubble size = customers',12,'#b5bee0')
left,top,right,bottom=748,711,1282,857
for j in range(5):
    x=left+(right-left)*j/4;y=top+(bottom-top)*j/4;d.line((x,top,x,bottom),fill='#334064');d.line((left,y,right,y),fill='#334064')
maxi=max(r['impressions'] for r in sources.values())*1.19
maxr=max(p(r['customers'],r['impressions']) for r in sources.values())*1.28
for i,name in enumerate(names):
    r=sources[name];cx=left+(right-left)*r['impressions']/maxi;cy=bottom-(bottom-top)*p(r['customers'],r['impressions'])/maxr;radius=9+11*(r['customers']/maxc)**.5
    d.ellipse((cx-radius,cy-radius,cx+radius,cy+radius),fill=cc[i],outline='#eeeeff',width=2)
    labelx=min(1220,cx+radius+8);txt(labelx,cy-9,name,11)
txt(925,876,'Impressions →',12,'#b9c4e4')
txt(39,923,'────────────────    SYNTHETIC PORTFOLIO DATA  ·  INTERACTIVE VERSION AT REPOSITORY ROOT',10,'#99a2c2')
txt(1390,923,'SAJID ALI · FUTURE_DS_03',10,'#99a2c2')
im.save(ROOT/'dashboard'/'dashboard.png',optimize=True)
print('Created dashboard/dashboard.png with figures from reports/analysis.json')
