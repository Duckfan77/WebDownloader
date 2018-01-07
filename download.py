import requests
from lxml import html
import sys

#URL of first page is first system argument, if present 
url=''
output='error.html'
try:
	url=sys.argv[1]
	output=sys.argv[2]
except:
	url=''
	print("Invalid paramaters")

#Hardcoded Test Values
titlePath='//h1[@class="entry-title"]'
bodyPath='//div[@class="entry-content"]'
nextPath='//div[@class="entry-content"]//p//a[contains(@title, "Next") or contains(text(), "Next")]'
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
		print('http error')

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
			nextLink = tree.xpath(nextPath)
		else:
			title=tree.cssselect(titlePath)[0]
			body = tree.cssselect(bodyPath)[0]
			nextLink = tree.cssselect(nextPath)
		
		print(title.text_content())

		#Get the Next URL, as cleaning can remove the links
		if(len(nextLink)!=0):
			url=nextLink[0].get('href')
		else:
			url=''
			print('next error')

		#Clean up body
		body.remove(body.xpath('.//div')[0])	#Removes last div tag in body, usually contains sharing links
		
		links=(body.xpath('.//p[.//a]'))			#Gets all links in paragraph tags
		#Removes all paragraph tags that contain said links.
		for p in links:
			#print(html.tostring(p))
			#print()
			body.remove(p)

		#Print main text of body
		#print(html.tostring(body).decode())

		#Populate TOC and Body
		toc+='<a href="#chap'+str(index)+'">'+title.text_content()+'</a><br>'
		bookBody+='<h1 id="chap'+str(index)+'">'+title.text_content()+'</h1>'
		bookBody+=(html.tostring(body)).decode()	#Outer div tag remains, but gerenally not impactful. Following line attempts to remove outer div tage, but frequently fails to get full text.
		#bookBody+=(b''.join((map(html.tostring, body.iterchildren(), 'unicode'))).decode())

		index+=1
with open(output,'w') as f:
	f.write(toc+'\n'+bookBody)
