import pandas as pd

data = pd.read_csv("csv/2026-08-12_20-31-54-statistic.csv")

# 1. Збираємо унікальні скіли (ваш код)
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
data.to_csv("test.csv", index=False)

print(data["Python"].sum())