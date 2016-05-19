import urllib
import json
import pafy
import unicodedata

class YoutubeInfoExtractor(object):

	def getTitle(self, video_id):
		text = self.getMetaData(video_id)['title']
		try:
			text = unicodedata.normalize('NFKD', 
				u"%s" % text).encode('ascii', 'ignore')
		except:
			text = "title not available"
		return text

	def getImage(self, video_id):
		return self.getMetaData(video_id)['thumbnail_url']

	def getStreamlink(self, video_id):
		stream = pafy.new(video_id, basic=False, gdata=False)
		return stream.getbestaudio(preftype='m4a').url_https

	def getInfo(self, video_id):
		#returns string[] { title, thumbnail, stream_url }
		if 'youtu' in video_id:
			video_id = video_id.split("watch?v=")[-1]
		if '&' in video_id:
			video_id = video_id.split('&')[0]
		data = self.getMetaData(video_id)

		info = []
		info.append( data['title'] )
		info.append( data['thumbnail_url'] )
		info.append( self.getStreamlink(video_id) )

		return info

	def getMetaData(self, video_id):
		link = "https://www.youtube.com/oembed?url=http://www.youtube.com/watch?v=" + video_id
		data = json.loads( urllib.urlopen(link).read() )
		return data

	def getSearchResults(self, query, byID=True):
		# Setup  Query
		if ' ' in query:
			query = query.replace(' ','_')
		query = urllib.quote_plus(query)
		q_url = 'https://youtube.com/results?search_query='
		text = urllib.urlopen(q_url+query).read()

		#Detect os for parsing
		if 'nt' in os.name:
			soup = bs4.BeautifulSoup(text,'html.parser')
		else:
			soup = bs4.BeautifulSoup(text,'lxml')

		#get results
		div = [d for d in soup.find_all('div') if d.has_attr('class') and 'yt-lockup-dismissable' in d['class'] ]
		results = []

		for d in div:
			image = d.find_all('img')[0]
			data  = image['src'] if not image.has_attr('data-thumb') else image['data-thumb']
			video_id = data.split('/')[-2]
			results.append(video_id)
