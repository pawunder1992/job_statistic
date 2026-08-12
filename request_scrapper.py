import asyncio

from playwright.async_api import async_playwright
from parsel import Selector
from config import PYTHON_URL, BASE_URL

data = []





async def get_html_content(page, url):
    try:
        await page.goto(url, wait_until="domcontentloaded")
        await asyncio.sleep(2)
        return await page.content()
    except Exception as e:
        print(f"Помилка завантаження {url}: {e}")
        return None


async def fetch_single_job(page, url):
    html = await get_html_content(page, url)
    if not html:
        return None
    selector = Selector(text=html)
    skills_elements = selector.css("div.sm\\:mt-xl.flex-wrap ul li ::text")
    skills_list = skills_elements.getall()
    cleaned_skills = [skill.strip() for skill in skills_list if skill.strip()]

    title_raw = selector.css("h1.my-0#h1-name ::text").get()
    title = title_raw.strip() if title_raw else "No title"
    print(f"Знайдено: {title}")

    company_name = selector.css("a.inline span.strong-500::text").get()

    ex_element = selector.xpath('//li[span[@title="Умови й вимоги"]]')
    try:
        experience = "".join(ex_element.css("*::text").getall()).split(" від ")[1][0]
    except IndexError:
        experience = "no experience"

    return {
        "title": title,
        "company": company_name.strip() if company_name else "No company",
        "skills": cleaned_skills,
        "url": url,
        "experience": experience
    }


async def fetch_jobs(page, context, url=PYTHON_URL):
    print(f"Обробляємо сторінку: {url}")
    html = await get_html_content(page, url)
    if not html:
        return

    selector = Selector(text=html)
    job_links = selector.css("h2.my-0 a::attr(href)").getall()

    for link in job_links:
        # Використовуємо context.new_page() замість page.context.new_page()
        job_page = await context.new_page()
        job_data = await fetch_single_job(job_page, BASE_URL + link)
        await job_page.close()

        if job_data:
            data.append(job_data)

    active_page_number = selector.css("ul.pagination li.active span::text").get()
    if active_page_number is not None:
        next_page = int(active_page_number) + 1
        next_url = f"{PYTHON_URL}?page={next_page}"
        await fetch_jobs(page, context, next_url)


async def main():
    async with async_playwright() as p:
        # Підключаємося до вашого відкритому через командний рядок Chrome
        browser = await p.chromium.connect_over_cdp("http://localhost:9222")
        context = browser.contexts[0]
        page = await context.new_page()

        print("Підключено до браузера. Починаємо збір даних...")
        await fetch_jobs(page, context, PYTHON_URL)

        await page.close()

    print(f"\nЗбір завершено. Всього зібрано: {len(data)}")


if __name__ == "__main__":
    asyncio.run(main())