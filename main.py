import bs4
from bs4 import BeautifulSoup as bs
import json
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import mechanize
import networkx as nx
import os

BASE_URL = "http://oldschool.runescape.wiki"
LIST_URL = "http://oldschool.runescape.wiki/w/Quests/List"
BR = mechanize.Browser()

QUEST_DICT = {}  # Dictionary with keys=quest name, elements=QuestNodes
QUEST_NAMES = {}  # Removed "(quest)" from all quest names

class QuestNode:
    def __init__(self):
        self.name = ''
        self.url = ''
        self.href = ''
        self.reqs = []

    def init(self, name, url, href, reqs):
        self.name = name
        self.url = url
        self.href = href
        self.reqs = reqs

    def setName(self, name):
        self.name = name

    def setHREF(self, href):
        self.href = href
        self.setURL(BASE_URL + href)

    def setURL(self, url):
        self.url = url

    def setReqs(self, reqs):
        self.reqs = reqs

    def addReq(self, quest):
        if quest not in self.reqs:
            print "\tAdded requirement " + quest.getName()
            self.reqs.append(quest)

    def removeReq(self, name):
        i = 0
        while i < len(self.reqs):
            req = self.reqs[i]
            if req.getName() == name:
                self.reqs.remove(req)
            else:
                i += 1

    def getName(self):
        return self.name

    def getURL(self):
        return self.url

    def getReqs(self):
        return self.reqs

    def getRecursiveReqs(self):
        if len(self.reqs) > 0:
            total = list(self.reqs)
            for req in total:
                total.extend(req.getRecursiveReqs())
            return total
        else:
            return []

    def removeDuplicates(self):
        for req in list(self.reqs):
            req.removeDuplicates()

        alreadySeen = []
        for req in list(self.getRecursiveReqs()):
            name = req.getName()
            if name in alreadySeen:
                self.removeReq(name)
            else:
                alreadySeen.append(name)

    def printReqs(self):
        if len(self.reqs) <= 0:
            print self.name
        else:
            print self.name
            for quest in self.reqs:
                reqs = quest.printReqsTabbed(1)
                if reqs is not None:
                    print '\t' + reqs

    def printReqsTabbed(self, numTabs):
        tabs = ''.join(['\t' for num in range(numTabs)])
        if len(self.reqs) <= 0:
            return self.name
        else:
            print tabs + self.name
            for quest in self.reqs:
                reqs = quest.printReqsTabbed(numTabs + 1)
                if reqs is not None:
                    print tabs + '\t' + reqs

class QuestNodeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, QuestNode):
            return {
                '_type': 'QuestNode',
                'name': obj.name,
                'url': obj.url,
                'href': obj.href,
                'reqs': obj.reqs
            }
        else:
            return super(QuestNodeEncoder, self).default(obj)

def getQuestTables(html):
    soup = bs(html, 'html5lib')

    tables = soup.findAll('tbody')
    tables = [tables[1], tables[3]]
    return tables

def getQuestList(table):
    for i in range(len(table.contents)):
        if i != 0 and i % 2 == 0:
            quest = QuestNode()
            quest.setName(table.contents[i].contents[1].contents[0].contents[0])
            quest.setHREF(table.contents[i].contents[1].contents[0].attrs[u'href'])
            global QUEST_DICT
            QUEST_DICT[quest.getName()] = quest

def setQuestNames(quests):
    names = {}
    for quest in quests.keys():
        name = quest
        if quest.endswith(" (quest)"):
            name = quest[:-len(" (quest)")]
        names[name] = quest
    QUEST_NAMES.update(names)
    return

def getQuestRequirementContainer(tables):
    for table in tables:
        for attr in table.attrs.keys():
            if attr == u'class':
                for key in table.attrs[u'class']:
                    if key == u'questdetails':
                        for container in table.contents:
                            if type(container) == bs4.element.Tag:
                                for row in container.contents:
                                    if type(row) == bs4.element.Tag and row.contents[1].contents[0].contents[0] == u"Requirements":
                                        for element in row.contents[3]:
                                            if type(element) == bs4.element.Tag:
                                                for bullets in element.contents:
                                                    if type(bullets) == bs4.element.Tag and type(bullets.contents[0]) == bs4.element.NavigableString:
                                                        if "completion" in bullets.contents[0].lower() or "completed" in bullets.contents[0].lower():
                                                            return bullets
                                            elif type(element) == bs4.element.NavigableString:
                                                if "completion" in element.lower() or "completed" in element.lower():
                                                    return row.contents[3].contents[row.contents[3].index(element) + 1]

def openPage(url):
    response = BR.open(url)

    soup = bs(response.read(), 'html5lib')

    tables = soup.findAll('table')

    return parseContents(getQuestRequirementContainer(tables))

def parseContents(container):
    quests = []
    if type(container) == bs4.element.Tag:
        if len(container.attrs) > 0:
            for key in container.attrs.keys():
                if key == u'href':
                    if "Awowogei" in container.attrs[u'href']:
                        return ["Recipe for Disaster/Freeing King Awowogei"]
                    elif "Pirate_Pete" in container.attrs[u'href']:
                        return ["Recipe for Disaster/Freeing Pirate Pete"]
        if len(container.contents) > 0:
            for item in container.contents:
                parsed = parseContents(item)
                if parsed is not None:
                    quests.extend(parsed)
    elif container != '\n' and container != '\n\n' and type(container) == bs4.element.NavigableString:
        if container in QUEST_DICT.keys():
            return [container]
        elif container in QUEST_NAMES.keys():
            return [QUEST_NAMES[container]]

    return quests

def convertDictToQuestNode(d):
    newQuest = QuestNode()
    newReqs = []
    for req in d['reqs']:
        newReqs.append(convertDictToQuestNode(req))
    newQuest.init(d['name'], d['url'], d['href'], newReqs)
    return newQuest

def generateGraphForQuest(quest):
    graph = nx.DiGraph()
    graph.add_node(str(quest.getName()))
    for req in quest.getReqs():
        graph.add_node(str(req.getName()))
        graph.add_edge(str(quest.getName()), str(req.getName()))
        if len(req.getReqs()) > 0:
            graph = nx.compose(graph, generateGraphForQuest(req))
    return graph

def getNodeDegree(quest):
    degree = 0
    if len(quest.getReqs()) > 0:
        degree = 1
        maxDegree = 0
        for req in quest.getReqs():
            nextDegree = getNodeDegree(req)
            if nextDegree > maxDegree:
                maxDegree = nextDegree
        degree += maxDegree
    return degree

def getNodeLayer(graph, quest):
    if len(nx.ancestors(graph, quest)) == 0:
        return 0

def main():
    global QUEST_DICT
    BR.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]

    BR.set_handle_equiv(True)
    BR.set_handle_gzip(True)
    BR.set_handle_redirect(True)
    BR.set_handle_referer(True)
    BR.set_handle_robots(True)

    # Parse through wiki page
    response = BR.open(LIST_URL)

    tables = getQuestTables(response.read())
    getQuestList(tables[0])  # f2p
    getQuestList(tables[1])  # members
    setQuestNames(QUEST_DICT)

    if not os.path.isfile('quests.txt'):
        for quest in QUEST_DICT.keys():
            if quest == "Recipe for Disaster":
                for name in QUEST_DICT.keys():
                    if name == u'Recipe for Disaster/Full guide':
                        continue
                    elif 'Recipe for Disaster/' in name:
                        QUEST_DICT[u'Recipe for Disaster'].addReq(QUEST_DICT[name])
            else:
                print "Loading", quest + "..."
                for req in openPage(QUEST_DICT[quest].getURL()):
                    QUEST_DICT[quest].addReq(QUEST_DICT[req])

        # Fix duplicate quests in quest requirements
        for quest in QUEST_DICT.keys():
            if quest == "The Great Brain Robbery":
                QUEST_DICT[quest].removeReq("Recipe for Disaster")
            QUEST_DICT[quest].removeDuplicates()

        with open('quests.txt', 'w') as outfile:
            print "\nOutputting quest list into json text file..."
            json.dump(QUEST_DICT, outfile, cls=QuestNodeEncoder)
    else:
        with open('quests.txt') as infile:
            jsonObj = json.load(infile)
            # Load the json objects into custom QuestNode class
            for obj in jsonObj.keys():
                obj = jsonObj[obj]
                if obj is not None:
                    newQuest = convertDictToQuestNode(obj)
                    QUEST_DICT[obj['name']] = newQuest
            # Pretty print all QuestNode instances
            # print json.dumps(jsonObj, indent=4, sort_keys=True)

    # Pretty print all quest requirements
    '''for quest in QUEST_DICT.keys():
        QUEST_DICT[quest].printReqs()'''

    # Create a network from the Quest dictionary
    completeGraph = nx.DiGraph()
    for name in QUEST_DICT.keys():
        if name == u'Recipe for Disaster/Full guide':
            continue
        completeGraph = nx.compose(completeGraph, generateGraphForQuest(QUEST_DICT[name]))

    maxDegree = 0
    maxQuest = ""
    for quest in QUEST_DICT.keys():
        degree = getNodeDegree(QUEST_DICT[quest])
        if degree > maxDegree:
            maxDegree = degree
            maxQuest = quest
    print "Quest with tallest tree structure:\n\t", maxQuest, "with degree", maxDegree

    #completeGraph = generateGraphForQuest(QUEST_DICT[u"Dragon Slayer II"])
    #completeGraph = generateGraphForQuest(QUEST_DICT[u"Recipe for Disaster"])
    #completeGraph = generateGraphForQuest(QUEST_DICT[u"Monkey Madness II"])
    #completeGraph = generateGraphForQuest(QUEST_DICT[u"A Taste of Hope"])
    #completeGraph = generateGraphForQuest(QUEST_DICT[u"Mourning's Ends Part II"])
    #completeGraph = generateGraphForQuest(QUEST_DICT[u"The Great Brain Robbery"])
    #completeGraph = nx.compose(completeGraph, generateGraphForQuest(QUEST_DICT[u"Recipe for Disaster"]))
    #completeGraph = nx.compose(completeGraph, generateGraphForQuest(QUEST_DICT[u"Monkey Madness II"]))
    #completeGraph = nx.compose(completeGraph, generateGraphForQuest(QUEST_DICT[u"A Taste of Hope"]))
    #completeGraph = nx.compose(completeGraph, generateGraphForQuest(QUEST_DICT[u"Mourning's Ends Part II"]))
    #completeGraph = nx.compose(completeGraph, generateGraphForQuest(QUEST_DICT[u'The Great Brain Robbery']))

    '''nx.draw_networkx_nodes(completeGraph, ax=None, pos=graphviz_layout(completeGraph, prog='dot'), node_shape='s')
    nx.draw_networkx_labels(completeGraph, ax=None, pos=graphviz_layout(completeGraph, prog='dot'), font_size=10)
    nx.draw_networkx_edges(completeGraph, ax=None, pos=graphviz_layout(completeGraph, prog='dot'))'''

    # Draw a pretty looking image
    aGraph = nx.nx_agraph.to_agraph(completeGraph.reverse())
    aGraph.layout('dot', args='-Nfontsize=10 -Nwidth=".2" -Nheight=".2" -Nmargin=0 -Gfontsize=8')
    aGraph.draw('test.png')

    completeGraph = completeGraph.reverse()

    nx.draw(completeGraph, pos=nx.nx_agraph.graphviz_layout(completeGraph, prog='dot'), with_labels=True)
    #nx.draw(completeGraph, pos=nx.shell_layout(completeGraph), with_labels=True)
    #nx.draw(aGraph, with_labels=True)
    plt.gcf().canvas.set_window_title("All Old School RuneScape Quests")
    plt.axis('tight')
    plt.axis('off')
    plt.show()

main()
