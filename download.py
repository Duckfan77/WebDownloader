import requests
from lxml import html
import sys

#URL of first page is first system argument, if present 
url=''
try:
	url=sys.argv[1]
except:
	url='No'

#Hardcoded Test Values
titlePath='//h1[@class="entry-title"]'
bodyPath='//div[@class="entry-content"]'
nextPath='//div[@class="entry-content"]//a'
XPath=True

#main download mechanism
toc="<h1>Table of Contents</h1>"
bookBody=""
index=1

#Iterate over all chapters
while url:
	#Fix malformed urls
	if('http' not in url):
		url=''

	print(url)

	#Get page content
	doc=requests.get(url)
	
	#Handle bad status codes
	if((doc.status_code//100)!=2):
		print("Error getting page: "+str(doc.status_code))
		url=''
	else:

		#Pull convert to tree
		tree = html.fromstring(doc.content)
		#Get title and body, choosing XPath or CSSSelector
		#For most items, the first item in each list is the correct one. Adjust list indecies accordingly
		if XPath:
			title=tree.xpath(titlePath)[0]
			body = tree.xpath(bodyPath)[0]
		else:
			title=tree.cssselect('h1.entry-title')[0]
			body = tree.cssselect('div.entry-content')[0]
		
		print(type(title))
		print(title.text_content())

		#Clean up body
		body.remove(body.xpath('.//div')[0])	#Removes last div tag in body, usually contains sharing links
		
		links=(body.xpath('.//p[.//a]'))			#Gets all links in paragraph tags
		#Removes all paragraph tags that contain said links.
		for a in links:
			#print(html.tostring(a))
			#print()
			body.remove(a)

		#Print main text of body
		#print(html.tostring(body))

		#Populate TOC and Body
		toc+="<a href=\"#chap"+str(index)+'\"'+str(html.tostring(title))+'</a><br>'
		bookBody+="h1 id=\"chap"+str(index)+'"'+str(html.tostring(title))+'</h1>'
		bookBody+=str(html.tostring(body))

		#Get URL of next chapter
		for p in links:
			a=p.xpath('.//a[contains(@title, "Next")]')
			print(a[0].get('href'))
		url2=tree.xpath(nextPath)
		print(url2)
		url=''
