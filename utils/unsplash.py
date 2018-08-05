from unsplash.api import Api
from unsplash.auth import Auth
import requests
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
import urllib.parse as urlparse
import datetime
import time


def get_image(search_term, image_name, unsplash_key=None):
    unsplash_keys = ["193597620d38bad554cbc25abc83facdb2edaf5f30c6b3c0e9309a2f65282237",
                     "b02b08dff59f76396a8baae8d6e981e41683954c2d68dabaab79b3233f2dcc39",
                     "b09fe903c14abd6b81434fcf821907617354c7a35bf463d9007c1420c15891b5",
                     "293d80bffd44a05e7f53e64685c039285c72feb87185397a58ccd927076bf0fe",
                     "0193a0e1b3b1ef396ab6ff1dc9f2845ef29d91fc194f4dca69605d3d0947e49a",
                     "71f7daecc23f75f0cf8fff3488a2cafe0040437d3240d8214e00379e6c337c0e",
                     "b036ac885ede0b5e6c803b97c770de3872b9fde6848adf4a359639d6a7612e95"]
    values = dict()
    values["client_id"] = unsplash_keys[0] if not unsplash_key else unsplash_key
    values["page"] = 1
    values["orientation"] = "landscape"
    url = "https://api.unsplash.com/photos/search/"
    values["query"] = search_term
    r = requests.get(url, values)
    if r.status_code == 200:
        images_data = r.json()
        results = dict()
        results_check_list = list()
        for photo in images_data:
            likes = photo["likes"]
            created_date_str = photo["created_at"] #"2014-11-18T14:35:36-05:00"
            created_date_str_shorted = created_date_str.split("T")[0]
            created_date = datetime.datetime.strptime(created_date_str_shorted, '%Y-%m-%d')
            now = datetime.datetime.now()
            days_diff = (now - created_date).days
            likes_index = likes/days_diff

            results_check = dict()
            results_check["url"] = photo["urls"]["full"]
            results_check["days_diff"] = days_diff
            results_check["likes"] = likes
            results_check["likes_index"] = likes_index
            results_check_list.append(results_check)

            if len(results) == 0 or likes_index > results["likes_index"]:
                image_url = photo["urls"]["full"]
                parsed = urlparse.urlparse(image_url)
                get_parameters = urlparse.parse_qs(parsed.query)
                r = requests.get(image_url)
                if r.status_code == requests.codes.ok:
                    if get_parameters.get("fm"):
                        extension = get_parameters.get("fm")[0]
                        img_filename = "%s.%s" % (image_name, extension)
                        results["likes_index"] = likes_index
                        results["data"] = (r.content, img_filename)

        # print(results_check_list)
        # import time
        # time.sleep(30)

        if len(results) > 0:
            return results["data"]
        else:
            return (None, None)
    else:
        try:
            print(unsplash_key)
            current_index = unsplash_keys.index(unsplash_key)
            next_index = current_index+1
            unsplash_key = unsplash_keys[next_index]
            print(unsplash_key)
            time.sleep(5)
            return get_image(search_term, image_name, unsplash_key)
        except Exception as e:
            print(e)
            time.sleep(10)
            return (None, None)
