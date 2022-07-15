
import argparse
from crawler import crawl_page
from scraper import Post
import config_mongdb


if __name__ == "__main__":

    # the endpoint for the posts lookup
    ENDPOINT = "https://m.facebook.com/search/posts/"

    # Setting up the arg parser to parse argument when the script called 
    parser = argparse.ArgumentParser(prog="FACEBOOK COLLECTOR",description='Collect facebook posts related to a specific subject.')
    parser.add_argument("-s","--subject",default="le décès du président Jacques Chirac") # for subject selection 
    parser.add_argument("-f","--file",default=None)

    print("Connecting to DB ...")
    db = config_mongdb.get_cnx_database()
    
    args = parser.parse_args()
    if args.file:
        print(f"Scraping data from {args.file}")
        with open(args.file,"r") as file:
            page_source = file. read()
    else:
        print(f"Starting Crawling Process for topic = {args.subject}")
        url = f"{ENDPOINT}?q={args.subject}&source=filter&isTrending=0&tsid"
        page_source = crawl_page(url)
    
    

    print("Extracing and Saving data to DB ...")
    for post in Post.scrape_posts(page_source):
        post.serialize() # serialize the object
        print(post.data)
        post.save(db) # save to the database DB

    print("Finished Successfully !")

