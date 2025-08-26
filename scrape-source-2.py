import requests
from bs4 import BeautifulSoup
import pandas as pd

def get_job_listings(base_url):
    page = 0
    jobs = []

    while True:
        if page==10:
            break
        url = f"{base_url}&page={page}"
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Failed to retrieve page {page}")
            break

        soup = BeautifulSoup(response.text, "html.parser")
        job_listings = soup.find_all("article", class_="rw-river-article")

        if not job_listings:
            break

        for job in job_listings:
            title_tag = job.find("h3", class_="rw-river-article__title")
            title = title_tag.get_text(strip=True) if title_tag else "Unknown Title"
            link_tag = title_tag.find("a") if title_tag else None
            link = link_tag["href"] if link_tag else "#"
            full_link = f"https://reliefweb.int{link}" if link.startswith("/") else link

            closing_date_tag = job.find("dd", class_="rw-entity-meta__tag-value rw-entity-meta__tag-value--closing-date rw-entity-meta__tag-value--date rw-entity-meta__tag-value--last")
            closing_date = closing_date_tag.find("time")["datetime"] if closing_date_tag and closing_date_tag.find("time") else "Not specified"

            jobs.append({"title": title, "link": full_link, "closing_date": closing_date})

        print(f"Scraped page {page} with {len(job_listings)} jobs.")
        page += 1

    return jobs

def get_job_details(job_url):
    response = requests.get(job_url)
    if response.status_code != 200:
        print(f"Failed to fetch job details from {job_url}")
        return None, None

    soup = BeautifulSoup(response.text, "html.parser")
    content_div = soup.find("div", class_="rw-article__content")
    source_tag = soup.find("dd", class_="rw-entity-meta__tag-value")
    source = source_tag.get_text(strip=True) if source_tag else "Unknown Source"

    if not content_div:
        print(f"No content found for {job_url}")
        return source, None

    paragraphs = [p.get_text(strip=True) for p in content_div.find_all("p")]
    return source, "\n".join(paragraphs)

def get_consultancies(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    consultancies = []
    for parent_div in soup.find_all('div', class_='col-sm-12'):
        title_div = parent_div.find('div', class_='field field-name-title-field field-type-text field-label-hidden')
        title_tag = title_div.find(['span', 'a']) if title_div else None
        title = title_tag.text.strip() if title_tag else 'N/A'
        link_tag = title_div.find('a', href=True) if title_div else None
        link = link_tag['href'] if link_tag else None
        
        deadline_div = parent_div.find('div', class_='field field-name-field-application-deadline field-type-datetime field-label-inline clearfix')
        deadline = ' '.join(tag.text.strip() for tag in deadline_div.find_all(['span', 'a'])) if deadline_div else 'N/A'
        
        org_div = parent_div.find('div', class_='field field-name-og-group-ref field-type-entityreference field-label-hidden')
        organization = ' '.join(tag.text.strip() for tag in org_div.find_all(['span', 'a'])) if org_div else 'N/A'
        
        description = get_description(link) if link else 'N/A'
        
        consultancies.append({
            'Job Title': title,
            'Organisation': organization,
            'Description': description,
            'Submission Deadline': deadline,
            'Source': "Daleel Madani",
            'Link': 'https://daleel-madani.org/'+ link
        })
    
    return consultancies

def get_description(link):
    if not link.startswith('http'):
        link = 'https://daleel-madani.org' + link
    
    response = requests.get(link)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    desc_divs = soup.find_all('div', class_='col-md-9')
    for div in desc_divs:
        if div.get('class') == ['col-md-9']:
            return ' '.join(div.stripped_strings)
    
    return 'No description found'
    
base_url = "https://reliefweb.int/jobs?advanced-search=%28TY264%29&search=research"
jobs = get_job_listings(base_url)

data = []
for i in range(len(jobs)):
    try:
        job = jobs[i]
        source, job_details = get_job_details(job['link'])
        data.append({
            "Job Title": job['title'],
            "Organisation": source,
            "Description": job_details,
            "Submission Deadline": job['closing_date'],
            "Source": 'ReliefWeb',
            "Link": job['link'],
        })
    except ValueError as e:
        print(f"Skipping last job due to error: {e}")
        break

df = pd.DataFrame(data)
df.to_csv("test4.csv")
