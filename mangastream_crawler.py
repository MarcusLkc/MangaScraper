"""This module checks for new manga updates from mangastream and
sends user emails when new updates have been released

Raises:
    Exception: raises an exception when user email was not provided

Returns:
    [type]: [description]
"""
import json
import smtplib
import requests
from bs4 import BeautifulSoup

GMAIL_USER = ""
GMAIL_PASSWORD = ""

if not GMAIL_USER or not GMAIL_PASSWORD:
    raise Exception('Please set your username and password')


def crawl_mangastream_for_links():
    """This function crawls the mangastream website

    Returns:
        list: returns list of bs4 a tags
    """

    url = 'https://readms.net'

    html = requests.get(url)

    soup = BeautifulSoup(html.text)

    new_list = soup.find('ul', {"class": "new-list"})
    return new_list.findAll('a')


def get_favorite_mangas():
    """Opens a json file which list reads from favorite_mangas.json

    Returns:
        dict: a dictionary of favorite mangas where the key is the name
              and the value is the chapter number
    """
    with open('favorite_mangas.json', 'r') as outfile:
        favorite_mangas = json.load(outfile)
    return favorite_mangas


def save_favorite_mangas(favorite_mangas):
    """Saves the updated dictionary of favorite mangas to json file

    Args:
        favorite_mangas (dict): dictionary of favorite mangas [name]:[chapter]
    """
    with open('favorite_mangas.json', 'w') as outfile:
        json.dump(favorite_mangas, outfile)


def send_email(new_chapters):
    """Sends an email notifying user of new chapters

    Args:
        new_chapters (list): a list of strings that represents manga titles
    """
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.login(GMAIL_USER, GMAIL_PASSWORD)
    sent_from = GMAIL_USER
    to = GMAIL_USER
    subject = 'New Manga Chapters Out'
    body = '\n'.join(new_chapters)

    email_text = "Subject: {}\n{}".format(subject, body)

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(GMAIL_USER, GMAIL_PASSWORD)
        server.sendmail(sent_from, to, email_text)
        server.close()

        print('Email sent!')
    except Exception as e:
        print(e)


def check_for_new_chapters():
    """Utility function that checks for new manga chapters from mangastream
    """
    update = False
    favorite_mangas = get_favorite_mangas()
    links = crawl_mangastream_for_links()
    new_chapters = []
    for link in links:
        contents = link.contents
        if link.find('i', {'class': 'fa fa-star'}):
            name = str(contents[2]).strip()
            chapter = contents[3].text
        else:
            name = str(contents[1]).strip()
            chapter = contents[2].text
        chapter = int(chapter)
        if name in favorite_mangas and chapter > favorite_mangas[name]:
            update = True
            favorite_mangas[name] = chapter
            new_chapters.append(name)

    if update:
        save_favorite_mangas(favorite_mangas)

        send_email(new_chapters)


if __name__ == "__main__":
    check_for_new_chapters()
