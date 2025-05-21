from bs4 import BeautifulSoup
from datetime import datetime
import requests
import time

now = datetime.now()
timestamp = now.strftime('%Y-%m-%d_%H-%M-%S')

def scraper():
    print('inside function')
    url = 'https://m.timesjobs.com/mobile/jobs-search-result.html?txtKeywords=python&cboWorkExp1=-1&txtLocation='
    html_text = requests.get(url).text
    soup = BeautifulSoup(html_text, 'lxml')
    jobs = soup.find_all('div', class_ = "srp-job-bx")

    for index, job in enumerate(jobs):
        print('inside loop')
        posting_date = job.div.find('div', class_ = 'srp-job-heading').h4.find('span', class_ = 'posting-time').text
        if '1 days ago' in posting_date or '2 days ago' in posting_date or f'{int}h':
            print('inside if')
            company_name = job.div.find('div', class_ = 'srp-job-heading').h4.find('span', class_ = 'srp-comp-name').text
            job_details = job.div.find('div', class_ = 'srp-job-heading').h3.a
            job_title = job_details.text
            job_link = job_details['href']

            with open(f'posts/{index}_{timestamp}.txt', 'w') as file:
                print('inside file')
                file.write(f'{company_name} posted {job_title} job {posting_date} \n')
                file.write(f'Click the link to access the job : {job_link} \n')

if __name__ == '__main__':
    from datetime import datetime
    while True:
        scraper()
        exit
        # time_wait = 10
        # print(f'Waiting {time_wait} minutes...')
        # time.sleep(time_wait * 60)
