# -*- coding: utf-8 -*-
import scrapy
import sys
import re
from sets import Set


class JenySpider(scrapy.Spider):
    name = "jeny"
    docker_images = Set()
    allowed_domains = ["jenkins.onap.org"]
    arrLines = []
    indexArr = 0
    start_urls = (
        'https://jenkins.onap.org//view/docker/',
    )
    BASE_URL = "https://jenkins.onap.org/"

    def parse(self, response):
        links = response.xpath('//table[@id="projectstatus"]').css('a::attr(href)').extract()
        for link in links:
            if str.__contains__(link.encode("ascii"), "lastSuccessfulBuild"):
                absolute_url = self.BASE_URL + link + "/consoleText"
                yield scrapy.Request(absolute_url, callback=self.parse_job)

    def parse_job(self, response):
        strArr = response.body
        dep = ""
        self.arrLines = strArr.splitlines()
        for j, x in enumerate(self.arrLines):
            if all(z in x for z in ['REPOSITORY', 'TAG', 'IMAGE ID', 'CREATED', 'SIZE']):
               self.indexArr  = j + 1
               self.parse_docker()
            if all(z in x for z in ["Step", "FROM"]):
                for i, y in enumerate(x.split()):
                    if y == "FROM":
                        dep = x.split()[i+1].encode("ascii")
            if "Successfully tagged" in x:
                for i, y in enumerate(x.split()):
                    if y == "tagged":
                        dep = dep +" --> " + x.split()[i+1].encode("ascii")
                        self.docker_images.add(re.sub("nexus3.onap.org:1000\d\/", "", dep))

    def parse_docker(self):
        dep = ''
        for x in self.arrLines[self.indexArr:]:
            if 'Pushing' not in x and all(w in x for w in ['for', 'tag', 'int']):
                print(x)
                dep = x.split()[0] + ' --> ' + dep
            else:
                self.docker_images.add(re.sub("nexus3.onap.org:1000\d\/", "", dep))
                return
       

    def closed(self, reason):
        f = open("dockerimages", "w+")
        for x in self.docker_images:
            f.write(x)
            f.write("\r\n")
        f.close()
        lineArr = self.docker_images
        from sets import Set
        keysSet = Set()
        for l in lineArr:
            line = l.split()
            print(line[2])
            if line[2].startswith("onap"):
                startPos = 5
            else:
                startPos = 0
            if "dcaegen2" in line[2]:
                keysSet.add("dcaegen2")
                continue
            keysSet.add(line[2][startPos:min(n for n in [line[2].find('/', startPos, len(line[2])), line[2].find('-', startPos, len(line[2])), line[2].find(':', startPos, len(line[2]))] if n > 0)])
        projects = {}
        for k in keysSet:
            projects[k] = Set()
        for l in lineArr:
            line = l.split()
            if line[2].startswith("onap"):
                startPos = 5
            else:
                startPos = 0
            if "dcaegen2" in line[2]:
                projects["dcaegen2"].add(l)
                continue
            projects[line[2][startPos:min(n for n in [line[2].find('/', startPos, len(line[2])), line[2].find('-', startPos, len(line[2])), line[2].find(':', startPos, len(line[2]))] if n > 0)]].add(l)
        counter = 0
        f = open("graphs", "w+")
        for k in projects.keys():
            import networkx as nx
            import matplotlib.pyplot as plt
            G = nx.DiGraph()
            f.write(k)
            print(k)
            for p in projects[k]:
                line = p.split()
                G.add_edge(line[2], line[0])
                counter+=1
                print("{0}".format(counter) + ' ' + p)
                f.write('\n')
                f.write("{0}".format(counter) + ' ' + p)
            DG = G.to_directed()
            nx.draw_networkx(DG)
            print("\n")
            print("\n")
            f.write('\n')
            f.write('\n')
    	f.close()
