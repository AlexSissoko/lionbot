from bs4 import BeautifulSoup
import requests
from random import randint
import os, sys
import json
import urllib.parse
import datetime, time

#from menu_scraper import get_menus

def dining_events_msg(result):
    """Interface Function for dining events intent"""
    msg = ""
    try:
        events = getDiningEvents()
    except:
        events = []
    if (events == []):
        msg = "Looks like there's no upcoming Dining Events. Check back later."
    else:
        for i in range(len(events)):
            msg += events[i]
    return msg

def dining_hall_food_request_msg(result):
    """Interface Function for food request intent"""
    try:
        food = result['parameters']['dining_hall_food'][0]
    except:
        error = "Could you ask that again? I don't know what food to check for."
        print( "error sent")
        return error
    #halls = result['parameters']['dining_halls']
    try:
        halls = result['parameters']['dining_halls']
        if len(halls) < 1:
            halls = []
        elif halls == []:
            halls = []
        else: 
            halls = halls 
    except:
        halls = []
    request_check = food_request(food, halls)
    if request_check:
        for key in request_check:
            response = key + " has:\n"
            #bot.send_text_message(recipient_id,key)
            for food in request_check[key]:
                response += food + "\n"
            response = response[:len(response) -1]
            return response
    else:
        msg1 = "Looks like %s is not available in the dining halls you asked me to check." % food
        return msg1

def getDiningEvents():
    url = "http://dining.columbia.edu/events"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    #get three collections of tag objects for events, dates, locations respectively
    letters1 = soup.find_all("div", class_="views-field-title")
    letters2 = soup.find_all("div", class_="views-field-field-event-date-value")
    letters3 = soup.find_all("div", class_="views-field-field-event-location-value")


    num = len(letters1)
    res = []

    for i in range(num):
        outStr = "Event: " + letters1[i].find("span", class_="field-content").get_text() + "\nTime: " + letters2[i].find("span", class_="date-display-single").get_text() + "\nLocation: " + letters3[i].find("span",class_="field-content").get_text() + "\n"
        res.append(outStr)
    return(res)

def food_request(foodname, halls="all"):
    check_all = ["dining hall"]
    requested_food = foodname
    try:
        menus = get_menus()
    except:
        return {}
    relevant_hall_dict = {}
    if halls == "all":
        check_all_dining_halls(requested_food, menus, relevant_hall_dict)
    elif len(halls) == 0:
        check_all_dining_halls(requested_food, menus, relevant_hall_dict)

    else:
        for key in halls:
            if key == "dining hall" or key == "":
                check_all_dining_halls(requested_food, menus, relevant_hall_dict)
            else:
                matched_foods = []
                try:
                    menu = menus[key]
                    for food in menu:
                        if requested_food.lower() in food.lower():
                            matched_foods.append(food)
                            relevant_hall_dict[key] = matched_foods
                except:
                    continue
        return relevant_hall_dict
    return {}

def check_all_dining_halls(requested_food, menus, relevant_hall_dict):
    for key in menus:
        matched_foods = []
        try:
            menu = menus[key]
            for food in menu:
                if requested_food.lower() in food.lower():
                    matched_foods.append(food)
                    relevant_hall_dict[key] = matched_foods
        except:
            continue
    return relevant_hall_dict

""" Given a URL, returns a BeautifulSoup object for that page
"""


def get_soup(url):
    #raw_page = urllib.request.urlopen(url).read()
    #soup = BeautifulSoup(raw_page, "html.parser")
    raw_page = requests.get(url)
    soup = BeautifulSoup(raw_page.text, "lxml")
    return soup


""" Builds the URL for the menu of a specific dining hall
"""


def get_hall_url(hall_id):
    url = 'http://dining.columbia.edu/?quicktabs_homepage_menus_quicktabs='
    url = url + str(hall_id)
    url = url + '#quicktabs-homepage_menus_quicktabs'
    return url


""" Returns a dictionary where the keys are the names of each dining hall with
    menu on dining.columbia.edu and the value for each key is a list of the
    menu items for that dining hall.

    Some logic borrowed from:
    https://github.com/samlouiscohen/starting/blob/master/sortedFood_crawler.py
"""


def get_menus():
    menus = {}

    for hall_id in range(3):
        url = get_hall_url(hall_id)
        soup = get_soup(url)
        hall = soup.find_all("li", class_="qtab-" + str(hall_id))
        try:
            hall_name = str(hall[0].a.get_text()).lstrip('u')
        except:
            hall_name = "None"
        food_elements = soup.find_all("span", class_="meal-title-calculator")
        foods = [str(elem.get_text()).lstrip('u') for elem in food_elements]

        menus[hall_name] = foods

    for hall_id in ["Hewitt", "Diana"]:
        menus[hall_id] = get_barnard(hall_id)
    return menus


""" This prints out the menus of each dining hall to the terminal
"""


def print_menus(menus):
    for hall in menus:
        print("\n\nDINING HALL: " + hall)
        menu = menus[hall]

        for food in menus[hall]:
            print("\n" + food)


"""
gets the barnard food
PS: the food is not seperated in a list, it is just a string
get food not available for barnard
"""


def get_barnard(arg):
    r = requests.get('https://barnard.edu/dining/menu/' + arg)
    soup = BeautifulSoup(r.text, "lxml")
    #r = urllib.request.urlopen('https://barnard.edu/dining/menu/' + arg).read()
    #soup = BeautifulSoup(r, "html.parser")

    # get three collections of tag objects for events, dates, locations respectively
    menu = soup.find_all("p", style="white-space: pre-wrap;")

    now = datetime.datetime.now()

    food = ''
    liist = []

    if len(menu) > 0:
        if arg == "Hewitt":
            if now.strftime("%A") == "Sunday" or len(menu) < 3 or now.hour < 12:
                food = menu[0].text
            elif now.hour < 15:
                food = menu[1].text
            else:
                food = menu[2].text
        elif arg == "Diana":
            if len(menu) < 2 or now.hour < 12:
                food = menu[0].text
            else:
                food = menu[1].text

        liist = food.split("\n")

        liist = list(filter(lambda x: x != '', liist))

    else:
        liist.append('error')
    return liist

""" This opens 'http://dining.columbia.edu/menus' and prints out the foods on
    the menu of the currently selected dining hall. Because this changes, we'll
    need to click on each dining hall and have the bot collect all the info.
"""

def dining_hall_menu_msg(result):
    menus = get_menus()
    halls = result['parameters']['dining_halls']
    if len(halls) < 1:
        mistake = "Can you ask me that again? I don't know which dining hall to check."
        return mistake
    for hall in halls:
        if hall == "dining hall":
            mistake = "Can you ask me that again? I don't know which dining hall to check."
            return mistake;
        try:
            menu = menus[hall]
            if len(menu) < 1:
                closed = "Looks like %s is closed right now." % hall
                return closed
            else:
                menu_list = "Here's what's available at %s right now:\n" % hall
                for item in menu:
                    menu_list += item + "\n"
                return menu_list
        except:
            msg = "Looks like I can't currently find any information about %s." % hall
            return msg
    return "success"

