"""
test_comic_snagger.py

Test for comic_snagger.
"""
import os

import pytest
from bs4 import BeautifulSoup, element

import comic_snagger as cs


@pytest.fixture(scope="module")
def dt_comics():
    """Dark Tower Comics Soup"""
    soup_dump_comics = os.path.join("tests", "dark_tower_comics.html")
    with open(soup_dump_comics) as f:
        comic_soup = BeautifulSoup(f, "html.parser")
    return comic_soup


@pytest.fixture(scope="module")
def dt_images():
    """Dark Tower Images Soup"""
    soup_dump_images = os.path.join("tests", "dark_tower_images.html")
    with open(soup_dump_images) as f:
        images_soup = BeautifulSoup(f, "html.parser")
    return images_soup


@pytest.fixture(scope="module")
def dt_series():
    """Dark Tower Series Soup"""
    soup_dump_series = os.path.join("tests", "dark_tower_series.html")
    with open(soup_dump_series) as f:
        series_soup = BeautifulSoup(f, "html.parser")
    return series_soup


def test_soup(dt_comics, dt_images, dt_series):
    """Tests that BeautifulSoup objects are being created properly"""
    assert isinstance(dt_comics, BeautifulSoup)
    assert isinstance(dt_images, BeautifulSoup)
    assert isinstance(dt_series, BeautifulSoup)


def test_search_for_series(dt_series):
    """Test search for series function"""
    m_series = cs.search_for_series(dt_series)
    assert isinstance(m_series, list)
    assert isinstance(m_series[0], cs.Comic)
    assert len(m_series) == 22
    assert (
        m_series[0].title == "Dark Tower - The Drawing of the Three - "
        "Lady of Shadows"
    )


def test_scrape_chosen_comic(dt_comics):
    """Test scrape chosen comic function"""
    m_comics = cs.scrape_chosen_comic(dt_comics)
    assert isinstance(m_comics, list)
    assert isinstance(m_comics[0], element.Tag)
    assert len(m_comics) == 5
    assert (
        m_comics[0].text == "Dark Tower - The Drawing of the Three - Lady"
        " of Shadows #5"
    )


def test_scrape_comics_found(dt_comics):
    """Test scrape comics found function"""
    m_issues = cs.scrape_chosen_comic(dt_comics)
    m_chapters = cs.scrape_comics_found(m_issues)
    assert isinstance(m_chapters, list)
    assert isinstance(m_chapters[0], cs.Comic)


def test_display_genres(dt_comics, capfd):
    """Test the creation of the genres heading"""
    expected = "[Ongoing] [Horror] [Marvel] [Graphic Novels] [Mature] " \
               "[Mystery]\n\n"
    cs.display_genres(dt_comics)
    output = capfd.readouterr()[0]
    assert output == expected


def test_get_links(dt_images):
    """Test get links function"""
    links = cs.get_links(dt_images)
    assert isinstance(links, list)
    assert len(links) == 29
    assert links[0].rsplit("/", 1)[1] == "1.jpg"
    assert links[-1].rsplit("/", 1)[1] == "29.jpg"


def test_generate_command():
    """Test generate wget command function"""
    link = "https://readcomics.io/images/manga/dark-tower-the-drawing-of-the" \
           "-three-lady-of-shadows/1/1.jpg"
    directory = "dark-tower-the-drawing-of-the-three-lady-of-shadows"
    command = cs.generate_command(link, directory)
    assert "wget" in command
    assert "--no-verbose" in command
    assert "--show-progress" in command
    assert " -c " in command
    assert " -O " in command
    assert "01.jpg" in command
