from careerjet_api import CareerjetAPIClient
import geonamescache
import json


def get_jobs(job_key, location, cj, jobs):
    temp_results = cj.search({
        'location': location,
        'keywords': job_key,
        'affid': '213e213hd12344552',
        'user_ip': '11.22.33.44',
        'url': 'http://www.example.com/',
        'user_agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:31.0) Gecko/20100101 Firefox/31.0'
    })
    if 'jobs' in temp_results and temp_results['jobs']:
        temp_jobs = list(filter(lambda job: 'salary' in job and job['salary'], temp_results['jobs']))
        # temp_jobs =temp_results['jobs']
        jobs_with_single_location = list(filter(lambda job: '-' not in job['locations'], temp_jobs))
        jobs_with_multiple_location = list(filter(lambda job: '-' in job['locations'], temp_jobs))
        for j in jobs_with_multiple_location:
            locations = j['locations'].split('-')
            for location in locations:
                new_job = j.copy()
                new_job['locations'] = location.strip()
                jobs.append(new_job)
        if jobs_with_single_location:
            for n_job in jobs_with_single_location:
                jobs.append(n_job)


def fetch_jobs():
    jobs = []
    gc = geonamescache.GeonamesCache()

    cj = CareerjetAPIClient("en_GB")
    job_keywords = ['python', 'data', 'java', 'frontend', 'backend', 'machine learning', 'software engineer',
                    'software developer', 'cyber security', 'database', 'artificial intelligence', 'blockchain',
                    'javascript', 'react', 'html', 'css', 'postgresql', 'mysql', 'php', 'information technology',
                    'gaming',
                    'software security']
    country_codes = ['IN', 'GB', 'RU', 'UAE', 'IT', 'JP', 'SA']
    states = gc.us_states
    cities = gc.get_cities()
    city_dict = [y for x, y in cities.items()]
    cities = list(map(lambda city: city['name'], filter(lambda city: city['countrycode'] in country_codes, city_dict)))[
             :200]

    for job_key in job_keywords:
        for state_key, state_info in states.items():
            state_name = state_info['name']
            get_jobs(job_key, state_name, cj, jobs)
        for city in cities:
            get_jobs(job_key, city, cj, jobs)

    with open("jobs.json", "w") as outfile:
        json.dump(jobs, outfile)
