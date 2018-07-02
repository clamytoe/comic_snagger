#!/usr/bin/env python3
"""
comic_snagger

Scrapes https://www.readcomics.io for comic book images
"""
import os
import shutil
import textwrap
from collections import namedtuple

import requests
from bs4 import BeautifulSoup

Comic = namedtuple("Comic", "title url")
LOCAL_DIR = "/home/mohh/Downloads/Comics/"
URL = "https://www.readcomics.io"
SEARCH_URL = f"{URL}/comic-search?key="
WIDTH = 70

try:
    TERM_COL = os.get_terminal_size()[0] - 2
    WIDTH = TERM_COL if TERM_COL < 119 else 118
except OSError:
    pass


def clear_screen():
    """
    Clears the screen
    :return: None
    """
    _ = os.system('cls' if os.name == 'nt' else 'clear')


def compress_comic(title_dir):
    """
    Takes the given directory and compresses it into the comic book format.

    :param title_dir: string - path to directory
    :return: None
    """
    clear_screen()
    if os.path.isdir(title_dir):
        print(f"Creating comic book file: {title_dir.split('/')[-1]}.cbz")
        shutil.make_archive(title_dir, "zip", title_dir)
        os.rename(f"{title_dir}.zip", f"{title_dir}.cbz")
        shutil.rmtree(title_dir)
    else:
        print(f"\nInvalid directory path was given:\n\t {title_dir}")
        exit(2)


def display_choice(search_term, comics):
    """
    Displays the comic book titles that were found.

    If no match is found, the user is informed. Otherwise the comics found are
    listed with an index number to the left. It will then ask the user for
    their choice and the user is to enter the index number of the comic that
    they want to retrieve.

    :param search_term: str - title of comic entered by user
    :param comics: list - containing Comic namedtuples
    :return: namedtuple - Comic(title, url)
    """
    if not comics:
        print(f"Sorry, did not find anything for {search_term}...")
        exit()

    while True:
        print(f"Found {len(comics)} titles matching {search_term}")
        for i, comic in enumerate(comics):
            print(f" [{i}] {comic.title}")
        try:
            choice = int(input(f"\nWhich one would you like to get? "))
            return comics[choice]
        except (ValueError, IndexError):
            clear_screen()
            print(f"\n** {choice} is not a valid entry! **\n")


def display_comics(issues):
    """
    Displays the comic book issues that were found.
    :param issues: list - Comic(title, url) namedtuples
    :return: None
    """
    count = len(issues)
    descriptive, plurality = ("is", "") if count == 1 else ("are", "s")

    while True:
        print(f"\nThere {descriptive} {count} comic{plurality} available:")
        for i, chapter in enumerate(issues):
            print(f" [{i}] {chapter.title}")
        choice = input("\nWhich one would you like? [ENTER] for all ")
        if not choice:
            for chapter in issues:
                download(chapter.title, chapter.url)
            break
        else:
            try:
                choice = int(choice)
                download(issues[choice].title, issues[choice].url)
                break
            except (ValueError, IndexError):
                clear_screen()
                print(f"\n** {choice} is not a valid entry! **\n")


def download(title, url):
    """
    Downloads the images for the comic.

    If the comic book file does not already exist, it will create the directory
    for the title and download all of the images for it into it. Once complete,
    it compresses the directory into the .CBZ format and removes the directory.

    :param title: str - title of the comic
    :param url: str - the url for the comic
    :return: None
    """
    title_dir = os.path.join(LOCAL_DIR, title)
    if not os.path.isfile(f"{title_dir}.cbz"):
        try:
            os.makedirs(title_dir)
        except FileExistsError:
            pass

        soup = get_soup(url+"/full")
        images = soup.find_all(class_="chapter_img")
        links = [link["src"] for link in images]
        for link in links:
            *_, image = link.split("/")
            num, ext = image.split(".")
            image = (
                f"{num.zfill(2)}.{ext}"
                if int(num) < 10 and len(num) == 1
                else image
            )
            img = os.path.join(title_dir, image)
            cmd = f'wget --no-verbose --show-progress -c {link} -O "{img}"'
            os.system(cmd)
        compress_comic(title_dir)
    else:
        print(f"{title_dir.split('/')[-1]}.cbz already exists, skipping.")


def get_comic(comic):
    """
    Scrapes the site for the given comic.

    :param comic: Comic - namedtuple
    :return: list - Comic(title, url) namedtuples
    """
    clear_screen()
    print(f"Retrieving: {comic.title}")
    # print(comic.url)
    issues = []
    soup = get_soup(comic.url)

    genres_ul = soup.find(class_="anime-genres")
    genres = [g.text for g in genres_ul.find_all("a")]
    print(f"{' '.join(genres)}\n")

    desc_div = soup.find(class_="detail-desc-content")
    desc = desc_div.find("p").text.strip()
    for line in desc.split("\n"):
        blurb = textwrap.fill(line,
                              initial_indent='  ',
                              subsequent_indent=' ',
                              width=WIDTH
                              )
        print(f"{blurb}")

    chapter_a = soup.find_all(class_="ch-name")
    for link in chapter_a:
        title = link.text
        url = link["href"]
        issues.append(Comic(title, url))

    return issues


def get_soup(url):
    """
    Default soupifying code.

    :param url: str - url of the page to soupify
    :return: BeautifulSoup - soup object of the page
    """
    page = requests.get(url)
    if page.ok:
        soup = BeautifulSoup(page.content, "html.parser")
        return soup

    print("Something's gone wrong, sorry...")
    exit(1)


def main():
    """
    Main entry point into the program.

    :return: None
    """
    try:
        clear_screen()
        search_term = input("Comic name: ")
        url = SEARCH_URL + search_term.replace(" ", "+")
        comics = search(url)
        choice = display_choice(search_term, comics)
        issues = get_comic(choice)
        display_comics(issues)
    except KeyboardInterrupt:
        print('\n\nProgram aborted by user. Exiting...\n')
        exit()


def search(search_url):
    """
    Scrapes for the site at the given url.

    :param search_url: str - the url to the search page
    :return: list - Comic(title, url) namedtuples
    """
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
