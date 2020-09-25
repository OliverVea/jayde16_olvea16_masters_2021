from requests import get

url = 'http://services.drift.kortinfo.net/kortinfo/services/Wfs.ashx?client=MapInfo&version=1.0.0&service=WFS&Site=Odense&Page=Kortopslag&Request=GetFeature&Typename=ugis:L167365_421559'
url = 'https://services.drift.kortinfo.net/kortinfo/services/Wfs.ashx?client=MapInfo&version=1.0.0&service=WFS&Site=Odense&Page=Kortopslag&request=GetFeature&typename=ugis:L167365_42155&bbox=587517.7075417278,6139491.009821663,587717.7075417278,6139691.009821663&srsName=EPSG:25832'
response = get(url)

content = response.content

from lxml import objectify, etree

try:
    content = objectify.fromstring(content)

    children = {c.tag.split('}')[-1]: c for c in content.iterchildren()}

    if 'Exception' in children:
        print(str(children['Exception'].ExceptionText), tag='WebService')
        response = content

    with open('last_response.xml', 'wb') as f:
        f.write(etree.tostring(content, pretty_print=True))
    response = content
except Exception as e:
    print(e)
    pass

s = etree.tostring(content, pretty_print=True)
s = s.decode('utf-8')

#print(s)

pass