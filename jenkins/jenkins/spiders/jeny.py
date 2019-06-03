# -*- coding: utf-8 -*-
import scrapy
import sys
from sets import Set


class JenySpider(scrapy.Spider):
    name = "jeny"
    docker_images = Set()
    allowed_domains = ["jenkins.onap.org"]
    start_urls = (
        'https://jenkins.onap.org//view/docker/',
    )
    BASE_URL = "https://jenkins.onap.org/"

#    def parse(self, response):
#        links = response.xpath('//div[@class="tabBar"]').css('a::attr(href)').extract()
#        for link in links:
##            print(link)
#            absolute_url = self.BASE_URL + link
#            yield scrapy.Request(absolute_url, callback=self.parse_tab)

    def parse(self, response):
        links = response.xpath('//table[@id="projectstatus"]').css('a::attr(href)').extract()
        for link in links:
            if str.__contains__(link.encode("ascii"), "lastSuccessfulBuild"):
                absolute_url = self.BASE_URL + link + "/consoleText"
#                print(absolute_url)
                yield scrapy.Request(absolute_url, callback=self.parse_job)

    def parse_job(self, response):
        str = response.xpath('//body').get() 
        dep = ""
        dep2 = ""
        for x in str.splitlines():
            if all(z in x for z in ["Step", "FROM"]):
#                self.docker_images.add(x.encode("ascii"))
                for i, y in enumerate(x.split()):
                    if y == "FROM":
                        dep = x.split()[i+1].encode("ascii")
#                self.docker_images.add(dep)
            if "Successfully tagged" in x:
#                print(x)
                for i, y in enumerate(x.split()):
                    if y == "tagged":
                        dep = dep +" --> " + x.split()[i+1].encode("ascii")
                        self.docker_images.add(dep)
#                        self.docker_images.add(x.split()[i+1].encode("ascii"))
#                        self.docker_images.add("\r\n")
            if "docker push " in x: 
                for i, y in enumerate(x.split()):
                    if y == "push ":
                        dep = dep + " --> " + x.split()[i+1].encode("ascii")
                        self.docker_images.add(dep)

    def closed(self, reason):
        f = open("dockerimages", "w+")
        for x in self.docker_images:
            f.write(x)
            f.write("\r\n")
        f.close()
 
#        for link in links:
#            absolute_url = self.BASE_URL + link
#            yield scrapy.Request(absolute_url, callback=self.parse_job)
#
#    def parse_job(self, response):
#        print(response.url)
