#!/usr/bin/env python
"""
Scrape http://readcomics.website for comic book images
"""
import json
import os
import shutil
from sys import exit

import requests
from bs4 import BeautifulSoup


def collect_image_data(chapters):
    """
    Scrapes the images for the comics
    """
    combined_total = 0
    comicbooks = {}

    # chapters contains lists consisting of [title, url]
    for chapter in chapters:
        title = chapter[0]
        url = chapter[1]
        # Scrape images in linked pages
        comicbooks[title] = scrape_links(url)
        # Display the name of the comic along with how many images it contains
        page_count = len(comicbooks[title])
        combined_total += page_count
        print("  {0} has {1} pages".format(title, page_count))

    print("Total images to be processed: {}".format(combined_total))

    return comicbooks


def exists(url):
    """
    Determines if the provided url exists
    """
    page = requests.head(url)
    status = page.status_code
    return True if status == requests.codes.ok else False


def scrape_chapters(base_url, main_title):
    """
    Scrape the title and url of all the comics in the page
    """
    soup = None

    # Try to retrieve the list of chapters
    try:
        print("Processing: {}...".format(main_title))
        page = requests.get(base_url)
        soup = BeautifulSoup(page.content, "html.parser")
        page.close()
    except requests.exceptions.ConnectionError:
        print("You must be connected to the Internet in order for this to work...")
        exit(1)

    chapters = soup.find_all(class_="chapter-title-rtl")
    comics = [[c.contents[1].next, c.contents[1]["href"]] for c in chapters]

    return comics


def scrape_links(url):
    """
    Scrape links pointing to the comic book images
    """
    images = []
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    images.append(soup.find(class_="img-responsive scan-page")["src"].strip())

    # to avoid multiple get requests, we're only going to check and see if the image exists
    page_url, img_num = images[-1].rsplit("/", 1)
    num, ext = img_num.split(".")
    num = int(num)

    # increase image number until the image is not found
    while True:
        num += 1
        img_num = str(num).zfill(2)
        image_url = page_url + "/{0}.{1}".format(img_num, ext)

        # if image is found add it to the list otherwise break out of the loop
        if exists(image_url):
            images.append(image_url)
        else:
            break

    return images


def download_images(local_dir, main_title, comicbooks):
    """
    Retrieve and save all of the images
    """
    for comic in comicbooks.keys():
        title_dir = os.path.join(local_dir, main_title)
        comic_dir = os.path.join(title_dir, comic)
        print("\nProcessing: {}...".format(comic))

        # Create the main directory for our title
        try:
            os.makedirs(title_dir)
        except FileExistsError:
            pass

        if not os.path.isfile(comic_dir + ".cbz"):
            for img in comicbooks[comic]:
                image = img.split("/")[-1]
                num, ext = image.split(".")

                # Pad the number with a zero
                image = (
                    "{0}.{1}".format(num.zfill(2), ext)
                    if int(num) < 10 and len(num) == 1
                    else image
                )
                filename = os.path.join(comic_dir, image)
                try:
                    os.makedirs(comic_dir)
                except FileExistsError:
                    pass

                cmd = 'wget --no-verbose --show-progress -c {0} -O "{1}"'.format(
                    img, filename
                )
                os.system(cmd)

            compress_comic(comic_dir)
        else:
            print('"{}" already exists, skipping'.format(comic_dir.split("/")[-1]))


def compress_comic(comic_dir):
    """
    Takes the given directory and compresses it into the comic book format
    """
    if os.path.isdir(comic_dir):
        print("Creating comic book file: {}.cbz".format(comic_dir.split("/")[-1]))
        shutil.make_archive(comic_dir, "zip", comic_dir)
        os.rename(comic_dir + ".zip", comic_dir + ".cbz")
        shutil.rmtree(comic_dir)
    else:
        print("\nInvalid directory path was given:\n\t {}".format(comic_dir))
        exit(2)


def save(directory, title, dictionary):
    """
    Takes a directory path and a dictionary object and dumps it to a json file
    """
    comic_log = os.path.join(directory, title)
    with open("{}.json".format(comic_log), "w") as f:
        json.dump(dictionary, f)


def main():
    """
    Get the comic's main page and follow the links to get all of the chapters that are available
    """
    local_dir = "/home/mohh/Downloads/Comics/"

    # Get main page and get links to all of the chapter pages
    # base_url = 'http://readcomics.website/comic/dungeons-dragons-frost-giants-fury-2017'
    # base_url = 'http://readcomics.website/comic/guidebook-to-the-marvel-cinematic-universe-marvels-doctor-strange'
    # base_url = 'http://readcomics.website/comic/dollface-st-patricks-day-special-2017'
    base_url = "http://readcomics.website/comic/my-little-pony-friendship-is-magic-2012"

    # Create the main directory for our title
    try:
        os.makedirs(local_dir)
    except FileExistsError:
        pass

    # Extract the title from the url
    main_title = ((base_url.split("/")[-1]).replace("-", " ")).title()

    filename = "{}.json".format(main_title)
    comic_cache = os.path.join(local_dir, filename)

    if not os.path.isfile(comic_cache):
        # Scrape chapters in the main page
        chapters = scrape_chapters(base_url, main_title)

        print("Found: {} comics".format(len(chapters)))
        print("Collecting image data...")

        comicbooks = collect_image_data(chapters)
        save(local_dir, main_title, comicbooks)
    else:
        print("Found cached file: {}".format(comic_cache))
        with open(comic_cache, "r") as f:
            comicbooks = json.load(f)

    # Download all of the images for each comic
    download_images(local_dir, main_title, comicbooks)

    print("\nAll comics have been retrieved and compiled.")


if __name__ == "__main__":
    main()
