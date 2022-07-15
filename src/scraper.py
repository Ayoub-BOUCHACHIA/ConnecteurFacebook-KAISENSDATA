from bs4 import BeautifulSoup
import dateparser
from cssutils import parseStyle
import re
import json
from utils import convert_str_to_number







class Post(object):
    """
    Post class (model) that handles process, extracting and saving post data
    """

    COLLECTION_NAME = "posts" # the name of the collection where the data will be stored


    def __init__(self,document,data={}):
        self.document = document
        self.data = data
        self.type = json.loads(document.get("data-ft")).get("story_attachment_style")


    @staticmethod
    def scrape_posts(document):
        """
        scrape all the posts from the document and return Post objects
        this is a static method bcz it contains generic class behavior and it's not linked to the object instances.
        """
        soup = BeautifulSoup(document,features="lxml")
        return map(lambda x: Post(x),soup.find_all("div",{"data-sigil":'story-div story-popup-metadata feed-ufi-metadata'}))



    def get_publisher(self):
        anchors = self.document.select("header div:nth-child(2) div div div h3 a")
        if anchors:
            return {"publisherName":anchors[0].get_text(),"publisherAccount":anchors[0]["href"]}
        return None

    def get_post_text(self):
        spans = self.document.select("header + div div span")
        # span = self.document.find("span", {"data-sigil":"expose"})
        if spans:
            return spans[0].get_text()
        return None


    
    def get_media(self):
        if self.type == "photo" or self.type == "album":
            images = self.document.select("header + div + div i.img[role='img']")
            if images:
                imgs = []
                for img in images:
                    style = img.get("style")
                    bg_image = parseStyle(style).backgroundImage
                    img_url = re.findall(r'(https?://\S+)', bg_image)
                    imgs.append(img_url)
                return imgs
            return None
        if self.type == "share":
            anchors = self.document.select("div section a.touchable[target='_blank']")
            if anchors:
                return anchors[0].get("href")
            return None
        if self.type == "video_inline":
            videos = self.document.select("div section div[data-sigil='inlineVideo']")
            if videos:
                data_store = videos[0].get("data-store")
                url = json.loads(data_store).get("src")
                return url
            return None
        
            
    def get_reactions(self):
        # reactions = self.document.find("div",{"data-sigil":"reactions-sentence-container"})
        reactions = self.document.select("div[data-sigil='reactions-sentence-container'] > div")
        if reactions:
            try:
                reactions_count = convert_str_to_number(reactions[0].get_text().replace(",","."))
                return reactions_count
            except:
                return None
            
            
    def get_comments(self):
        comments = self.document.select("div[data-sigil='reactions-sentence-container'] + div span")
        if comments:
            comments_str = ''.join(comments[0].get_text().split()[:-1])
            try:
                comments_count = convert_str_to_number(comments_str.replace(",","."))
                return comments_count
            except:
                return None
    
    def get_shares(self):
        shares = self.document.select("div[data-sigil='reactions-sentence-container'] + div span:nth-child(2)")
        if shares:
            shares_str = ''.join(shares[0].get_text().split()[:-1])
            try:
                shares_count = convert_str_to_number(shares_str.replace(",","."))
                return shares_count
            except:
                return None

    def get_publish_date(self):
        abbr = self.document.find("header").find("abbr")
        if abbr:
            text_date = abbr.get_text()
            date = dateparser.parse(text_date)
            return date
        return None


    def serialize(self):
        """
        extract and return a json like format of the post data
        """
        self.data = {
            "type"      : self.type,
            "publisher" : self.get_publisher(),
            "text"      : self.get_post_text(),
            "media"     : self.get_media(),
            "publishDate":self.get_publish_date(),
            "shares"    : self.get_shares(),
            "comments"  : self.get_comments(),
            "reactions" : self.get_reactions()
        }
        return self.data
    
    
    def save(self,db):
        return db[Post.COLLECTION_NAME].insert_one(self.data)