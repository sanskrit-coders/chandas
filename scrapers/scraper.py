from os import listdir
from os.path import isfile, join
from BeautifulSoup import BeautifulSoup
import re
hexentityMassage = [(re.compile('&#x([^;]+);'),
lambda m: '&#%d;' % int(m.group(1), 16))]

mypath = '/home/vvasuki/Downloads/HTML/'
onlyfiles = [ f for f in listdir(mypath) if isfile(join(mypath,f)) and f.startswith('v')]
for file_name in onlyfiles:
  with open(join(mypath, file_name), 'r') as content_file:
    content = content_file.read()
    soup = BeautifulSoup(content,
    convertEntities=BeautifulSoup.HTML_ENTITIES,
    markupMassage=hexentityMassage)
    h2_items = soup.findAll('h2')
    li_items = soup.findAll('li')
    output =  re.sub(r'<.+?>', r'', str(h2_items[0]))
    for item in li_items:
      output = output + ',' + re.sub(r'<.+?>', r'', str(item))
    print output
    # print ul_items
