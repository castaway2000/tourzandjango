import requests
import re
import bs4


def get_location_summary(location):
    wiki = "https://wikitravel.org/wiki/en/api.php?action=parse&page=%s&prop=text&section=0&format=json&redirects" % location
    data = requests.get(wiki).json()
    bs = bs4.BeautifulSoup
    dataset = bs(data['parse']['text']['*'], features="html.parser").text.strip()
    stripped = re.sub(r'\n\s*\n', '\n', dataset).splitlines()
    out = []
    for line in stripped[1:]:
        if line[0] == ' ' or 'For other places with the same name,' in line or '— have a look at each of them.' in line:
            pass
        else:
            out.append(' '.join(re.sub(r'\[.*?\]', '', line).split()))
    location_description = ''.join(out)
    location_summary = ''.join(location_description.split('. ')[:4])
    return str(location_summary)