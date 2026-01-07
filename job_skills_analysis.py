import pandas as pd

print("Loading skills data...")

# 1. Load job postings (for titles) and skills
posts = pd.read_csv("linkedin_job_postings.csv", usecols=["job_link", "job_title"])
skills = pd.read_csv("job_skills.csv")

print("Posts shape:", posts.shape)
print("Skills shape:", skills.shape)

# 2. Keep only needed columns and rename
skills = skills[["job_link", "job_skills"]]
skills = skills.rename(columns={"job_skills": "skill"})

# 3. Join skills with job titles
jobs_skills = skills.merge(posts, on="job_link", how="inner")

# 4. Overall skills demand
skills_overall = (
    jobs_skills.groupby("skill")
    .size()
    .reset_index(name="demand_count")
    .sort_values("demand_count", ascending=False)
)

# 5. Skills by role
skills_by_role = (
    jobs_skills.groupby(["job_title", "skill"])
    .size()
    .reset_index(name="count")
)

# 6. Export for Power BI
skills_overall.to_csv("skills_overall.csv", index=False)
skills_by_role.to_csv("skills_by_role.csv", index=False)

print("Skills export complete.")
