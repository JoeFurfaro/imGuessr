import random

wordsFile = open('keys.txt', "r")
words = wordsFile.readlines()
wordsFile.close()


def get_random_word():
    global words
    key = words[random.randrange(0, len(words)-1)].strip()
    return key.lower()
