import urllib
import urllib2
import re
try:
    import json
except ImportError:
    try:
        import simplejson as json
    except ImportError:
        raise ImportError("Need a json decoder")


def get_oembed(url, **kwargs):
    """
    Gets oEmbed data from Embedly
    """
    ACCEPTED_ARGS = ['maxwidth', 'maxheight', 'format', 'wmode']

    api_url = 'http://api.embed.ly/1/oembed?'

    params = {'url':url }

    for key, value in kwargs.items():
        if key not in ACCEPTED_ARGS:
            raise ValueError("Invalid Argument %s" % key)
        params[key] = value

    oembed_call = "%s%s" % (api_url, urllib.urlencode(params))

    return json.loads(urllib2.urlopen(oembed_call).read())

embedly_video_re = re.compile("http://(.*youtube\.com/watch.*|.*\.youtube\.com/v/.*|youtu\.be/.*|.*\.youtube\.com/user/.*|.*\.youtube\.com/.*#.*/.*|m\.youtube\.com/watch.*|m\.youtube\.com/index.*|.*\.youtube\.com/profile.*|.*justin\.tv/.*|.*justin\.tv/.*/b/.*|.*justin\.tv/.*/w/.*|www\.ustream\.tv/recorded/.*|www\.ustream\.tv/channel/.*|www\.ustream\.tv/.*|qik\.com/video/.*|qik\.com/.*|qik\.ly/.*|.*revision3\.com/.*|.*\.dailymotion\.com/video/.*|.*\.dailymotion\.com/.*/video/.*|www\.collegehumor\.com/video:.*|.*twitvid\.com/.*|www\.break\.com/.*/.*|vids\.myspace\.com/index\.cfm\?fuseaction=vids\.individual&videoid.*|www\.myspace\.com/index\.cfm\?fuseaction=.*&videoid.*|www\.metacafe\.com/watch/.*|www\.metacafe\.com/w/.*|blip\.tv/file/.*|.*\.blip\.tv/file/.*|video\.google\.com/videoplay\?.*|.*revver\.com/video/.*|video\.yahoo\.com/watch/.*/.*|video\.yahoo\.com/network/.*|.*viddler\.com/explore/.*/videos/.*|liveleak\.com/view\?.*|www\.liveleak\.com/view\?.*|animoto\.com/play/.*|dotsub\.com/view/.*|www\.overstream\.net/view\.php\?oid=.*|www\.livestream\.com/.*|www\.worldstarhiphop\.com/videos/video.*\.php\?v=.*|worldstarhiphop\.com/videos/video.*\.php\?v=.*|teachertube\.com/viewVideo\.php.*|www\.teachertube\.com/viewVideo\.php.*|www1\.teachertube\.com/viewVideo\.php.*|www2\.teachertube\.com/viewVideo\.php.*|bambuser\.com/v/.*|bambuser\.com/channel/.*|bambuser\.com/channel/.*/broadcast/.*|www\.schooltube\.com/video/.*/.*|bigthink\.com/ideas/.*|bigthink\.com/series/.*|sendables\.jibjab\.com/view/.*|sendables\.jibjab\.com/originals/.*|www\.xtranormal\.com/watch/.*|dipdive\.com/media/.*|dipdive\.com/member/.*/media/.*|dipdive\.com/v/.*|.*\.dipdive\.com/media/.*|.*\.dipdive\.com/v/.*|v\.youku\.com/v_show/.*\.html|v\.youku\.com/v_playlist/.*\.html|www\.snotr\.com/video/.*|snotr\.com/video/.*|video\.jardenberg\.se/.*|www\.whitehouse\.gov/photos-and-video/video/.*|www\.whitehouse\.gov/video/.*|wh\.gov/photos-and-video/video/.*|wh\.gov/video/.*|www\.hulu\.com/watch.*|www\.hulu\.com/w/.*|hulu\.com/watch.*|hulu\.com/w/.*|.*crackle\.com/c/.*|www\.fancast\.com/.*/videos|www\.funnyordie\.com/videos/.*|www\.funnyordie\.com/m/.*|funnyordie\.com/videos/.*|funnyordie\.com/m/.*|www\.vimeo\.com/groups/.*/videos/.*|www\.vimeo\.com/.*|vimeo\.com/groups/.*/videos/.*|vimeo\.com/.*|vimeo\.com/m/#/.*|www\.ted\.com/talks/.*\.html.*|www\.ted\.com/talks/lang/.*/.*\.html.*|www\.ted\.com/index\.php/talks/.*\.html.*|www\.ted\.com/index\.php/talks/lang/.*/.*\.html.*|.*nfb\.ca/film/.*|www\.thedailyshow\.com/watch/.*|www\.thedailyshow\.com/full-episodes/.*|www\.thedailyshow\.com/collection/.*/.*/.*|movies\.yahoo\.com/movie/.*/video/.*|movies\.yahoo\.com/movie/.*/trailer|movies\.yahoo\.com/movie/.*/video|www\.colbertnation\.com/the-colbert-report-collections/.*|www\.colbertnation\.com/full-episodes/.*|www\.colbertnation\.com/the-colbert-report-videos/.*|www\.comedycentral\.com/videos/index\.jhtml\?.*|www\.theonion\.com/video/.*|theonion\.com/video/.*|wordpress\.tv/.*/.*/.*/.*/|www\.traileraddict\.com/trailer/.*|www\.traileraddict\.com/clip/.*|www\.traileraddict\.com/poster/.*|www\.escapistmagazine\.com/videos/.*|www\.trailerspy\.com/trailer/.*/.*|www\.trailerspy\.com/trailer/.*|www\.trailerspy\.com/view_video\.php.*|www\.atom\.com/.*/.*/|fora\.tv/.*/.*/.*/.*|www\.spike\.com/video/.*|www\.gametrailers\.com/video/.*|gametrailers\.com/video/.*|www\.koldcast\.tv/video/.*|www\.koldcast\.tv/#video:.*|techcrunch\.tv/watch.*|techcrunch\.tv/.*/watch.*|mixergy\.com/.*|video\.pbs\.org/video/.*|www\.zapiks\.com/.*|tv\.digg\.com/diggnation/.*|tv\.digg\.com/diggreel/.*|tv\.digg\.com/diggdialogg/.*|www\.trutv\.com/video/.*|www\.nzonscreen\.com/title/.*|nzonscreen\.com/title/.*|app\.wistia\.com/embed/medias/.*|https://app\.wistia\.com/embed/medias/.*|hungrynation\.tv/.*/episode/.*|www\.hungrynation\.tv/.*/episode/.*|hungrynation\.tv/episode/.*|www\.hungrynation\.tv/episode/.*|indymogul\.com/.*/episode/.*|www\.indymogul\.com/.*/episode/.*|indymogul\.com/episode/.*|www\.indymogul\.com/episode/.*|channelfrederator\.com/.*/episode/.*|www\.channelfrederator\.com/.*/episode/.*|channelfrederator\.com/episode/.*|www\.channelfrederator\.com/episode/.*|tmiweekly\.com/.*/episode/.*|www\.tmiweekly\.com/.*/episode/.*|tmiweekly\.com/episode/.*|www\.tmiweekly\.com/episode/.*|99dollarmusicvideos\.com/.*/episode/.*|www\.99dollarmusicvideos\.com/.*/episode/.*|99dollarmusicvideos\.com/episode/.*|www\.99dollarmusicvideos\.com/episode/.*|ultrakawaii\.com/.*/episode/.*|www\.ultrakawaii\.com/.*/episode/.*|ultrakawaii\.com/episode/.*|www\.ultrakawaii\.com/episode/.*|barelypolitical\.com/.*/episode/.*|www\.barelypolitical\.com/.*/episode/.*|barelypolitical\.com/episode/.*|www\.barelypolitical\.com/episode/.*|barelydigital\.com/.*/episode/.*|www\.barelydigital\.com/.*/episode/.*|barelydigital\.com/episode/.*|www\.barelydigital\.com/episode/.*|threadbanger\.com/.*/episode/.*|www\.threadbanger\.com/.*/episode/.*|threadbanger\.com/episode/.*|www\.threadbanger\.com/episode/.*|vodcars\.com/.*/episode/.*|www\.vodcars\.com/.*/episode/.*|vodcars\.com/episode/.*|www\.vodcars\.com/episode/.*|confreaks\.net/videos/.*|www\.confreaks\.net/videos/.*|video\.allthingsd\.com/video/.*|aniboom\.com/animation-video/.*|www\.aniboom\.com/animation-video/.*|clipshack\.com/Clip\.aspx\?.*|www\.clipshack\.com/Clip\.aspx\?.*|grindtv\.com/.*/video/.*|www\.grindtv\.com/.*/video/.*|ifood\.tv/recipe/.*|ifood\.tv/video/.*|ifood\.tv/channel/user/.*|www\.ifood\.tv/recipe/.*|www\.ifood\.tv/video/.*|www\.ifood\.tv/channel/user/.*|logotv\.com/video/.*|www\.logotv\.com/video/.*|lonelyplanet\.com/Clip\.aspx\?.*|www\.lonelyplanet\.com/Clip\.aspx\?.*|streetfire\.net/video/.*\.htm.*|www\.streetfire\.net/video/.*\.htm.*|trooptube\.tv/videos/.*|www\.trooptube\.tv/videos/.*|www\.godtube\.com/featured/video/.*|godtube\.com/featured/video/.*|www\.godtube\.com/watch/.*|godtube\.com/watch/.*|www\.tangle\.com/view_video.*|mediamatters\.org/mmtv/.*|www\.clikthrough\.com/theater/video/.*|espn\.go\.com/video/clip.*|espn\.go\.com/.*/story.*|abcnews\.com/.*/video/.*|abcnews\.com/video/playerIndex.*|washingtonpost\.com/wp-dyn/.*/video/.*/.*/.*/.*|www\.washingtonpost\.com/wp-dyn/.*/video/.*/.*/.*/.*|www\.boston\.com/video.*|boston\.com/video.*|www\.facebook\.com/photo\.php.*|www\.facebook\.com/video/video\.php.*|www\.facebook\.com/v/.*|cnbc\.com/id/.*\?.*video.*|www\.cnbc\.com/id/.*\?.*video.*|cnbc\.com/id/.*/play/1/video/.*|www\.cnbc\.com/id/.*/play/1/video/.*|cbsnews\.com/video/watch/.*|www\.google\.com/buzz/.*/.*/.*|www\.google\.com/buzz/.*|www\.google\.com/profiles/.*|google\.com/buzz/.*/.*/.*|google\.com/buzz/.*|google\.com/profiles/.*|www\.cnn\.com/video/.*|edition\.cnn\.com/video/.*|money\.cnn\.com/video/.*|today\.msnbc\.msn\.com/id/.*/vp/.*|www\.msnbc\.msn\.com/id/.*/vp/.*|www\.msnbc\.msn\.com/id/.*/ns/.*|today\.msnbc\.msn\.com/id/.*/ns/.*|multimedia\.foxsports\.com/m/video/.*/.*|msn\.foxsports\.com/video.*|www\.globalpost\.com/video/.*|www\.globalpost\.com/dispatch/.*|guardian\.co\.uk/.*/video/.*/.*/.*/.*|www\.guardian\.co\.uk/.*/video/.*/.*/.*/.*|bravotv\.com/.*/.*/videos/.*|www\.bravotv\.com/.*/.*/videos/.*|video\.nationalgeographic\.com/.*/.*/.*\.html|dsc\.discovery\.com/videos/.*|animal\.discovery\.com/videos/.*|health\.discovery\.com/videos/.*|investigation\.discovery\.com/videos/.*|military\.discovery\.com/videos/.*|planetgreen\.discovery\.com/videos/.*|science\.discovery\.com/videos/.*|tlc\.discovery\.com/videos/.*)", re.I)

embedly_pic_re = re.compile("http://(.*yfrog\..*/.*|tweetphoto\.com/.*|www\.flickr\.com/photos/.*|flic\.kr/.*|twitpic\.com/.*|www\.twitpic\.com/.*|twitpic\.com/photos/.*|www\.twitpic\.com/photos/.*|.*imgur\.com/.*|.*\.posterous\.com/.*|post\.ly/.*|twitgoo\.com/.*|i.*\.photobucket\.com/albums/.*|s.*\.photobucket\.com/albums/.*|phodroid\.com/.*/.*/.*|www\.mobypicture\.com/user/.*/view/.*|moby\.to/.*|xkcd\.com/.*|www\.xkcd\.com/.*|imgs\.xkcd\.com/.*|www\.asofterworld\.com/index\.php\?id=.*|www\.asofterworld\.com/.*\.jpg|asofterworld\.com/.*\.jpg|www\.qwantz\.com/index\.php\?comic=.*|23hq\.com/.*/photo/.*|www\.23hq\.com/.*/photo/.*|.*dribbble\.com/shots/.*|drbl\.in/.*|.*\.smugmug\.com/.*|.*\.smugmug\.com/.*#.*|emberapp\.com/.*/images/.*|emberapp\.com/.*/images/.*/sizes/.*|emberapp\.com/.*/collections/.*/.*|emberapp\.com/.*/categories/.*/.*/.*|embr\.it/.*|picasaweb\.google\.com.*/.*/.*#.*|picasaweb\.google\.com.*/lh/photo/.*|picasaweb\.google\.com.*/.*/.*|dailybooth\.com/.*/.*|brizzly\.com/pic/.*|pics\.brizzly\.com/.*\.jpg|img\.ly/.*|www\.tinypic\.com/view\.php.*|tinypic\.com/view\.php.*|www\.tinypic\.com/player\.php.*|tinypic\.com/player\.php.*|www\.tinypic\.com/r/.*/.*|tinypic\.com/r/.*/.*|.*\.tinypic\.com/.*\.jpg|.*\.tinypic\.com/.*\.png|meadd\.com/.*/.*|meadd\.com/.*|.*\.deviantart\.com/art/.*|.*\.deviantart\.com/gallery/.*|.*\.deviantart\.com/#/.*|fav\.me/.*|.*\.deviantart\.com|.*\.deviantart\.com/gallery|.*\.deviantart\.com/.*/.*\.jpg|.*\.deviantart\.com/.*/.*\.gif|.*\.deviantart\.net/.*/.*\.jpg|.*\.deviantart\.net/.*/.*\.gif|plixi\.com/p/.*|plixi\.com/profile/home/.*|plixi\.com/.*|www\.fotopedia\.com/.*/.*|fotopedia\.com/.*/.*|photozou\.jp/photo/show/.*/.*|photozou\.jp/photo/photo_only/.*/.*|instagr\.am/p/.*|skitch\.com/.*/.*/.*|img\.skitch\.com/.*|https://skitch\.com/.*/.*/.*|https://img\.skitch\.com/.*|share\.ovi\.com/media/.*/.*|www\.questionablecontent\.net/|questionablecontent\.net/|www\.questionablecontent\.net/view\.php.*|questionablecontent\.net/view\.php.*|questionablecontent\.net/comics/.*\.png|www\.questionablecontent\.net/comics/.*\.png|picplz\.com/user/.*/pic/.*/|twitrpix\.com/.*|.*\.twitrpix\.com/.*|www\.someecards\.com/.*/.*|someecards\.com/.*/.*|some\.ly/.*|www\.some\.ly/.*|pikchur\.com/.*|achewood\.com/.*|www\.achewood\.com/.*|achewood\.com/index\.php.*|www\.achewood\.com/index\.php.*)", re.I)

category_id = {'link': 9, 'pic': 10, 'video': 11}

def scrape(url):
    data = {'category': 'link'}
    keys = None
    oembed = None
    if embedly_video_re.match(url):
        oembed = get_oembed(url, maxwidth=640, wmode='transparent')
        if oembed['type'] == 'video':
            data['category'] = 'video'
            keys = ('html','width','height','thumbnail_url','thumbnail_width','thumbnail_height')

    elif embedly_pic_re.match(url):
        oembed = get_oembed(url)
        if oembed['type'] == 'photo':
            data['category'] = 'pic'
            keys = ('url','width','height','thumbnail_url','thumbnail_width','thumbnail_height')

    if keys: 
        for key in keys: 
            try:
                data[key] = oembed[key]
            except KeyError:
                pass

    data['category_id'] = category_id[data['category']]
    return data
        
