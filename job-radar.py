#!/usr/bin/env python
# coding: utf-8

# In[1]:


import requests
from bs4 import BeautifulSoup
import numpy as np


def scrape_careers_information(page_url):
    r = requests.get(page_url)
    data = BeautifulSoup(r.text,"html.parser")
    jobs= []
    all_div = data.find_all('div', attrs={'class':"bti-ui-job-detail-container"}) 
    for i in all_div:
        job={}
        job['Title'] = i.find('a').text
        job['Company'] = i.find('div', attrs={'class':"bti-ui-job-result-detail-employer"}).text.strip()
        job['Location'] = i.find('div', attrs={'class':"bti-ui-job-result-detail-location"}).text.strip()
        job['Date'] = i.find('div', attrs={'class':"bti-ui-job-result-detail-age"}).text.strip()
        job['URL'] = 'https://careers.journalists.org{}'.format(i.find('a')['href'])
        job['Current Status'] = np.nan
        job['Source'] = 'careers'
        job['Description'] = np.nan
        jobs.append(job)
    return jobs
def scrape_careers_description(description_url):
    r = requests.get(description_url)
    data = BeautifulSoup(r.text,"html.parser")
    return data.find('div', attrs={'class':"bti-jd-description"}).text

def scrape_indeed_information(page_url):
    r = requests.get(page_url)
    data = BeautifulSoup(r.text,"html.parser")
    jobs= []
    all_h2 = data.find_all('h2', attrs={'class':"jobtitle"}) 
    #it's a weirdo page that the last item's 'class' is different from above 9, so that we use its sub label h2.
    for i in all_h2:
        job = {}
        job['Title'] = i.a['title']
        job['Company'] = i.parent.find('span', attrs={'class':"company"}).text.strip()
        #ust back to the higher label
        job['Location'] = i.parent.find('span', attrs={'class':"location"}).text.strip()
        job['Date'] = i.parent.find('span', attrs={'class':"date"}).text.strip()
        job['URL'] = 'https://www.indeed.com/viewjob?jk={}'.format(i['id'][3:])
        job['Current Status'] = np.nan
        job['Source'] = 'indeed'
        job['Description'] = np.nan
        jobs.append(job)
        #when the index url exceeds the range of pages in indeed, the page will become circulation, so that we should do duplicate checking
    return jobs

def scrape_indeed_description(description_url):
    r = requests.get(description_url)
    data = BeautifulSoup(r.text,"html.parser")
    return data.find('div', attrs={'class':"jobsearch-JobComponent-description icl-u-xs-mt--md"}).text

def scrape_jobsdb_information(page_url):
    r = requests.get(page_url)
    data = BeautifulSoup(r.text,"html.parser")
    jobs= []
    all_div = data.find_all('div', attrs={'class':"_3ASfTyv _2EUSthc"})
    for i in all_div:
        job={}
        job['Title'] = i.find('div', attrs={'class':"_3gfm7U9 _3ho-Knb _2swcdgn"}).a.text
        job['Company'] = i.find('div', attrs={'class':"_1NdWRqw _3ho-Knb _2swcdgn"}).find('span').text
        job['Location'] = i.find('div', attrs={'class':"_124cxoK _3ho-Knb _2swcdgn"}).find('span').text
        job['Date'] = i.find('span', attrs={'class':"JG37Vx2 _3Re95QG _2XGgj_O"}).find('span').text
        job['URL'] = i.find('div', attrs={'class':"_3gfm7U9 _3ho-Knb _2swcdgn"}).a['href']
        job['Current Status'] = np.nan
        job['Source'] = 'jobsdb'
        job['Description'] = np.nan
        jobs.append(job)
    return jobs
    
def scrape_jobsdb_description(description_url):
    r = requests.get(description_url)
    data = BeautifulSoup(r.text,"html.parser")
    return data.find('div', attrs={'class':"jobad-primary"}).text

def scrape_all_information(base_url,starting_index,step,function_scrape_information):
    global all_jobs
    all_jobs = []
    page_index = starting_index
    while True: 
        page_url = '{}{}'.format(base_url,page_index)
        try:
            jobs = function_scrape_information(page_url)
        except:
            jobs = []   
        if jobs == []: #if all jobs have been scraped, break the loop
            break
        all_jobs.extend(jobs)
        if len(all_jobs) > 10: #only scrape 20 jobs from each website
            break
        page_index += step  #level is in url to indiccate different pages' index
#     all_jobs.sort(key=lambda item: item[3], reverse=False) 

def scrape_all_description(urls_and_sources):
    list_descriptions = []
    list_websites = [m["source"] for m in websites]
    list_functions = [i["function_scrape_description"] for i in websites]
    for u, s in urls_and_sources:
        list_descriptions.append(list_functions[list_websites.index(s)](u))
    return list_descriptions

websites = [
    {
        "source": 'careers',
        "base_url": 'https://careers.journalists.org/jobs/?keywords=data+OR+journalist&page=',
        "starting_index": 1,        
        "step": 1,
        "function_scrape_information": scrape_careers_information,
        "function_scrape_description": scrape_careers_description,
    }, 
    {
        "source": 'indeed',
        "base_url": 'https://www.indeed.com/jobs?q=Data+Journalist+Internship&start=',
        "starting_index": 0,        
        "step": 10,
        "function_scrape_information": scrape_indeed_information,
        "function_scrape_description": scrape_indeed_description,
    },
    {
        "source": 'jobsdb',
        "base_url": 'https://hk.jobsdb.com/hk/search-jobs/data-journalist/',
        "starting_index": 1,        
        "step": 1,
        "function_scrape_information": scrape_jobsdb_information,
        "function_scrape_description": scrape_jobsdb_description,
    },
]  


# In[3]:


import pandas as pd
import numpy as np
header = ['Title','Company','Location','Date','URL','Current Status','Source','Description']
try:
    df = pd.read_csv('jobs.csv', header = 0, names = header)
except FileNotFoundError:
    df = pd.DataFrame(columns = header)
for i in websites:
    scrape_all_information(i["base_url"],i["starting_index"],i["step"],i["function_scrape_information"])
    df = df.append(all_jobs,ignore_index=True)
df = df.drop_duplicates(['URL']) #drop dupilictes according to URL
urls_and_sources = zip(df['URL'].tolist(), df['Source'].tolist())
df['Description'] = scrape_all_description(urls_and_sources)
df.to_csv('jobs.csv',na_rep='NaN')

