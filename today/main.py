#!/usr/bin/python3
# -*- coding:utf-8 -*-
import sys
import os
import logging
from PIL import Image, ImageDraw, ImageFont

import arrow
import requests
import icalendar
import time
import requests_cache
from datetime import timedelta

os.chdir("/home/pi/PaperProject/today")
# get OPENWEATHER_API_KEY from environment
OPENWEATHER_API_KEY = os.environ.get('OPENWEATHER_API_KEY')
print("Did we get key", OPENWEATHER_API_KEY)
libdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'lib')

if os.path.exists(libdir):
    sys.path.append(libdir)

import feedparser
from waveshare_epd import epd7in5b_V2

# enable DEBUG logging
logging.basicConfig(level=logging.DEBUG)

## Set up URLS we’ll use on this client
geo_call_url = "https://api.openweathermap.org/geo/1.0/direct?q=Seattle&limit=1&appid=" + OPENWEATHER_API_KEY
rss_feed = "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml"
cal_url = "https://p25-caldav.icloud.com/published/2/NjI5NjMzNjM2Mjk2MzM2M7P9vPAUf2XJwUfr0SHIekqR5OqcF_Cpvf7qcX7i1hTt"

session = requests_cache.CachedSession('xml_cache', expire_after=timedelta(minutes=5))
cal_session = requests_cache.CachedSession('cal_cache', expire_after=timedelta(minutes=5))
geo_session = requests_cache.CachedSession('geo_cache', expire_after=timedelta(hours=48))
weather_session = requests_cache.CachedSession('weather_cache', expire_after=timedelta(minutes=45))
weather_one_call_session = requests_cache.CachedSession('weather_one_call_cache', expire_after=timedelta(minutes=45))

german_word_session = requests_cache.CachedSession('german_word_cache', expire_after=7200)
t = icalendar.Calendar.from_ical(cal_session.get(cal_url).text)
rss_call = feedparser.parse(session.get(rss_feed).text)
geo = geo_session.get(geo_call_url).json()

# One-line lat and lon variables
seattle = [geo[0].get("lat"), geo[0].get("lon")]
weather = weather_session.get("https://api.openweathermap.org/data/2.5/weather?lat=" + str(seattle[0]) + "&lon=" + str(seattle[1]) + "&units=imperial&appid=" + OPENWEATHER_API_KEY).json()
one_call_weather = weather_one_call_session.get("https://api.openweathermap.org/data/2.5/onecall?lat=%s&lon=%s&units=imperial&exclude=minutely,daily&appid=%s" % (str(seattle[0]), str(seattle[1]), OPENWEATHER_API_KEY)).json()

# in one_call_weather, hourly is a list of dictionaries. Move the first five to an array of dictionaries
hourly_weather = []
for i in range(0, 3):
    hourly_weather.append(one_call_weather.get("hourly")[i])

# write out the one_call_weather call to a file so I can browse it
with open("one_call_weather.json", "w") as f:
    f.write(str(one_call_weather))

# Get a random german word and use google translate to translate it to english
# Strip out [""] from the text below
words = requests.get("https://nextjs-dareiff.vercel.app/api/single-word").json()
print(words)
german_word = words.get("word")
english_word = words.get("translation")

def matchweathericonwithlocalvariant(openweathermapiconname):
    # This function matches the openweathermap icon name to a local icon name
    # This is a dictionary of the openweathermap icon names and the local icon names
    print(openweathermapiconname)
    matching_weather_icon = ""
    if openweathermapiconname == "01d":
        matching_weather_icon = "clear"
    elif openweathermapiconname == "01n":
        matching_weather_icon = "nt_sunny"
    elif openweathermapiconname == "02d":
        matching_weather_icon = "partlycloudy"
    elif openweathermapiconname == "02n":
        matching_weather_icon = "nt_partlycloudy"
    elif openweathermapiconname == "03d":
        matching_weather_icon = "cloudy"
    elif openweathermapiconname == "03n":
        matching_weather_icon = "nt_cloudy"
    elif openweathermapiconname == "04d":
        matching_weather_icon = "mostlycloudy"
    elif openweathermapiconname == "04n":
        matching_weather_icon = "nt_mostlycloudy"
    elif openweathermapiconname == "09d":
        matching_weather_icon = "chancerain"
    elif openweathermapiconname == "09n":
        matching_weather_icon = "nt_chancerain"
    elif openweathermapiconname == "10d":
        matching_weather_icon = "rain"
    elif openweathermapiconname == "10n":
        matching_weather_icon = "nt_rain"
    elif openweathermapiconname == "11d":
        matching_weather_icon = "tstorms"
    elif openweathermapiconname == "11n":
        matching_weather_icon = "nt_tstorms"
    elif openweathermapiconname == "13d":
        matching_weather_icon = "snow"
    elif openweathermapiconname == "13n":
        matching_weather_icon = "nt_snow"
    elif openweathermapiconname == "50d":
        matching_weather_icon = "fog"
    elif openweathermapiconname == "50n":
        matching_weather_icon = "nt_fog"

    return "/home/pi/PaperProject/today/icons/png/128x128/" + matching_weather_icon + ".png"

try:
    epd = epd7in5b_V2.EPD()
    epd.init()

    font18 = ImageFont.truetype('Helvetica.ttc', 18)
    font24 = ImageFont.truetype('Helvetica.ttc', 24)
    font24bold = ImageFont.truetype('Helvetica.ttc', size=24, index=1)
    font40 = ImageFont.truetype('Helvetica.ttc', 40)
    font60 = ImageFont.truetype('Helvetica.ttc', 60)
    font80 = ImageFont.truetype('Helvetica.ttc', 80)
    fontLiterata = ImageFont.truetype('Literata_18pt-Regular.ttf', 18)
    fontLiterata40 = ImageFont.truetype('Literata_18pt-Regular.ttf', 40)

    # Instantiate our different images
    RedImage = Image.new('1', (epd.height, epd.width), 255)
    draw_red = ImageDraw.Draw(RedImage)
    BlackImage = Image.new('1', (epd.height, epd.width), 255)
    draw_black = ImageDraw.Draw(BlackImage)


    ### ADD THE DAY AT THE TOP OF THE SCREEN ###
    draw_black.text((10, 0), time.strftime("%A"), fill=0, font=font80)
    ### ADD THE TIME AT THE TOP OF THE SCREEN ###
    draw_black.text((10, 80), time.strftime("%I:%M"), font=font60, fill=0)
    ### ADD DATE NEXT TO TIME ###
    draw_black.text((180, 92), time.strftime("%m/%d"), fill=0, font=font24)

    draw_black.text((10, 160), german_word, font=font24bold, fill=0)
    draw_black.text((10 + font24bold.getsize(german_word)[0], 160), " - " + english_word, font=font24, fill=0)

    # Add weather for the next hour for area code 98103
    logging.info("3. Add weather")

    # Don't use decimals for temperature
    weather_temp = int(weather["main"]["temp"])
    weather_desc = weather["weather"][0]["description"]
    weather_icon_url = matchweathericonwithlocalvariant(weather["weather"][0]["icon"])
    weather_icon = Image.open(weather_icon_url)
    # Draw weather icon in the upper-right corner
    draw_black.bitmap((epd.height - 128, -10), weather_icon, fill=0)
    draw_black.text((epd.height - 90, 120), str(weather_temp) + "°", font=font40, fill=0, align="center")


    # Walk through the events from today and add them to an array
    logging.info("2. Add events")
    events = []
    eventtimes = []
    for component in t.walk():
        if component.name == "VEVENT":
            start = arrow.get(component["DTSTART"].dt)
            end = arrow.get(component["DTEND"].dt)
            if start.date() == arrow.now().date():
                events.append(component["SUMMARY"].to_ical().decode("utf-8"))
                eventtimes.append(start.format("HH:mm"))
    # # Sort the events by time
    # events.sort(key=lambda x: eventtimes.index(x.split(" ")[1]))
    # Add the events to the frame
    for i in range(len(events)):
        draw_black.text((10, i*30+200), eventtimes[i], fill=0, font=font24bold)
        draw_black.text((100, i*30+200), events[i], font=font24, fill=0)

    logging.info("4. Add weather")
    for i in range(len(hourly_weather)):
        hourly_weather_icon_url = matchweathericonwithlocalvariant(hourly_weather[i]["weather"][0]["icon"])
        hourly_weather_icon = Image.open(hourly_weather_icon_url)
        # hourly_weather_icon = hourly_weather_icon.resize((100, 100), Image.BICUBIC)
        # draw weather icon halfway down screen; if the "rain" key exists, draw it in red instead of black
        draw_black.bitmap((i*128 + 20, epd.height - 128), hourly_weather_icon, fill=0)
        draw_black.text((i*135 + 60, epd.height), str(int(hourly_weather[i]["temp"])) + "°", font=font24, fill=0, align="center")

    # Add a random headline from the RSS feeds to the bottom of the display with font24
    logging.info("5. Add headline from NYT")
    rsses = []
    text = rss_call
    for posts in text.entries:
        rsses.append(posts.title)

    # Draw a NEWS header
    draw_red.text((10, epd.width - 180), "NEWS", font=fontLiterata40, fill=0)
    # Display 3 headlines from the RSS feeds
    startheight = epd.width - 140
    for i in range(3):
        draw_black.text((10, startheight + i*30), rsses[i], font=fontLiterata, fill=0)

    logging.info("6. Write image to file")
    RedImage.save('RedImage.bmp')
    BlackImage.save('BlackImage.bmp')

    epd.display(epd.getbuffer(BlackImage), epd.getbuffer(RedImage))
    time.sleep(2)

    logging.info("Goto Sleep...")
    epd.sleep()

except IOError as e:
    logging.info(e)

except KeyboardInterrupt:
    logging.info("ctrl + c:")
    epd7in5b_V2.epdconfig.module_exit()
    exit()
