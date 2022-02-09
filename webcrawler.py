import requests
from requests.exceptions import HTTPError
from urllib.parse import urljoin, urlparse, unquote
import os, codecs
import re

global base_url
base_url = 'https://mike.cpe.ku.ac.th'
def get_page(url):
    global headers
    text = ''
    try:
        response = requests.get(url, headers=headers, timeout=2)
        # If the response was successful, no Exception will be raised
        response.raise_for_status()
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')  # Python 3.6
    except Exception as err:
        print(f'Other error occurred: {err}')  # Python 3.6
    else:
        # print('Success!')
        text = response.text
    return text.lower()


# FIFO queue
def dequeue():
    global frontier_q
    current_url = frontier_q[0]
    frontier_q = frontier_q[1:]
    return current_url
    
def enqueue(links):
    global frontier_q
    for link in [ x for x in links if( re.findall(r'.pdf|.doc|.xls|.xlsx|.ppt|.exe|.jpg|.mpg|.zip|.png|.mp4|.mp3|.jpeg',x) == [])]:
        # print(link) 
        if checkLink(link):
            frontier_q.append(link)
            
def checkLink(a):
    return a not in frontier_q and a not in visited_q 

def link_parser(raw_html):
    urls = [];
    pattern_start = '<a href="';  pattern_end = '"'
    index = 0;  length = len(raw_html)
    while index < length:
        start = raw_html.find(pattern_start, index)
        if start > 0:
            start = start + len(pattern_start)
            end = raw_html.find(pattern_end, start)
            link = raw_html[start:end]
            if len(link) > 0:
                if link not in urls:
                    urls.append(link)
            index = end
        else:
            break
    return urls


# saveFile
def saveFile(i,raw_html):
    i = unquote(i)
    if(len(raw_html) != 0):
        htmlLink = urlparse(i)
        path = 'html/' + htmlLink.netloc + htmlLink.path
        if(path[-1] == '/'):
            path = path[:len(path)-1]
        if re.findall(r'.html|.php|.htm|.asp|.jsp',i) != []:
            path =  "html/" + htmlLink.netloc  +  htmlLink.path[:htmlLink.path.rfind("/")]
            abs_file =  path+'/' + htmlLink.path[htmlLink.path.rfind("/")+1:]
        elif re.findall(r'robots.txt',i) != []:
            path = 'html/' + htmlLink.netloc
            abs_file = path+ "/robots.txt"
        else:
            abs_file = path + "/dummy"
        # print(abs_file)
        
        try:
            os.makedirs(path, 0o755, exist_ok=True)
            f = codecs.open(abs_file, 'w', 'utf-8')
            f.write(raw_html)
            f.close()
        except:
            print(f"error {abs_file}")
            return 0
        return 1
    return 0

    seed_url = 'https://www.ku.ac.th/th/'
frontier_q = [seed_url,"https://mike.cpe.ku.ac.th/","https://kps.ku.ac.th/", "https://www.src.ku.ac.th/", "https://www.csc.ku.ac.th/th/,https://sbc.ku.ac.th/"]
visited_q = []
robot = []
sitemap = []
headers = {
    'User-Agent': 'MyTestWeb',
    'From': 'sila.l@ku.th'
}
seed_url = 'https://www.ku.ac.th/th/'
base_url = 'https://mike.cpe.ku.ac.th'
page = 0
try:
    while(page < 40000):
        current_url = dequeue()
        visited_q.append(current_url)
        raw_html = get_page(current_url)
        page += saveFile(current_url,raw_html)
        robot_txt = get_page(urlparse(current_url).scheme + "://" + urlparse(current_url).netloc + "/robots.txt")
        if(len(robot_txt) != 0  and robot_txt[0:4]== "user"):
            saveFile(urlparse(current_url).scheme + "://" + urlparse(current_url).netloc + "/robots.txt",robot_txt)
            if( urlparse(current_url).netloc  not in robot):
                f = codecs.open("list_robots.txt", 'a', 'utf-8')
                f.write(urlparse(current_url).netloc + "\n")
                f.close() 
                if "sitemap" in robot_txt:
                    print(robot_txt)
                    f = codecs.open("list_sitemap.txt", 'a', 'utf-8')
                    f.write(urlparse(current_url).netloc + "\n")
                    f.close()
            robot.append(urlparse(current_url).netloc)
        extracted_links = [ urljoin(seed_url,x) for x in link_parser(raw_html)]
        extracted_links = [ x for x in extracted_links if urlparse(x).scheme == "https" and "ku.ac.th" in urlparse(x).netloc]
        enqueue(extracted_links)
        print(page) 
except:
    print("--------------- Frontier_q is not enough -----------")