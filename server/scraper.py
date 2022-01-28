import requests
import random
import os


def scrape_word(word, MAX_IMAGES=5):
    word = word.replace(" ", "+")
    url = "https://www.google.com/search?&hl=en&tbm=isch&q=" + word

    resp = requests.get(url)
    text = resp.text

    images = []
    cur = ""
    imageOpen = False
    i = 0

    while i < len(text):
        if not imageOpen:
            if text[i:i+4] == "<img":
                cur += "<img"
                imageOpen = True
                i += 4
            else:
                i += 1
        else:
            if text[i:i+2] == "/>":
                cur += "/>"
                images.append(cur)
                if len(images) == MAX_IMAGES:
                    break
                cur = ""
                imageOpen = False
                i += 2
            else:
                cur += text[i]
                i += 1

    links = []
    for image in images:
        link = ""
        i = 0
        linkOpen = False
        while i < len(image):
            if not linkOpen:
                if image[i:i+9] == "src=\"http":
                    linkOpen = True
                    i += 5
                else:
                    i += 1
            else:
                if image[i] == '\"':
                    links.append(link)
                    break
                else:
                    link += image[i]
                    i += 1

    # Now get a random image
    finalURL = links[random.randrange(0, len(links))]
    return finalURL
