import json
import csv
import clean_csv as cc
import pandas as pd


def dump_to_csv():
    headers = list()
    with open('jobs.json', 'r') as f:
        data = json.load(f)
        for job in data:
            for key, value in job.items():
                if key not in headers:
                    headers.append(key)

    with open('jobs.csv', 'w', encoding='UTF8') as f:
        writer = csv.writer(f)
        # write the header
        job_headers = ['id']
        job_headers.extend(headers)
        writer.writerow(job_headers)
        job_id = 0
        for job in data:
            add_job = 1
            job_data = []
            for header in headers:
                if header in job:
                    if header == 'locations':
                        location = cc.location_filter(job[header])
                        if not location:
                            add_job = 0
                            break
                        job_data.append(location)
                    else:
                        value = cc.cleanhtml(job[header])
                        if '&pound;' in value:
                            value = value.replace('&pound;', '£')
                        job_data.append(value)
                else:
                    job_data.append('')
            if add_job:
                job_id += 1
                job_values = ["job"+str(job_id)]
                job_values.extend(job_data)
                writer.writerow(job_values)
    companies = dict()
    job_data = pd.read_csv('jobs.csv')
    with open('companies.csv', 'w', encoding='UTF8') as f:
        writer = csv.writer(f)
        for index, job in job_data.iterrows():
            if 'company' in job and job['company']:
                if job['company'] in companies:
                    companies[job['company']] += 1
                else:
                    companies.update({
                        job['company']: 1
                    })
        writer.writerow(['id', 'company'])
        company_id = 0
        for company, number in companies.items():
            company_id += 1
            writer.writerow(["com"+str(company_id), company])
        output_data = []


    locations = dict()

    location_id = 0
    for index, job in job_data.iterrows():
        if job['locations'] not in locations:
            location_id += 1
            locations.update({
                job['locations']: "loc"+str(location_id)
            })

    for index, job in job_data.iterrows():
        job['company'] = "com" + str(companies[job['company']])
        job['locations'] = locations[job['locations']]
        output_data.append(list(job))
    df = pd.DataFrame(output_data, columns=job_headers)
    df.to_csv('jobs.csv', index=False)

    locations = {index: location.split(',') for location, index in locations.items()}

    indexed_locations, cities, states = dict(), dict(), dict()
    city_index, state_index = 0, 0
    for index, location in locations.items():
        city_index += 1
        cities.update({
            "city"+str(city_index): location[0]
        })

        if location[1].strip() not in list(states.keys()):
            state_index += 1
            states.update({location[1].strip(): "state" + str(state_index)})
        indexed_locations.update({
            index: ("city"+str(city_index), str(states[location[1].strip()]))
        })

    indexed_location_list = []
    for index, loc in indexed_locations.items():
        indexed_location_list.append([index, loc[0], loc[1]])
    df = pd.DataFrame(indexed_location_list, columns=['id', 'city_id', 'state_id'])
    df.to_csv('locations.csv', index=False)

    indexed_city_list = []
    for index, city in cities.items():
        indexed_city_list.append([index,city])
    df = pd.DataFrame(indexed_city_list, columns=['id', 'city'])
    df.to_csv('cities.csv', index=False)

    indexed_state_list = []
    for state, index in states.items():
        indexed_state_list.append([index, state])
    df = pd.DataFrame(indexed_state_list, columns=['id', 'state'])
    df.to_csv('states.csv', index=False)

