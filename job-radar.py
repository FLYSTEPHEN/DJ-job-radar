#!/usr/bin/env python
# coding: utf-8

# In[19]:


import requests
from bs4 import BeautifulSoup
def scrape_careers_information(page_url):
    r = requests.get(page_url)
    data = BeautifulSoup(r.text,"html.parser")
    jobs= []
    all_div = data.find_all('div', attrs={'class':"bti-ui-job-detail-container"}) 
    for i in all_div:
        job=[]
        job.append(i.find('a').text)
        # title
        job.append(i.find('div', attrs={'class':"bti-ui-job-result-detail-employer"}).text.strip())
        # company
        job.append(i.find('div', attrs={'class':"bti-ui-job-result-detail-location"}).text.strip())
        # company address
        job.append(i.find('div', attrs={'class':"bti-ui-job-result-detail-age"}).text.strip())
        # post date
        job.append('https://careers.journalists.org{}'.format(i.find('a')['href']))
        # page url
        job.append('NaN')
        # job status
        job.append('careers')
        # source website
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
        job = []
        job.append(i.a['title'])
        job.append(i.parent.find('span', attrs={'class':"company"}).text.strip()) 
        #use .parent back to the higher label
        job.append(i.parent.find('span', attrs={'class':"location"}).text.strip())
        job.append(i.parent.find('span', attrs={'class':"date"}).text.strip())
        job.append('https://www.indeed.com/viewjob?jk={}'.format(i['id'][3:]))
        job.append('NaN')
        job.append('indeed')
        if job not in all_jobs:
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
        job=[]
        job.append(i.find('div', attrs={'class':"_3gfm7U9 _3ho-Knb _2swcdgn"}).a.text)
        job.append(i.find('div', attrs={'class':"_1NdWRqw _3ho-Knb _2swcdgn"}).find('span').text)
        job.append(i.find('div', attrs={'class':"_124cxoK _3ho-Knb _2swcdgn"}).find('span').text)
        job.append(i.find('span', attrs={'class':"JG37Vx2 _3Re95QG _2XGgj_O"}).find('span').text)
        job.append(i.find('div', attrs={'class':"_3gfm7U9 _3ho-Knb _2swcdgn"}).a['href'])
        job.append('NaN')
        job.append('jobsdb')
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
        if len(all_jobs) > 20: #only scrape 20 jobs from each website
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


# In[21]:


import csv
from os import remove
try:
    e = open('existed-jobs.csv','r')
    jobs_existed_url = [row[4] for row in csv.reader(e)]
    e.close()
except FileNotFoundError:
    jobs_existed_url = []
try:
    remove('new-jobs.csv')
except FileNotFoundError:
    pass
for i in websites:
    scrape_all_information(i["base_url"],i["starting_index"],i["step"],i["function_scrape_information"])
    e = open('existed-jobs.csv','a')
    n = open('new-jobs.csv','a')
    for a in all_jobs:
        if a[4] not in jobs_existed_url: #duplicate checking
            csv.writer(e).writerow(a)
            csv.writer(n).writerow(a)
    e.close()
    n.close()


# - since we scrap the other information from the index page of each website to make the operation quicker. we need go deep into the page of each job to get their description. As a result, we need to read the existed csv first. We also define two functions for each website to scrape a job's description and the other information.

# In[22]:


import pandas as pd
for i in ['existed-jobs.csv','new-jobs.csv']:
    try:
        df=pd.read_csv(i, header=None, names=['Title','Company','Location','Date','URL','Current Status','Source'])
        urls_and_sources = zip(df['URL'].tolist(), df['Source'].tolist())
        df['Description'] = scrape_all_description(urls_and_sources)
        df.to_csv('{}-with-description.csv'.format(i[:-4]),na_rep='NaN')
    except FileNotFoundError:
        pass

