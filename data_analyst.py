import pandas as pd
import matplotlib.pyplot as plt



def get_plot(csv: str, now: str) -> None:
    data = pd.read_csv(csv)
    set_skills = set()
    for skill in data.skills:
        if isinstance(skill, str):
            for char in skill.split(", "):
                set_skills.add(char)
    all_skills = sorted(list(set_skills))

    skills_dict = {}
    for skill in all_skills:
        skills_dict[skill] = data['skills'].apply(
            lambda x: 1 if isinstance(x, str) and skill in x.split(", ") else 0
        )

    skills_df = pd.DataFrame(skills_dict)
    data = pd.concat([data, skills_df], axis=1)

    ax = data[all_skills].sum().sort_values(ascending=False).head(20).plot.bar(rot=90)
    plt.title("Top 20")
    plt.xlabel("Technology")
    plt.ylabel("Amount")
    plt.tight_layout()

    plt.savefig(f"plots/{now}-top_skills_chart.png", dpi=300, bbox_inches='tight')
