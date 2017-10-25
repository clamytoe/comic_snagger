#!/usr/bin/env python
"""
Scrape http://readcomicbooksonline.net for comic book images
"""
import shutil
import os
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys


def init_browser():
    """
    Initialize the browser object with all of its needed options
    """
    browser = webdriver.Firefox()

    return browser


def scrape_chapters(soup):
    """
    Scrape the title and url of all the chapters in the page
    """
    chapter_soup = soup
    # chapters = chapter_soup.find_all(class_='ch-name')
    chapters = chapter_soup.find_all(class_='chapter-title-rtl')
    total_chapters = len(chapters)
    comic = {}
    
    for x in range(total_chapters):
        title = chapters[x].contents[0]
        link = chapters[x]['href'] + '/full'
        img = []
        comic[x] = [title, link, img]

    return comic


def scrape_links(data):
    """
    Scrape links pointing to the comic book chapters
    """
    page = BeautifulSoup(data)

    images = page.find_all(class_='chapter_img')
    image_links = []

    for img in images:
        image_links.append(img['src'])

    return image_links


def download_image(local_dir, title, directory, images):
    """
    Retrieve and save all of the images
    """
    browser = init_browser()
    title_dir = os.path.join(local_dir, title)
    comic_dir = os.path.join(title_dir, directory)
    print('\nProcessing: {}...'.format(directory))

    # Create the main directory for our title
    try:
        os.makedirs(title_dir)
    except OSError:
        pass

    if not os.path.isfile(comic_dir + '.cbz'):
        for img in images:
            page = img.split('/')[-1]
            num, ext = page.split('.')

            # Pad the number with a zero
            if int(num) < 10:
                num = '0' + str(num)
            page = num + '.' + ext
            filename = os.path.join(comic_dir, page)
            try:
                os.makedirs(comic_dir)
            except OSError:
                pass

            if not os.path.isfile(filename):
                print('\tSaving: {}'.format(filename))

                try:
                    browser.retrieve(img, filename)
                except KeyboardInterrupt:
                    print('\nDownload interrupted by the user.')
                    quit()
            else:
                print('\tFile: {} already exists, skipping'.format(page))

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
    title = ((base_url.split('/')[-1]).replace('-', ' ')).title()
    browser = init_browser()
    soup = None

    # Try to retrieve the list of chapters
    try:
        page = browser.open(base_url)
        print('Processing: {}...'.format(title))
        soup = BeautifulSoup(page)
        page.close()
    except:
        print('You must be connected to the Internet in order for this to work...')
        quit()

    # Scrape chapters in the main page
    comics = scrape_chapters(soup)
    total = len(comics)
    print('Found: {} chapters'.format(total))
    print('Collecting image data...')

    # Scrape images in linked pages
    for i in range(total):
        data = browser.open(comics[i][1])
        comics[i][2] = scrape_links(data)

    # Display the name of the comic along with how many images it contains
    combined_total = 0
    for x in range(total):
        page_count = len(comics[x][2])
        combined_total += page_count
        print('\t{0}: {1} images'.format(comics[x][0], page_count))

    print('Total images to be processed: {}'.format(combined_total))

    # Download all of the images for each comic
    for y in range(total):
        download_image(local_dir, title, comics[y][0], comics[y][2])

    print('\nAll comics have been retrieved and compiled.')

if __name__ == '__main__':
    main()
