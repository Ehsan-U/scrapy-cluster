from typing import Iterable, List
from urllib.parse import parse_qs, urlencode, urlparse
import scrapy
from scrapy.http import Request, Response
from scrapy_redis.spiders import RedisSpider



class TruePeopleSearch(RedisSpider):
    name = "truepeoplesearch"
    redis_key = "people:start_urls"


    def parse(self, response: Response):
        """
        parse the results page
        """
        persons = response.xpath("//div[contains(@class, 'card-summary')]//div[contains(@class, 'hidden-mobile')]/a[contains(@href, '/find/person')]")
        if persons:
            for person in persons[:1]:
                link = person.xpath("./@href").get()
                url = response.urljoin(link)
                yield scrapy.Request(url, callback=self.parse_person)
        else:
            name = parse_qs(urlparse(str(response.url)).query).get("name")[0]
            yield {
                "name": name,
                "age": None,
                "birth_year": None,
                "street": None,
                "city": None,
                "region": None,
                "zipcode": None,
                "phone_1": None,
                "phone_2": None,
                "phone_3": None,
                "phone_4": None,
                "phone_5": None,
            }


    def parse_person(self, response: Response):
        """ 
        parse the person profile page 
        """
        item = {
            "name": response.xpath("//h1/text()").get(),
            "age": response.xpath("//span[contains(text(), 'Born')]/text()").re_first("(?:Age\s)(\d+)"),
            "birth_year": response.xpath("//span[contains(text(), 'Born')]/text()").re_first("\d{4}"),
            "street": response.xpath("//div[@itemprop='homeLocation']//span[@itemprop='streetAddress']/text()").get(),
            "city": response.xpath("//div[@itemprop='homeLocation']//span[@itemprop='addressLocality']/text()").get(),
            "region": response.xpath("//div[@itemprop='homeLocation']//span[@itemprop='addressRegion']/text()").get(),
            "zipcode": response.xpath("//div[@itemprop='homeLocation']//span[@itemprop='postalCode']/text()").get(),
            "phone_1": None,
            "phone_2": None,
            "phone_3": None,
            "phone_4": None,
            "phone_5": None,
        }

        phones = list(set(response.xpath("//span[@itemprop='telephone']/text()").getall()))
        for idx, phone in enumerate(phones, start=1):
            item[f"phone_{idx}"] = phone
            if idx == 5:
                break
        
        return item

    
    