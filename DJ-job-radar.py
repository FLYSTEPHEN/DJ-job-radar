import requests
from bs4 import BeautifulSoup
import pandas as pd
from numpy import nan
from dateutil.parser import parse
from datetime import timedelta
from datetime import datetime

def normalise_time(time_str):
    now = parse(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    if time_str.lower().find('30+ days ago') != -1:
        post_date = 'an unknown date more than 30 days ago'
    elif time_str.lower().find('yesterday') != -1:
        post_date = str(now - timedelta(days=1))
    elif time_str.lower().find('year') != -1:
        post_date = str(now - timedelta(days=int(time_str.split()[0]) * 365))
    elif time_str.lower().find('month') != -1:
        post_date = str(now - timedelta(days=int(time_str.split()[0]) * 30))
    elif time_str.lower().find('week') != -1:
        post_date = str(now - timedelta(weeks=int(time_str.split()[0])))
    elif time_str.lower().lower().find('day') != -1:
        post_date = str(now - timedelta(days=int(time_str.split()[0])))
    elif time_str.lower().find('hour') != -1:
        post_date = str(now - timedelta(hours=int(time_str.split()[0])))
    elif time_str.lower().find('minute') != -1:
        post_date = str(now - timedelta(minutes=int(time_str.split()[0])))
    elif time_str.lower().find('second') != -1:
        post_date = str(now - timedelta(seconds=int(time_str.split()[0])))
    else:
        try:
            post_date = str(parse(time_str))
        except: 
            post_date = 'an unrecognisable date'
    return post_date

def scrape_careers_information(page_url):
    r = requests.get(page_url)
    data = BeautifulSoup(r.text,"html.parser")
    jobs= []
    all_div = data.find_all('div', attrs={'class':"bti-ui-job-detail-container"}) 
    for i in all_div:
        job = {}
        job['Title'] = i.find('a').text
        job['Company'] = i.find('div', attrs={'class':"bti-ui-job-result-detail-employer"}).text.strip()
        job['Location'] = i.find('div', attrs={'class':"bti-ui-job-result-detail-location"}).text.strip()
        job['Post_Date'] = normalise_time(i.find('div', attrs={'class':"bti-ui-job-result-detail-age"}).text.strip())
        job['URL'] = 'https://careers.journalists.org{}'.format(i.find('a')['href'])
        job['Current Status'] = nan
        job['Source'] = 'careers'
        job['Description'] = nan
        jobs.append(job)
    return jobs, len(all_div)

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
        #use back to the higher label
        job['Location'] = i.parent.find('span', attrs={'class':"location"}).text.strip()
        job['Post_Date'] = normalise_time(i.parent.find('span', attrs={'class':"date"}).text.strip())
        job['URL'] = 'https://www.indeed.com/viewjob?jk={}'.format(i['id'][3:])
        job['Current Status'] = nan
        job['Source'] = 'indeed'
        job['Description'] = nan
        jobs.append(job)
        #when the index url exceeds the range of pages in indeed, the page will become circulation, so that we should do duplicate checking
    return jobs, len(all_h2)

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
        job['Post_Date'] = normalise_time(i.find('span', attrs={'class':"JG37Vx2 _3Re95QG _2XGgj_O"}).find('span').text)
        job['URL'] = i.find('div', attrs={'class':"_3gfm7U9 _3ho-Knb _2swcdgn"}).a['href']
        job['Current Status'] = nan
        job['Source'] = 'jobsdb'
        job['Description'] = nan
        jobs.append(job)
    return jobs, len(all_div)
    
def scrape_jobsdb_description(description_url):
    r = requests.get(description_url)
    data = BeautifulSoup(r.text,"html.parser")
    return data.find('div', attrs={'class':"jobad-primary"}).text

def scrape_all_information(base_url,starting_index,step,function_scrape_information):
    global all_jobs
    all_jobs = []
    page_index = starting_index
    experienced_loops = 0
    while True: 
        page_url = '{}{}'.format(base_url,page_index)
        try:
            info = function_scrape_information(page_url)
            jobs, len_page_jobs = info[0], info[1]
        except:
            jobs, len_page_jobs = [], 1
        all_jobs.extend(jobs)
        page_index += step  #level is in url to indiccate different pages' index
        experienced_loops += 1
        if len_page_jobs == 0 or len(all_jobs) > 999 or experienced_loops > 99:
            break
        #if all jobs have been scraped, or jobs is enough, or there have been too many steps, break the loop

def scrape_all_description(titles_urls_sources):
    list_descriptions = []
    list_websites = [m["source"] for m in websites]
    list_functions = [i["function_scrape_description"] for i in websites]
    for u, s in urls_and_sources:
        list_descriptions.append(list_functions[list_websites.index(s)](u))
    return list_descriptions

websites = [
    {
        "source": 'careers',
        "base_url": 'https://careers.journalists.org/jobs/?keywords=journalist&page=',
        "starting_index": 1,        
        "step": 1,
        "function_scrape_information": scrape_careers_information,
        "function_scrape_description": scrape_careers_description,
    }, 
    {
        "source": 'indeed',
        "base_url": 'https://www.indeed.com/jobs?q=journalist&start=',
        "starting_index": 0,        
        "step": 10,
        "function_scrape_information": scrape_indeed_information,
        "function_scrape_description": scrape_indeed_description,
    },
    {
        "source": 'jobsdb',
        "base_url": 'https://hk.jobsdb.com/hk/search-jobs/journalist/',
        "starting_index": 1,        
        "step": 1,
        "function_scrape_information": scrape_jobsdb_information,
        "function_scrape_description": scrape_jobsdb_description,
    },
]  


header = ['Title','Company','Location','Post_Date','URL','Current Status','Source','Description']
df = pd.DataFrame(columns = header)

for i in websites:
    scrape_all_information(i["base_url"],i["starting_index"],i["step"],i["function_scrape_information"])
    try:
        df = df.append(all_jobs,ignore_index=True)
    except IndexError:
        pass
df = df.drop_duplicates(['URL']) #drop dupilictes according to URL
urls_and_sources = zip(df['URL'].tolist(), df['Source'].tolist())
df['Description'] = scrape_all_description(urls_and_sources)
df.to_csv('jobs.csv',na_rep='NaN',index=False)

from string import punctuation
punctuation += '\"“”‘’—-–'

def kill_punctuations_capitals(string): 
    string = string.replace("’s","") 
    translator = str.maketrans("","",punctuation) 
    return string.lower().translate(translator)

def check_real(string, real_check_list):
    j = 0
    for i in real_check_list:
        j += kill_punctuations_capitals(string).find(i)
    return j > -len(real_check_list)

def check_new(date, new_check_point):
    try:
        return parse(date) > new_check_point
    except ValueError:
        return False

df=pd.read_csv("jobs.csv")

real_check_list = ['journalist','reporter','editor','news','data']
new_check_point = datetime.now() - timedelta(weeks=2)
real_flag = []
new_flag = []
for i in range(df.iloc[:,0].size):
    real_flag.append(check_real(df['Title'][i], real_check_list))
    new_flag.append(check_new(df['Post_Date'][i], new_check_point))
df['Real']=real_flag
df['New']=new_flag

df = df[(df['Real']==True) & (df['New']==True)].sort_values(by='Post_Date',ascending=False).loc[:,'Title':'Description']
df.to_csv('new-selected-jobs.csv',na_rep='NaN',index=False)