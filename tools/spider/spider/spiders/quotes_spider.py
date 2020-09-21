
import scrapy


# class QuotesSpider(scrapy.Spider):
#     name = "quotes"
#
#     def start_requests(self):
#         urls = [
#             'http://quotes.toscrape.com/page/1/',
#             'http://quotes.toscrape.com/page/2/',
#         ]
#         for url in urls:
#             yield scrapy.Request(url=url, callback=self.parse)
#
#     def parse(self, response):
#         page = response.url.split("/")[-2]
#         filename = 'quotes-%s.html' % page
#         with open(filename, 'wb') as f:
#             f.write(response.body)
#         self.log('Saved file %s' % filename)

#shortcut version:
class QuotesSpider(scrapy.Spider):
    name = "quotes"
    start_urls = [
        'http://quotes.toscrape.com/page/1/',
        'http://quotes.toscrape.com/page/2/',
    ]

    def parse(self, response):
        page = response.url.split("/")[-2]
        filename = 'quotes-%s.html' % page
        with open(filename, 'wb') as f:
            f.write(response.body)

# response.css('title::text').getall()
# response.css('title::text').get()
# response.css('title::text')[0].get()

# response.css('title::text').re(r'Quotes.*')
# ['Quotes to Scrape']

# response.css('title::text').re(r'Q\w+')
# ['Quotes']

# response.css('title::text').re(r'(\w+) to (\w+)')
# ['Quotes', 'Scrape']

# xpath_title = response.xpath('//title/text()').get()
# 'Quotes to Scrape'

# response.css("div.quote")
# quote = response.css("div.quote")[0]
# title = quote.css("span.text::text").get()

# author = quote.css("small.author::text").get()

# Given that the tags are a list of strings, we can use the .getall() method to get all of them:
# tags = quote.css("div.tags a.tag::text").getall()

# Having figured out how to extract each bit, we can now iterate over all the quotes elements and put them together into a Python dictionary:
for quote in response.css("div.quote"):
        text = quote.css("span.text::text").get()
        author = quote.css("small.author::text").get()
        tags = quote.css("div.tags a.tag::text").getall()
        print(dict(text=text, author=author, tags=tags))
# {'tags': ['change', 'deep-thoughts', 'thinking', 'world'], 'author': 'Albert Einstein', 'text': '“The world as we have created it is a process of our thinking. It cannot be changed without changing our thinking.”'}
# {'tags': ['abilities', 'choices'], 'author': 'J.K. Rowling', 'text': '“It is our choices, Harry, that show what we truly are, far more than our abilities.”'}
#    ... a few more of these, omitted for brevity