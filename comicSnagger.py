#!/usr/bin/env python3
"""
Scrape https://www.readcomics.io for comic book images
"""
import json
import os
import shutil
from collections import namedtuple
from sys import exit

import requests
from bs4 import BeautifulSoup


Comic = namedtuple("Comic", "title url")
LOCAL_DIR = "/home/mohh/Downloads/Comics/"
URL = "https://www.readcomics.io"
SEARCH_URL = f"{URL}/comic-search?key="


def display_choice(search_term):
    url = SEARCH_URL + search_term.replace(" ", "+")
    comics = search(url)
    print(f"Found {len(comics)} titles matching {search_term}")
    for i, comic in enumerate(comics):
        print(f" [{i}] {comic.title}")
    try:
        choice = int(input(f"\nWhich one would you like to get? "))
        get_comic(comics[choice])
    except ValueError as e:
        print(f"\n  {e}")


def download(url):
    soup = get_soup(url+"/full")
    images = soup.find_all(class_="chapter_img")
    links = [link["src"] for link in images]
    for link in links:
        print(f"Downloading: {link}")


def get_comic(comic):
    print(f"Retrieving: {comic.title}")
    print(comic.url)
    chapters = []
    soup = get_soup(comic.url)

    genres_ul = soup.find(class_="anime-genres")
    genres = [g.text for g in genres_ul.find_all("a")]
    print(f"{' '.join(genres)}")

    desc_div = soup.find(class_="detail-desc-content")
    desc = desc_div.find("p").text.strip()
    print(f"\n  {desc}\n")

    chapter_a = soup.find_all(class_="ch-name")
    for link in chapter_a:
        title = link.text
        url = link["href"]
        chapters.append(Comic(title, url))

    count = len(chapters)
    if count == 1:
        descriptive = "is"
        s = ""
    else:
        descriptive = "are"
        s = "s"
    print(f"There {descriptive} {count} chapter{s} available:")

    for i, chapter in enumerate(chapters):
        print(f" [{i}] {chapter.title}")
    choice = input("\nWhich one would you like? [ENTER] for all ")
    if not choice:
        for chapter in chapters:
            download(chapter.url)
    else:
        try:
            choice = int(choice)
            download(chapters[choice].url)
        except ValueError as e:
            print(f"\n  {e}")


def get_soup(url):
    page = requests.get(url)
    if page.ok:
        soup = BeautifulSoup(page.content, "html.parser")
        return soup
    print("Something's gone wrong, sorry...")
    exit(1)


def main():
    search_term = input("Comic name: ")
    display_choice(search_term)


def search(search_url):
    comics = []
    try:
        term = search_url.split('=')[1].replace('+', ' ').title()
        print(f"Searching for: {term}...")
        soup = get_soup(search_url)
        series = soup.find_all(class_="egb-serie")
        for link in series:
            title = link.text
            url = link["href"]
            comics.append(Comic(title, url))
        return comics
    except requests.exceptions.ConnectionError:
        print("You must have an active Internet connection to use...")
        exit(1)
    

if __name__ == "__main__":
    main()
