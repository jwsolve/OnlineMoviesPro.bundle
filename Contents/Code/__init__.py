######################################################################################
#
#	OnlineMovies.Pro - v1
#
######################################################################################

TITLE = "OnlineMovies.pro"
PREFIX = "/video/onlinemoviespro"
ART = "art-default.jpg"
ICON = "icon-default.png"
ICON_LIST = "icon-list.png"
ICON_COVER = "icon-cover.png"
ICON_SEARCH = "icon-search.png"
ICON_NEXT = "icon-next.png"
ICON_MOVIES = "icon-movies.png"
ICON_SERIES = "icon-series.png"
BASE_URL = "http://onlinemovies.pro"
CATEGORY_URL = "http://onlinemovies.pro/category"
CATEGORIES_URL = "http://onlinemovies.pro/categories/"
SEARCH_URL = 'http://onlinemovies.pro/'

######################################################################################
# Set global variables

def Start():

	ObjectContainer.title1 = TITLE
	ObjectContainer.art = R(ART)
	DirectoryObject.thumb = R(ICON_COVER)
	DirectoryObject.art = R(ART)
	VideoClipObject.thumb = R(ICON_COVER)
	VideoClipObject.art = R(ART)
	
	HTTP.CacheTime = CACHE_1HOUR
	HTTP.Headers['User-Agent'] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36"
	HTTP.Headers['Referer'] = "http://onlinemovies.pro/"
	
######################################################################################
# Menu hierarchy

@handler(PREFIX, TITLE, art=ART, thumb=ICON)
def MainMenu():

	oc = ObjectContainer()
	oc.add(InputDirectoryObject(key = Callback(Search), title='Search', summary='Search OnlineMovies.Pro', prompt='Search for...'))
	channel_page = HTML.ElementFromURL(CATEGORIES_URL)
	channels = channel_page.xpath("//ul[@class='listing-cat']/li")
	for each in channels:
		url = each.xpath("./a/@title")[0]
		title = each.xpath("./a/@title")[0]
		thumb = each.xpath("./img/@src")[0]
		url = url.replace('%2b','-')
		url = url.replace(' ', '-')
		oc.add(DirectoryObject(key = Callback(ShowCategory, title = title, category = url, page_count = 1), title = title, thumb = thumb))

	return oc

######################################################################################
# Creates page url from category and creates objects from that page

@route(PREFIX + "/showcategory")	
def ShowCategory(title, category, page_count):

	oc = ObjectContainer(title1 = title)
	if str(page_count) == "1":
		page_data = HTML.ElementFromURL(CATEGORY_URL + '/' + str(category) + '/?filtre=date')
	else:
		page_data = HTML.ElementFromURL(CATEGORY_URL + '/' + str(category) + '/page/' + str(page_count) + '/')

	for each in page_data.xpath("//ul[@class='listing-videos listing-tube']/li"):
		url = each.xpath("./a/@href")[0]
		try:
			title = each.xpath("./img/@title")[0]
		except:
			title = each.xpath("./img/@alt")[0]
		thumb = each.xpath("./img/@src")[0]
		if str(category) == "Tv":
			oc.add(DirectoryObject(
				key = Callback(ShowEpisodes, title = title, url = url),
				title = title,
				thumb = Resource.ContentsOfURLWithFallback(url = thumb, fallback='icon-series.png')
				)
			)
		else:
			oc.add(DirectoryObject(
				key = Callback(EpisodeDetail, title = title, url = url),
				title = title,
				thumb = Resource.ContentsOfURLWithFallback(url = thumb, fallback='icon-cover.png')
				)
			)

	oc.add(NextPageObject(
		key = Callback(ShowCategory, title = category, category = category, page_count = int(page_count) + 1),
		title = "Next...",
		thumb = R(ICON_NEXT)
			)
		)
	
	return oc

######################################################################################
# Creates page url from tv episodes and creates objects from that page

@route(PREFIX + "/showepisodes")	
def ShowEpisodes(title, url):

	oc = ObjectContainer(title1 = title)
	page_data = HTML.ElementFromURL(url)
	for each in page_data.xpath("//table[@class='table']/tbody/tr"):
		url = each.xpath("./td[@class='entry2']/a/@href")[0].strip()
		title = each.xpath("./td[@class='entry']/text()")[0].strip()
		thumb = each.xpath("./td[@class='entry2']/a/img/@src")[0]

		oc.add(DirectoryObject(
			key = Callback(EpisodeDetail, title = title, url = url),
			title = title,
			thumb = Resource.ContentsOfURLWithFallback(url = thumb, fallback='icon-cover.png')
			)
		)
	
	return oc

######################################################################################
# Gets metadata and google docs link from episode page. Checks for trailer availablity.

@route(PREFIX + "/episodedetail")
def EpisodeDetail(title, url):
	
	oc = ObjectContainer(title1 = title)
	page_data = HTML.ElementFromURL(url)
	try:
		title = page_data.xpath("//div[@id='video']/h1/span/text()")[0]
	except:
		title = page_data.xpath("//div[@id='video']/h1/span/text()")
	thumb = page_data.xpath("//div[@id='video']/meta/@content")
	oc.add(VideoClipObject(
		url = url,
		title = title,
		thumb = Resource.ContentsOfURLWithFallback(url = thumb, fallback='icon-movies.png')
		)
	)	
	
	return oc

####################################################################################################
@route(PREFIX + "/search")
def Search(query):

	oc = ObjectContainer(title2='Search Results')
	data = HTTP.Request(SEARCH_URL + '?s=%s' % String.Quote(query, usePlus=True), headers="").content

	html = HTML.ElementFromString(data)

	for movie in html.xpath("//ul[@class='listing-videos listing-tube']/li"):
		url = movie.xpath("./a/@href")[0]
		try:
			title = movie.xpath("./img/@title")[0]
		except:
			title = movie.xpath("./img/@alt")[0]
		thumb = movie.xpath("./img/@src")[0]
		title = url
		oc.add(DirectoryObject(
				key = Callback(EpisodeDetail, title = title, url = url),
				title = title,
				thumb = Resource.ContentsOfURLWithFallback(url = thumb, fallback='icon-cover.png')
				)
		)

	return oc