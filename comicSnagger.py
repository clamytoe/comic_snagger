#!/usr/bin/env python
"""
Scrape http://readcomics.website for comic book images
"""
import json
import os
import requests
import shutil
import time
from bs4 import BeautifulSoup
from sys import exit


def scrape_chapters(base_url, main_title):
    """
    Scrape the title and url of all the chapters in the page
    """
    soup = None

    # Try to retrieve the list of chapters
    try:
        page = requests.get(base_url)
        print('Processing: {}...'.format(main_title))
        soup = BeautifulSoup(page.content, 'html.parser')
        page.close()
    except requests.exceptions.ConnectionError:
        print('You must be connected to the Internet in order for this to work...')
        exit(1)

    chapters = soup.find_all(class_='chapter-title-rtl')
    comics = [[c.contents[1].next, c.contents[1]['href']] for c in chapters]

    # for chapter in chapters:
    #     title = chapter.contents[1].text
    #     link = chapter.contents[1]['href']
    #     comics.append([title, link])

    return comics


def scrape_links(url):
    """
    Scrape links pointing to the comic book chapters
    """
    images = []
    counter = 0

    while True:
        counter += 1
        page = requests.get('{0}/{1}'.format(url, counter))
        soup = BeautifulSoup(page.content, 'html.parser')
        try:
            alert = soup.find(class_='alert alert-info').find('p').text
            if alert:
                return images
        except AttributeError:
            images.append(soup.find(class_='img-responsive scan-page')['src'])
        time.sleep(1)


def download_images(local_dir, main_title, comicbooks):
    """
    Retrieve and save all of the images
    """
    for comic in comicbooks.keys():
        title_dir = os.path.join(local_dir, main_title)
        comic_dir = os.path.join(title_dir, comic)
        print('\nProcessing: {}...'.format(comic))

        # Create the main directory for our title
        try:
            os.makedirs(title_dir)
        except FileExistsError:
            pass

        if not os.path.isfile(comic_dir + '.cbz'):
            for img in comicbooks[comic]:
                image = img.split('/')[-1]
                num, ext = image.split('.')

                # Pad the number with a zero
                image = '{0}.{1}'.format(num.zfill(2), ext) if int(num) < 10 and len(num) == 1 else image
                # if int(num) < 10 and len(num) == 1:
                #     num = '0' + str(num)
                #     image = num + '.' + ext
                filename = os.path.join(comic_dir, image)
                try:
                    os.makedirs(comic_dir)
                except FileExistsError:
                    pass

                cmd = 'wget --no-verbose --show-progress -c {0} -O "{1}"'.format(img, filename)
                os.system(cmd)

            compress_comic(comic_dir)
        else:
            print('"{}" already exists, skipping'.format(comic_dir.split('/')[-1]))


def compress_comic(comic_dir):
    """
    Takes the given directory and compresses it into the comic book format
    """
    if os.path.isdir(comic_dir):
        print('Creating comic book file: {}.cbz'.format(comic_dir.split('/')[-1]))
        shutil.make_archive(comic_dir, 'zip', comic_dir)
        os.rename(comic_dir + '.zip', comic_dir + '.cbz')
        shutil.rmtree(comic_dir)
    else:
        print('\nInvalid directory path was given:\n\t {}'.format(comic_dir))
        exit(2)


def save(directory, title, object):
    """
    Takes a directory path and a dictionary object and dumps it to a json file
    """
    comic_log = os.path.join(directory, title)
    with open('{}.json'.format(comic_log), 'w') as f:
        json.dump(object, f)


def main():
    """
    Get the comic's main page and follow the links to get all of the chapters that are available
    """
    local_dir = '/home/mohh/Downloads/Comics/'

    # Get main page and get links to all of the chapter pages
    base_url = 'http://readcomics.website/comic/dungeons-dragons-frost-giants-fury-2017'

    # Create the main directory for our title
    try:
        os.makedirs(local_dir)
    except FileExistsError:
        pass

    # Extract the title from the url
    main_title = ((base_url.split('/')[-1]).replace('-', ' ')).title()

    filename = '{}.json'.format(main_title)
    comic_cache = os.path.join(local_dir, filename)
    print('Looking for cached file: {}'.format(comic_cache))

    if not os.path.isfile(comic_cache):
        # Scrape chapters in the main page
        chapters = scrape_chapters(base_url, main_title)

        print('Found: {} comics'.format(len(chapters)))
        print('Collecting image data...')
        combined_total = 0
        comicbooks = {}

        # chapters contains lists consisting of [title, url]
        for chapter in chapters:
            # Scrape images in linked pages
            comicbooks[chapter[0]] = scrape_links(chapter[1])
            # Display the name of the comic along with how many images it contains
            page_count = len(comicbooks[chapter[0]])
            combined_total += page_count
            print('  {0} has {1} pages'.format(chapter[0], page_count))

        print('Total images to be processed: {}'.format(combined_total))

        save(local_dir, main_title, comicbooks)
    else:
        with open(comic_cache, 'r') as f:
            comicbooks = json.load(f)

    # Download all of the images for each comic
    download_images(local_dir, main_title, comicbooks)

    print('\nAll comics have been retrieved and compiled.')

if __name__ == '__main__':
    main()
