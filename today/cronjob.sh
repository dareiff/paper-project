#!/bin/sh

export OPENWEATHER_API_KEY="547ac905697f975640ad2029c10a69f6"
export ICAL_URL="https://p25-caldav.icloud.com/published/2/NjI5NjMzNjM2Mjk2MzM2M7P9vPAUf2XJwUfr0SHIekqR5OqcF_Cpvf7qcX7i1hTt"

source /home/pi/.profile
python3 /home/pi/PaperProject/today/main.py