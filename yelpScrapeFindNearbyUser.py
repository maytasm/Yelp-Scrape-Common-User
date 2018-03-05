from bs4 import BeautifulSoup
import requests
from functools import reduce
import sys
import re
from geopy.geocoders import Nominatim
from geopy.distance import vincenty
from time import sleep

MY_LOCATION = geolocator.geocode("San Francisco, CA, USA", timeout=10)
MY_LAT_LONG = (MY_LOCATION.latitude, MY_LOCATION.longitude)

geolocator = Nominatim()

locationResultCache = {}

def isUserCloseby(city):
	isCloseby = locationResultCache.get(city)
	if (isCloseby is None):
		userLocation = geolocator.geocode(city, timeout=120)
		if (userLocation is None):
			print city
			return False
		userLatLong = (userLocation.latitude, userLocation.longitude)
		if vincenty(userLatLong, MY_LAT_LONG).miles < 50:
			locationResultCache[city] = True
			return True
		else:
			locationResultCache[city] = False
			return False
	else:
		return isCloseby

#Get rest from input
if (len(sys.argv[1:]) != 0 ):
	print ("Listed of resturants input are: " + ", ".join(sys.argv[1:]))
	bizNameList = sys.argv[1:]
#Get rest from pre-inputed
else:
	bizNameList = ["michele-coulon-dessertier-la-jolla"]
	print ("Listed of resturants input are: " + ", ".join(bizNameList))

userRatingDicList = []
nearbyUsers = []

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
			userCity = review.find("li", {"class": "user-location"}).find('b').text
			if (review.find("a", {"class": "user-display-name"}) != None):
				userRatingDic[(review.find("a", {"class": "user-display-name"})["href"])] = review.find("div", {"class": "i-stars"})["title"]
		print ("finished scraping page" + str(page))

	userRatingDicList.append(userRatingDic)
	starEqualUsers = {k: v for k,v in userRatingDic.items() if v == "5.0 star rating"}
	nearbyUsers.extend(starEqualUsers)

if len(nearbyUsers) == 0:
	print("********************")
	print ("No Nearby User Found!")
	print("********************")
	sys.exit()	

#Write to terminal output
print("********************")
print("Nearby user are:")
for user in nearbyUsers:
	print(user)
print("********************")

userReviewDicList = []
nearbyResturants = []

for user in nearbyUsers:
	userReviewDic = {}
	startIndex = user.find('=')
	userId = user[startIndex+1:]
	url = "https://www.yelp.com/user_details_reviews_self?userid=" + userId
	urlnext = url + "&rec_pagestart="
	response = requests.get(url)
	html = response.content
	soup = BeautifulSoup(html, "html.parser")
	number_of_page = soup.find("div", {"class": "page-of-pages arrange_unit arrange_unit--fill"}).text
	number_of_page = int(number_of_page.split()[-1])

	for page in range(number_of_page):
		sleep(2)
		response = requests.get(urlnext+(str(page*10)))
		html = response.content
		soup = BeautifulSoup(html, "html.parser")
		for review in soup.findAll("div", {"class": "review"}):
			bizName = review.find("a", {"class": "biz-name"})['href']
			star = review.find("div", {"class": "i-stars"})["title"]
			address = review.find("address").find("br")
			if (address != None):
				address = next(address.next_siblings)
			else:
				# For debug
				address = review.find("address").text.strip()
			address = address.strip().split(" ")
			if len(address) == 3:
				address = " ".join(address[:-1])
			else:
				address = " ".join(address)
			if (bizName != None and isUserCloseby(address)):
				userReviewDic[bizName] = star
		print ("finished scraping page" + str(page))

	userReviewDicList.append(userReviewDic)
	starEqualReviews = {k: v for k,v in userReviewDic.items() if v == "5.0 star rating"}
	nearbyResturants.extend(starEqualReviews)

nearbyResturants = set(nearbyResturants)

if len(nearbyResturants) == 0:
	print("********************")
	print ("No Nearby Resturants Found!")
	print("********************")
	sys.exit()	

#Write to terminal output
print("********************")
print("Nearby Resturants are:")
for rest in nearbyResturants:
	print(rest)
print("********************")

#Writing to output file
userFileName = "Scraped_users_" + "_".join(sys.argv[1:])
restFileName = "Scraped_resturants_" + "_".join(sys.argv[1:])

out = open(userFileName, 'w+')
for user in nearbyUsers:
	out.write(user + "\n")
out.close()

out = open(restFileName, 'w+')
for rest in nearbyResturants:
	out.write(rest + "\n")
out.close()
