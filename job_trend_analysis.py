print("Script started")

import pandas as pd
import numpy as np

print("About to read CSV")

# ---------- 1. Load data ----------
df = pd.read_csv("linkedin_job_postings.csv")
print("CSV loaded")

# Keep and rename needed columns
df = df[[
    "job_title",
    "company",
    "job_location",
    "first_seen",
    "job_type"
]]
print("Columns selected")

df = df.rename(columns={
    "company": "company_name",
    "job_location": "location",
    "first_seen": "posted_at"
})
print("Columns renamed")

# Add empty columns for fields not in this file but used later
df["job_description"] = ""
df["skills"] = ""
df["salary_range"] = ""

# ---------- 2. Basic cleaning ----------
df = df.drop_duplicates()
df = df.dropna(subset=["job_title", "location"])

for col in ["job_title", "company_name", "location", "job_type"]:
    df[col] = df[col].astype(str).str.strip()

# ---------- 3. Date handling ----------
df["posted_at"] = pd.to_datetime(df["posted_at"], errors="coerce")
df = df.dropna(subset=["posted_at"])

df["year"] = df["posted_at"].dt.year
df["month"] = df["posted_at"].dt.month
df["year_month"] = df["posted_at"].dt.to_period("M").astype(str)

# Filter only 2024 data (or remove this line if you want all years)
df_2024 = df[df["year"] == 2024].copy()

# ---------- 4. Salary cleaning ----------
def parse_salary_range(s):
    return np.nan, np.nan  # no salary in this file, keep as NaN

df_2024[["salary_min", "salary_max"]] = df_2024["salary_range"].apply(
    lambda x: pd.Series(parse_salary_range(x))
)
df_2024["salary_avg"] = df_2024[["salary_min", "salary_max"]].mean(axis=1)

# ---------- 5. Aggregations for trends ----------

# 5.1 Jobs by role
jobs_by_role = (
    df_2024.groupby("job_title")
    .size()
    .reset_index(name="job_count")
    .sort_values("job_count", ascending=False)
)

# 5.2 Jobs by location
jobs_by_location = (
    df_2024.groupby("location")
    .size()
    .reset_index(name="job_count")
    .sort_values("job_count", ascending=False)
)

# 5.3 Jobs over time (month-wise)
jobs_over_time = (
    df_2024.groupby("year_month")
    .size()
    .reset_index(name="job_count")
    .sort_values("year_month")
)

# 5.4 Salary by role (will be empty / NaN because salary not present)
salary_by_role = (
    df_2024.dropna(subset=["salary_avg"])
    .groupby("job_title")["salary_avg"]
    .mean()
    .reset_index()
    .sort_values("salary_avg", ascending=False)
)

# 5.5 Skills analysis (no skills in this file, so this will be empty)
skills_df = df_2024.dropna(subset=["skills"]).copy()
skills_df["skills"] = skills_df["skills"].astype(str)

skills_exploded = skills_df.assign(
    skill=skills_df["skills"].str.split(",")
).explode("skill")

skills_exploded["skill"] = skills_exploded["skill"].str.strip().str.title()
skills_exploded = skills_exploded[skills_exploded["skill"] != ""]

skills_overall = (
    skills_exploded.groupby("skill")
    .size()
    .reset_index(name="demand_count")
    .sort_values("demand_count", ascending=False)
)

skills_by_role = (
    skills_exploded.groupby(["job_title", "skill"])
    .size()
    .reset_index(name="count")
)

# ---------- 6. Export CSVs for Power BI ----------
df_2024.to_csv("clean_jobs_2024.csv", index=False)
jobs_by_role.to_csv("jobs_by_role.csv", index=False)
jobs_by_location.to_csv("jobs_by_location.csv", index=False)
jobs_over_time.to_csv("jobs_over_time.csv", index=False)
salary_by_role.to_csv("salary_by_role.csv", index=False)
skills_overall.to_csv("skills_overall.csv", index=False)
skills_by_role.to_csv("skills_by_role.csv", index=False)

print("Export complete.")
