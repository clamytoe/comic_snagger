# comicSnagger
Python script for downloading comics from http://www.readcomics.tv. Once you provide the entry page for the comic that you want, it will download all of the issues for it. At this time, it only downloads all of the issues.

## Backstory
I wrote this script for my kids. I have limited bandwidth at home, so to prevent them each from reading them online at different times I decided to just download them once. 

## Requirements
You will need to have mechanize and BeautifulSoup in order to use. It's still using Python 2, but I'll try to convert it to 3. I hope it's pretty self explanatory, but I do plan on writing a more proper Readme once I have more time.

## How To Run
You will need to provide the `local_dir` for where you want your comics to be saved. Then all you have to do is provide the `base_url` for the comic that you want to download. I've left some examples in the script.

## NOTE
If you stop a download or your connection drops, check the last image. More than likely you will have to remove it if it didn't download completely. You can tell if there is nothing butblack towards to bottom of the image. If you re-run the script on the same comic, it will resume where it left off or download any new comics if you maintain the established file structure.
