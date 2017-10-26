# comicSnagger
Python script for downloading comics from http://readcomics.website. Once you provide the entry page for the comic that you want, it will download all of the chapters for it. At this time, it only downloads all of them but I plan to give you a choice between the ones that are available.

## Backstory
I wrote this script for my kids. I have limited bandwidth at home, so to prevent them each from reading them online at different times I decided to just download them once. 

## Requirements
You will need to have requests and BeautifulSoup in order to use. It's written for Python 3, but it should work in 2 as well. I hope it's pretty self explanatory, but I do plan on writing a more proper Readme once I have more time.

## How To Run
You will need to provide the `local_dir` for where you want your comics to be saved. Then all you have to do is provide the `base_url` for the comic that you want to download. I've left an example in the script.

## NOTE
At this time, there is no clean way to stop the script, so you must let it run its course.
