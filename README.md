# olx_scraper
Hi, this scraper get information from website www.olx.ua with help framework Scrapy
## Running all the stuff
1. Clone repo: `git clone https://github.com/Wadwadw/olx_scraper.git`
2. Create virtualenv, for example: `python3 -m venv venv` or `virtualenv -p python3 venv`
3. Activate it `source venv/bin/activate`
4. Install all the packages `pip install -r requirements.txt`
5. In file olx_scraper/spiders/scrape.py in line 16 change url what you need
6. Start scraper script `scrapy crawl scrape -o results.csv`
