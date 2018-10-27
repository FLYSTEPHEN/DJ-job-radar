# Only operate when the newjoblist need to be resetted
# import csv
# with open('newjoblist.csv','w',newline='') as g:
#     writer = csv.writer(g)
#     header = ['Title','Company','Location','Date','URL']
#     writer.writerow(header)

import requests
from bs4 import BeautifulSoup
import csv

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

def scrape_all_pages(base_url,starting_index,step,function):
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
        if len(all_jobs) > 100: #only scrape 50 jobs from each website
            break
        page_index += step  #level is in url to indiccate different pages' index

def output_new_jobs(website):
#     with open('existedjobs-{}.csv'.format(website),'r') as f:
#         myreader = csv.reader(f)
#         url_existed = [row[4] for row in myreader] #read a row

#     with open('newjobs.csv','a') as g:
#         mywriter = csv.writer(g)
#         for i in all_jobs:
#             if i[4] not in url_existed: #duplicate checking
#                 mywriter.writerow(i)
            
    with open('existedjobs-{}.csv'.format(website),'w') as h:
        mywriter=csv.writer(h)
        header=['Title','Company','Location','Date','URL']
        mywriter.writerow(header) 
        mywriter.writerows(all_jobs)


websites = [
    {
        "website": 'indeed',
        "base_url": 'https://www.indeed.com/jobs?q=Data+Journalist+Internship&start=',
        "starting_index": 0,        
        "step": 10,
        "function": scrape_indeed 
    },
    {
        "website": 'careers',
        "base_url": 'https://careers.journalists.org/jobs/?keywords=data+OR+journalist+OR+internship&page=',
        "starting_index": 1,        
        "step": 1,
        "function": scrape_careers
    }, 
    {
        "website": 'jobsdb',
        "base_url": 'https://hk.jobsdb.com/hk/search-jobs/data-journalist/',
        "starting_index": 1,        
        "step": 1,
        "function": scrape_jobsdb
    },
]  

for i in websites:
    all_jobs=[] 
    scrape_all_pages(i["base_url"],i["starting_index"],i["step"],i["function"])
    output_new_jobs(i["website"])

# import pandas
# df=pandas.read_csv('newjoblist.csv')
# df[['Title','Company','Location','Date']]