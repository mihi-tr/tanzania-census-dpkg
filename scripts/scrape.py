import lxml.html
import requests
import itertools
import csv
import re

s=requests.Session()

def get_districts():
  url="http://www.nbs.go.tz/sensa/popu1.php"
  r=requests.Request('GET',url).prepare()
  resp=s.send(r)
  h=resp.text
  r=lxml.html.fromstring(h)
  table=r.xpath("//table[@border=1]")[0]
  rows=table.xpath(".//tr")
  captions=["number","name","total","male","female","household size"]
  return [j for j in 
    itertools.ifilter(lambda x: x["number"],
      (dict(zip(captions,[i.text for i in r.xpath("./td")])) for r in rows))]

def remove_commas(l):
  if not l: 
    return l
  if re.search(",[0-9]{3}",l):
    return l.replace(",","")
  else:
    return l.strip()

def get_councils_for_district(d):
  url="http://www.nbs.go.tz/sensa/popu2.php"
  r=requests.Request('POST',url,data={"Reg2":d,"Submit3": "SEARCH"}).prepare()
  h=s.send(r).text
  r=lxml.html.fromstring(h)
  table=r.xpath("//table//table")[0]
  rows=table.xpath(".//tr")
  captions=["region","number","council","total","male","female",
  "household size"]
  return [j for j in 
    itertools.ifilter(lambda x: x["number"] and x["number"]!="0",
      (dict(zip(captions,[d]+[remove_commas(i.text) for i in r.xpath("./td")])) 
        for r in rows))]

def get_all_councils():
  districts=(i['name'] for i in get_districts())
  return [get_councils_for_district(d) for d in districts]

def scrape():
  columns=["region","number","council","total","male","female","household size"]
  with open("../data/tanzania-census.csv","wb") as f:
    w=csv.DictWriter(f,columns)
    w.writerow(dict(zip(columns,columns)))
    for d in reduce(lambda x,y: x+y,get_all_councils()):
      w.writerow(d)

if __name__=="__main__":
  scrape()
