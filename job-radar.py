import requests
from bs4 import BeautifulSoup
import csv


def scrape_careers(data):
    jobs= []
    all_div = data.find_all('div', attrs={'class':"bti-ui-job-detail-container"}) 
    for i in all_div:
        job=[]
        job.append(i.find('a').text)
        job.append(i.find('div', attrs={'class':"bti-ui-job-result-detail-employer"}).text.strip())
        job.append(i.find('div', attrs={'class':"bti-ui-job-result-detail-location"}).text.strip())
        job.append(i.find('div', attrs={'class':"bti-ui-job-result-detail-age"}).text.strip())
        job.append('https://careers.journalists.org{}'.format(i.find('a')['href']))
        jobs.append(job)
    return jobs

def scrape_indeed(data):
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
        if job not in all_jobs:
            jobs.append(job)
        #when the index url exceeds the range of pages in indeed, the page will become circulation, so that we should do duplicate checking
    return jobs

def scrape_jobsdb(data):
    jobs= []
    all_div = data.find_all('div', attrs={'class':"_3ASfTyv _2EUSthc"}) 
    for i in all_div:
        job=[]
        job.append(i.find('div', attrs={'class':"_3gfm7U9 _3ho-Knb _2swcdgn"}).a.text)
        job.append(i.find('div', attrs={'class':"_1NdWRqw _3ho-Knb _2swcdgn"}).find('span').text)
        job.append(i.find('div', attrs={'class':"_124cxoK _3ho-Knb _2swcdgn"}).find('span').text)
        job.append(i.find('span', attrs={'class':"JG37Vx2 _3Re95QG _2XGgj_O"}).find('span').text)
        job.append(i.find('div', attrs={'class':"_3gfm7U9 _3ho-Knb _2swcdgn"}).a['href'])
        jobs.append(job)
    return jobs



websites = [
    {
        "website": 'careers',
        "base_url": 'https://careers.journalists.org/jobs/?keywords=data+OR+journalist&page=',
        "starting_index": 1,        
        "step": 1,
        "function": scrape_careers
    }, 
    {
        "website": 'indeed',
        "base_url": 'https://www.indeed.hk/jobs?q=Data+Journalist+Internship&start=',
        "starting_index": 0,        
        "step": 10,
        "function": scrape_indeed 
    },
    {
        "website": 'jobsdb',
        "base_url": 'https://hk.jobsdb.com/hk/search-jobs/data-journalist/',
        "starting_index": 1,        
        "step": 1,
        "function": scrape_jobsdb
    },
]  



def scrape_all_pages(base_url,starting_index,step,function):
    global all_jobs
    all_jobs=[] 
    page_index = starting_index
    while True: 
        page_url = '{}{}'.format(base_url,page_index)
        try:
            r = requests.get(page_url)
            data = BeautifulSoup(r.text,"html.parser")
            jobs = function(data)
        except:
            jobs = []    
        if jobs == []: #if all jobs have been scraped, break the loop
            break
        all_jobs.extend(jobs)
        if len(all_jobs) > 50: #only scrape 50 jobs from each website
            break
        page_index += step  #level is in url to indiccate different pages' index
#     all_jobs.sort(key=lambda item: item[3], reverse=False) 

def store_new_jobs(website):
    try:
        with open('existedjobs-{}.csv'.format(website),'r+') as e:
            jobs_existed = [row for row in csv.reader(e)]
            e.seek(0,0) #return to the beginning
            csv.writer(e).writerows(all_jobs)
    except FileNotFoundError:
        with open('existedjobs-{}.csv'.format(website),'w') as e:
            jobs_existed = []
            csv.writer(e).writerows(all_jobs)
    with open('newjobs.csv','w') as n:
        for i in all_jobs:
            if i not in jobs_existed: #duplicate checking
                csv.writer(n).writerow(i)

for i in websites:
    scrape_all_pages(i["base_url"],i["starting_index"],i["step"],i["function"])
    store_new_jobs(i["website"])


    
import pandas
df = pandas.read_csv('newjobs.csv', header=None, names=['Title','Company','Location','Date','URL'])
df