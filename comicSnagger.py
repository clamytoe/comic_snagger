#!/usr/bin/env python
"""
Scrape http://readcomicbooksonline.net for comic book images
"""
import json
import os
import random
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
        quit()

    chapters = soup.find_all(class_='chapter-title-rtl')
    comic = []

    for chapter in chapters:
        title = chapter.contents[1].text
        link = chapter.contents[1]['href']
        comic.append([title, link])

    return comic


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


def download_image(local_dir, main_title, comicbooks):
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
        except OSError:
            pass

        if not os.path.isfile(comic_dir + '.cbz'):
            for img in comicbooks[comic]:
                image = img.split('/')[-1]
                num, ext = image.split('.')

                # Pad the number with a zero
                if int(num) < 10 and len(num) == 1:
                    num = '0' + str(num)
                    image = num + '.' + ext
                filename = os.path.join(comic_dir, image)
                try:
                    os.makedirs(comic_dir)
                except OSError:
                    pass

                try:
                    cmd = 'wget --no-verbose --show-progress -c {0} -O "{1}"'.format(img, filename)
                    # print(' Command: {}'.format(cmd))
                    os.system(cmd)
                except KeyboardInterrupt:
                    print('\nDownload interrupted by the user.')
                    quit()

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
        quit()


def save(dir, title, object):
    """
    Takes a directory path and a dictionary object and dumps it to a json file
    """
    comic_log = os.path.join(dir, title)
    with open('{}.json'.format(comic_log), 'w') as f:
        json.dump(object, f)


def main():
    """
    Get the comic's main page and follow the links
    to get all of the chapters that are available
    """
    local_dir = '/home/mohh/Downloads/Comics/'

    # Get main page and get links to all of the chapter pages
    # base_url = 'http://www.readcomics.tv/comic/amazing-spider-man-complete'
    # base_url = 'http://www.readcomics.tv/comic/lara-croft-and-the-frozen-omen-2015'
    # base_url = 'http://www.readcomics.tv/comic/star-trek'
    # base_url = 'http://www.readcomics.tv/comic/legendary-star-lord'
    # base_url = 'http://www.readcomics.tv/comic/star-wars'
    # base_url = 'http://www.readcomics.tv/comic/star-wars-knights-of-the-old-republic-2006'
    # base_url = 'http://www.readcomics.tv/comic/star-wars-darth-vader-and-the-ghost-prison'
    # base_url = 'http://www.readcomics.tv/comic/star-wars-darth-vader-and-the-ninth-assassin'
    # base_url = 'http://www.readcomics.tv/comic/star-wars-vader-down'
    # base_url = 'http://www.readcomics.tv/comic/darth-vader'
    # base_url = 'http://www.readcomics.tv/comic/obi-wan-and-anakin-2016'
    # base_url = 'http://www.readcomics.tv/comic/lando'
    # base_url = 'http://www.readcomics.tv/comic/chewbacca'
    # base_url = 'http://www.readcomics.tv/comic/star-wars-chewbacca-2004'
    # base_url = 'http://www.readcomics.tv/comic/injustice-gods-among-us-year-four'
    # base_url = 'http://www.readcomics.tv/comic/injustice-gods-among-us-year-five-2016'
    base_url = 'http://readcomics.website/comic/the-walking-dead-2003'

    # Extract the title from the url
    main_title = ((base_url.split('/')[-1]).replace('-', ' ')).title()

    comic_log = '{}.json'.format(main_title)
    comic_log = os.path.join(local_dir, comic_log)
    print('Looking for cached file: {}'.format(comic_log))

    if not os.path.isfile(comic_log):
        # Scrape chapters in the main page
        chapters = scrape_chapters(base_url, main_title)

        print('Found: {} comics'.format(len(chapters)))
        print('Collecting image data...')
        combined_total = 0
        comicbooks = {}

        # Scrape images in linked pages
        for chapter in chapters:
            comicbooks[chapter[0]] = scrape_links(chapter[1])
            # Display the name of the comic along with how many images it contains
            page_count = len(comicbooks[chapter[0]])
            combined_total += page_count
            print('  {0} has {1} pages'.format(chapter[0], page_count))

        print('Total images to be processed: {}'.format(combined_total))

        save(local_dir, main_title, comicbooks)
    else:
        with open(comic_log, 'r') as f:
            comicbooks = json.load(f)

    # Download all of the images for each comic
    download_image(local_dir, main_title, comicbooks)

    print('\nAll comics have been retrieved and compiled.')

if __name__ == '__main__':
    main()
