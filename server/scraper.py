import requests
import lxml
import re
import datetime
from bs4 import BeautifulSoup
import json
import urllib
import random

from PIL import Image

MAX_DEPTH = 15


def scrape_word(word, dlp="", dlurl=""):
    headers = {
        "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.80 Safari/537.36 Edg/98.0.1108.43"
    }

    params = {
        "q": word,
        "tbm": "isch",
        "ijn": "0",
    }

    html = requests.get("https://www.google.com/search",
                        params=params, headers=headers)
    soup = BeautifulSoup(html.text, 'lxml')

    # print('\nGoogle Images Metadata:')
    for google_image in soup.select('.isv-r.PNCib.MSM1fd.BUooTd'):
        title = google_image.select_one(
            '.VFACy.kGQAp.sMi44c.lNHeqe.WGvvNb')['title']
        source = google_image.select_one('.fxgdke').text
        link = google_image.select_one(
            '.VFACy.kGQAp.sMi44c.lNHeqe.WGvvNb')['href']

    # this steps could be refactored to a more compact
    all_script_tags = soup.select('script')

    # # https://regex101.com/r/48UZhY/4
    matched_images_data = ''.join(re.findall(
        r"AF_initDataCallback\(([^<]+)\);", str(all_script_tags)))

    # https://kodlogs.com/34776/json-decoder-jsondecodeerror-expecting-property-name-enclosed-in-double-quotes
    # if you try to json.loads() without json.dumps it will throw an error:
    # "Expecting property name enclosed in double quotes"
    matched_images_data_fix = json.dumps(matched_images_data)
    matched_images_data_json = json.loads(matched_images_data_fix)

    # https://regex101.com/r/pdZOnW/3
    matched_google_image_data = re.findall(
        r'\[\"GRID_STATE0\",null,\[\[1,\[0,\".*?\",(.*),\"All\",', matched_images_data_json)

    # https://regex101.com/r/NnRg27/1
    matched_google_images_thumbnails = ', '.join(
        re.findall(r'\[\"(https\:\/\/encrypted-tbn0\.gstatic\.com\/images\?.*?)\",\d+,\d+\]',
                   str(matched_google_image_data))).split(', ')

    # print('Google Image Thumbnails:')  # in order
    for fixed_google_image_thumbnail in matched_google_images_thumbnails:
        # https://stackoverflow.com/a/4004439/15164646 comment by Frédéric Hamidi
        google_image_thumbnail_not_fixed = bytes(
            fixed_google_image_thumbnail, 'ascii').decode('unicode-escape')

        # after first decoding, Unicode characters are still present. After the second iteration, they were decoded.
        google_image_thumbnail = bytes(
            google_image_thumbnail_not_fixed, 'ascii').decode('unicode-escape')
        # print(google_image_thumbnail)

    # removing previously matched thumbnails for easier full resolution image matches.
    removed_matched_google_images_thumbnails = re.sub(
        r'\[\"(https\:\/\/encrypted-tbn0\.gstatic\.com\/images\?.*?)\",\d+,\d+\]', '', str(matched_google_image_data))

    # https://regex101.com/r/fXjfb1/4
    # https://stackoverflow.com/a/19821774/15164646
    matched_google_full_resolution_images = re.findall(r"(?:'|,),\[\"(https:|http.*?)\",\d+,\d+\]",
                                                       removed_matched_google_images_thumbnails)

    links = []
    # print('\nFull Resolution Images:')  # in order
    for index, fixed_full_res_image in enumerate(matched_google_full_resolution_images):
        original_size_img_not_fixed = bytes(
            fixed_full_res_image, 'ascii').decode('unicode-escape')
        original_size_img = bytes(
            original_size_img_not_fixed, 'ascii').decode('unicode-escape')
        links.append(original_size_img)

    if len(links) > 0:
        links = links[0:MAX_DEPTH]
    else:
        return None

    resp = None
    iters = 0
    while resp == None or resp.status_code != 200 or resp.headers["Content-Type"].split("/")[-1] not in ("jpeg", "jpg", "png"):
        if iters > 2*len(links):
            return None
        # print('getting a link:', word)
        lnk = links[random.randrange(0, len(links))]
        # print("Link to use", lnk)
        iters += 1
        resp = None
        try:
            resp = requests.get(lnk, timeout=2)
            # print("response code")
            # print(resp, resp.status_code)
        except Exception as e:
            print("GET exception fired:", e)
            pass

    file_type = resp.headers["Content-Type"].split("/")[-1]
    fname = f"{dlp}download.{file_type}"

    # print("writing to file")
    with open(fname, "wb") as file:
        file.write(resp.content)
    # print("done writing!")

    # Adjust size to improve download times
    image = Image.open(fname)
    image.thumbnail((500, 500))
    image.save(fname)
    # print("done resaving!")

    # print("Final url:", dlurl + f"download.{file_type}")
    return dlurl + f"download.{file_type}"
