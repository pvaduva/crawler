import sys
import os
import errno
import re
from sets import Set
from collections import defaultdict

class Parser():
    name = "jeny"
    docker_images = Set()
    allowed_domains = ["jenkins.onap.org"]
    arrLines = []
    indexArr = 0
    start_urls = (
        'https://jenkins.onap.org//view/docker/',
    )
    BASE_URL = "https://jenkins.onap.org/"
    dock_dict = defaultdict()


    def parse_job(self):
        for filename in os.listdir('jobs'):
            print('\n')
            print(filename)
            with open(os.path.join('jobs', filename), 'r') as content_file:
                strArr = content_file.read()
                dep = ""
                locked = False
                self.arrLines = strArr.splitlines()
                dock_set = Set()
                for j, x in enumerate(self.arrLines):
                    if all(z in x for z in ["Step", "FROM"]):
                        for i, y in enumerate(x.split()):
                            if y == "FROM":
                                dep = x.split()[i+1].encode("ascii")
                    elif "Successfully tagged" in x:
                        locked = True
                        for i, y in enumerate(x.split()):
                            if y == "tagged":
                                dep = dep +" --> " + x.split()[i+1].encode("ascii")
                                self.docker_images.add(re.sub("nexus3.onap.org:1000\d\/", "", dep))
                                dock_set.add(re.sub("nexus3.onap.org:1000\d\/", "", dep))
                                print(dep)
                    elif all(z in x for z in ['Downloaded', 'newer', 'image', 'for']):
                        for i, y in enumerate(x.split()):
                            if y == 'for':
                                dep = x.split()[i+1].encode("ascii")
                                print(dep)
                    elif all(z in x for z in ['DOCKER>', 'Pushed']):
                        locked = True
                        for i, y in enumerate(x.split()):
                            if y == "Pushed":
                                dep = dep +" --> " + x.split()[i+1].encode("ascii")
                                self.docker_images.add(re.sub("nexus3.onap.org:1000\d\/", "", dep))
                                dock_set.add(re.sub("nexus3.onap.org:1000\d\/", "", dep))
                                print(dep)
                    elif all(z in x for z in ['REPOSITORY', 'TAG', 'IMAGE ID', 'CREATED', 'SIZE']) and not locked:
                       self.indexArr  = j + 1
                       self.parse_docker(filename, dock_set)
                if filename.split('-')[0] in self.dock_dict:
                    self.dock_dict[filename.split('-')[0]].update(dock_set)
                else:
                    self.dock_dict[filename.split('-')[0]] = dock_set

    def parse_docker(self, filename, dock_set):
        dep = ''
        for x in self.arrLines[self.indexArr:]:
            if 'Pushing' not in x:
                dep = x.split()[0] + ' --> ' + dep
            else:
                self.docker_images.add(re.sub("nexus3.onap.org:1000\d\/", "", dep))
                dock_set.add(re.sub("nexus3.onap.org:1000\d\/", "", dep))
                print(dep)
                return

    def closed(self):
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
            f.write(k)
            print(k)
            for p in projects[k]:
                line = p.split()
                counter+=1
                print("{0}".format(counter) + ' ' + p)
                f.write('\n')
                f.write("{0}".format(counter) + ' ' + p)
            print("\n")
            print("\n")
            f.write('\n')
            f.write('\n')
        f.close()
        counter = 0
        with open("dict", "w+") as f:
            for project in self.dock_dict:
                f.write(project)
                f.write('\n')
                f.write('\n')
                for docker_dep in self.dock_dict[project]:
                    counter+=1
                    f.write('{0}'.format(counter) + ' ' + docker_dep)
                    f.write('\n')
                f.write('\n')

if __name__ == '__main__':
    parser = Parser()
    parser.parse_job()
    parser.closed() 
