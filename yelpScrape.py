from bs4 import BeautifulSoup
import requests
from functools import reduce
import sys

#Get rest from input
if (len(sys.argv[1:]) != 0 ):
	print ("Listed of resturants input are: " + ", ".join(sys.argv[1:]))
	bizNameList = sys.argv[1:]
#Get rest from pre-inputed
else:
	bizNameList = ["sushi-ota-san-diego", "akikos-restaurant-san-francisco", "saru-sushi-bar-san-francisco"]
	print ("Listed of resturants input are: " + ", ".join(bizNameList))

userRatingDicList = []
filteredDictList = []

#Scraping

for bizNumber in range(len(bizNameList)):

	print ("Currently scraping " + str(bizNameList[bizNumber]))

	urlnext = "http://www.yelp.com/biz/" + bizNameList[bizNumber] + "?start="
	url = "http://www.yelp.com/biz/" + bizNameList[bizNumber]

	response = requests.get(url)
	html = response.content

	soup = BeautifulSoup(html, "html.parser")

	userRatingDic = {}

	number_of_page = soup.find("div", {"class": "page-of-pages arrange_unit arrange_unit--fill"}).text
	number_of_page = int(number_of_page.split()[-1])


	for page in range(number_of_page):

		response = requests.get(urlnext+(str(page*20)))
		html = response.content

		soup = BeautifulSoup(html, "html.parser")

		for review in soup.findAll("div", {"class": "review review--with-sidebar"}):
			if (review.find("a", {"class": "user-display-name"}) != None):
				userRatingDic[(review.find("a", {"class": "user-display-name"})["href"])] = review.find("meta", {"itemprop": "ratingValue"})["content"]
		print ("finished scraping page" + str(page))

	userRatingDicList.append(userRatingDicList)
	filteredDict = {k: v for k,v in userRatingDic.items() if v == "5.0"}
	filteredDictList.append(filteredDict)

#Getting commonUser from all entry in filteredDictList
try:
	commonUser = reduce(lambda x, y: x.keys() & y.keys(), filteredDictList)
except AttributeError:
	print("********************")
	print ("No Common User Found!")
	print("********************")
	sys.exit()

if len(commonUser) == 0:
	print("********************")
	print ("No Common User Found!")
	print("********************")
	sys.exit()	

#Write to terminal output
print("********************")
print("Common user are:")
for user in commonUser:
	print(user)
print("********************")


#Writing to output file
fileName = "Scraped_resturants_" + "_".join(sys.argv[1:])

out = open(fileName, 'w+')
for user in commonUser:
	out.write(user + "\n")
out.close()
