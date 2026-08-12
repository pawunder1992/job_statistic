import asyncio
import csv
from datetime import datetime

import aiohttp
from parsel import Selector
from config import PYTHON_URL, BASE_URL, HEADERS


data = []



async def get_selector(url: str) -> Selector | None:
    async with aiohttp.ClientSession(headers=HEADERS) as session:
        try:
            await asyncio.sleep(1)
            async with session.get(url) as response:
                if response.status != 200:
                    print(f"Server error: {response.status}")
                    return None
                html_content = await response.text()
                return Selector(text=html_content)
        except Exception as e:
            print(f"Error: {e}")
            return None


async def fetch_jobs(url=PYTHON_URL):
    selector = await get_selector(url)
    job_links = selector.css("h2.my-0 a::attr(href)").getall()
    job_tasks = [fetch_single_job(BASE_URL + link) for link in job_links]
    if job_tasks:
        page_results = await asyncio.gather(*job_tasks)
        data.extend(page_results)
    active_page_number = selector.css("ul.pagination li.active span::text").get()
    if active_page_number:
        await fetch_jobs(PYTHON_URL + f"?page={int(active_page_number) + 1}")
    return data


async def fetch_single_job(url):
    selector = await get_selector(url)

    skills_elements = selector.css("div.sm\\:mt-xl.flex-wrap ul li ::text")
    skills_list = skills_elements.getall()
    skills = ", ".join([skill.strip() for skill in skills_list if skill.strip() and skill.isascii()])


    title = selector.css("h1.my-0#h1-name ::text").get().strip()

    company_name = selector.css("a.inline span.strong-500::text").get()

    ex_element = selector.xpath('//li[span[@title="Умови й вимоги"]]')
    try:
        experience = "".join(ex_element.css("*::text").getall()).split(" від ")[1][0]
    except IndexError:
        experience = 0

    job_item = {
        "title": title,
        "company_name": company_name,
        "experience": int(experience),
        "skills": "".join(skills)
    }
    return job_item


async def main():
    all_jobs = await fetch_jobs()
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    base_fields = ['title', 'company_name', 'experience', 'skills']
    with open(f"csv/{now}-statistic.csv", "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=base_fields, restval=0)
        writer.writeheader()
        for job in all_jobs:
            writer.writerow(job)



if __name__ == "__main__":
    asyncio.run(main())
