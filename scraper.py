import requests as rq
from BeautifulSoup import BeautifulSoup as bs
import psycopg2

def getAllCategories(indexPageSoup):
    categoryList=[]
    try:
        catalogTag=indexPageSoup.find("div",{"id":"catalogs"})
        if catalogTag is not None:
            categorySpans=catalogTag.findAll("span")
            if len(categorySpans) >0:
                for span in categorySpans:
                    categoryLink=span.find("a")
                    if categoryLink is not None:
                        categoryDict={}
                        categoryDict["name"]=categoryLink.getText().strip()
                        categoryDict["link"]="http://www.dmoz.org"+str(categoryLink.get("href")).strip()
                        categoryList.append(categoryDict)

        return categoryList
    except UnicodeEncodeError as err:
        pass

def getAllSubCategories(categoryDict):
    try:
        subCategoryList=[]
        sp=bs(rq.get(str(categoryDict["link"])).text)
        allHtmlLists=sp.findAll("ul",{"class":"directory dir-col"})
        if len(allHtmlLists)>0:
            for ul in allHtmlLists:
                htmlListElements=ul.findAll("li")
                if len(htmlListElements)>0:
                    subcatDict={}
                    for li in htmlListElements:
                        linkElement=li.find("a")
                        if linkElement is not None:
                            subcatDict["name"]=str(linkElement.getText()).strip()
                            subcatDict["link"]="http://www.dmoz.org"+linkElement.get("href").strip()
                            subCategoryList.append(subcatDict)

        return subCategoryList
    except UnicodeEncodeError as err:
        pass

conn=psycopg2.connect(database="YOUR DATABASE NAME",
                user="postgres",
                password="YOUR PASSWORD HERE#",
                host="127.0.0.1",
                port="5432")
print("[*]Fetching and storing values...")
sp=bs(rq.get("http://www.dmoz.org").text)
categoryList=getAllCategories(sp)
cursorObj=conn.cursor()

for dictElement in categoryList:
    cursorObj.execute("insert into categoryLinks values('%s','%s')" \
    %(dictElement['name'],dictElement['link']))

conn.commit()
print("[*]Values stored to database successfully!")
conn.close()
