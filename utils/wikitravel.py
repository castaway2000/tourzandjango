import requests
import re
import bs4


def get_location_summary(location, full_location=None):
    try:
        location_description = 'Description Pending'
        location = re.sub(r'[\(].*?[\)]', '', location)  # removing parenthesis for proper search
        wiki = "https://wikitravel.org/wiki/en/api.php?action=parse&page=%s&prop=text&section=0&format=json&redirects" % location
        data = requests.get(wiki).json()
        bs = bs4.BeautifulSoup
        dataset = bs(data['parse']['text']['*'], features="html.parser").text.strip()
        print(dataset)
        stripped = re.sub(r'\n\s*\n', '\n', dataset).splitlines()
        # print(stripped)
        if stripped[0] == location:
            stripped = stripped[1:]
        out = []
        for idx, line in enumerate(stripped):
            if line.split(",")[0] == stripped[0]:
                location_description = ' '.join(re.sub(r'\[.*?\]', '', stripped[idx]).split())
            elif line[0] == ' ' or 'For other places with the same name,' in line or '— have a look at each of them.' in line:
                pass
            else:
                out.append(' '.join(re.sub(r'\[.*?\]', '', line).split()))
                location_description = ''.join(out)
        # print(location_description)
        if "There is more than one place called" in location_description and full_location is not None:
            location_description = '%s is a City located in %s' % (location, str(full_location).split(",")[1])
        return location_description
    except KeyError:
        location_description = 'Description Pending'
        return str(location_description)
    except Exception as err:
        print(err)
        location_description = 'Description Pending'
        return str(location_description)

get_location_summary('Seattle')