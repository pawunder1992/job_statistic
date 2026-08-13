import asyncio

import csv
from datetime import datetime

from data_analyst import get_plot
from scrapper import fetch_jobs


async def main() -> None:
    all_jobs = await fetch_jobs()
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    base_fields = ['title', 'company_name', 'experience', 'skills']
    file_path = f"csv/{now}-statistic.csv"
    with open(file_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=base_fields, restval=0)
        writer.writeheader()
        for job in all_jobs:
            writer.writerow(job)
    get_plot(file_path, now)

if __name__ == "__main__":
    asyncio.run(main())