# Devlog
## ver20181115
**time parsing & double check**
- formatting all post time with dateutil.parser.parse and datetime
- check post time and title. Now only jobs posted within 2 weeks from now related to journalism will be recorded.
- some part of the codes become more elegant!
## ver20181112
**A brand new concise version after 2 weeks shelved!**
- use DataFrame to replace csv
- add description of each job
- add np.nan to replace blank
## Thinking:
- [x] I use two different series of source to scrape the description and the other information respectively - the job’s own page for description and the index page for the other information. Since when scraping the description, we must go deep into the page of each jobs, the wall time will be much longer than only scraping from the index page of jobs, I think it will be more stable and efficient if we scrape them in different way. Do I understand it correctly?
- [x] I want to stay in pandas so we don’t need to read and write csv over and over again. Is the pandas library is a more efficient and flexible one than csv library? 
