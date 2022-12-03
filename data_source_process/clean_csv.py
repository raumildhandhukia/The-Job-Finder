import pandas as pd
import re
import geonamescache


def clean_data(file_name):
    job_file = pd.read_csv(file_name)
    d = job_file[~job_file['description'].str.contains(r'[^\x00-\x7F]+')]
    d.to_csv(file_name, index=False)


CLEANR = re.compile('<.*?>')


def cleanhtml(raw_html):
    cleantext = re.sub(CLEANR, '', raw_html)
    return cleantext


def location_filter(location):
    us_states = {sc: sd['name'] for sc, sd in geonamescache.GeonamesCache().us_states.items()}
    if location.count(',') == 1:
        city_state_comb = location.split(',')
        city_state_comb = list(map(lambda str: str.strip(), city_state_comb))
        if city_state_comb[1] in us_states:
            city_state_comb[1] = us_states[city_state_comb[1]]
        location = ", ".join(city_state_comb)
        return location
    return False
