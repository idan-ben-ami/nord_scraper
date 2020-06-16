import scrapy


SECTIONS = [
    # 'acknowledgment',
    'synonyms',
    'general-discussion',
    'symptoms',
    'causes',
    'affected-populations',
    'related-disorders',
    'diagnosis',
    'standard-therapies',
    'investigational-therapies',
    # 'resources',
    # 'supporting-organizations',
    'references',
    'years_published',
    # 'disclaimer'
]


class NordSpider(scrapy.Spider):
    name = 'nords'
    start_urls = ['https://rarediseases.org/for-patients-and-families/information-resources/rare-disease-information/']
    custom_settings = {
        "FEED_URI": "nord_%(time)s.csv",
        "FEED_FORMAT": "csv"
    }

    def parse1(self, response):
        for title in response.css('.post-header>h2'):
            yield {'title': title.css('a ::text').get()}

        for next_page in response.css('a.next-posts-link'):
            yield response.follow(next_page, self.parse)

    def parse_article(self, response, name):
        result = {"name": name}
        for section in response.css("div.rdr-box"):
            sec_name = section.css("::attr(id)").extract_first()
            if sec_name not in SECTIONS:
                continue
            text = section.css("::text").extract()[2:]
            # Some text handling logic?
            result[sec_name] = text
        yield result

    def parse(self, response):
        for article in response.css("article"):  # .css("a::attr(href)"):
            article_url = article.css("a::attr(href)").extract_first()
            article_name = article.css("a::text").extract_first()
            yield scrapy.Request(response.urljoin(article_url), callback=self.parse_article,
                                 cb_kwargs={"name": article_name})

        next_page = response.css(".pagination").css(".next::attr(href)").extract_first()
        if next_page:
            yield scrapy.Request(response.urljoin(next_page), callback=self.parse)
