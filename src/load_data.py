import pandas as pd
import re


def clean_columns(df):
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace(r"[()]", "", regex=True)
    )
    return df


def clean_task_name(name):
    if pd.isna(name):
        return name

    name = re.sub(r"\s*\(https://.*?\)", "", str(name))

    return name.strip()


def clean_dependency_field(dep):
    if pd.isna(dep):
        return dep

    deps = str(dep).split(",")
    cleaned = [clean_task_name(d) for d in deps if d.strip()]

    return ",".join(cleaned)


def load_data():
    # --- LOAD ---
    deployments = pd.read_csv("data/deployments.csv")
    tasks = pd.read_csv("data/tasks.csv")
    resources = pd.read_csv("data/resources.csv")
    risks = pd.read_csv("data/risks.csv")

    deployments = clean_columns(deployments)
    tasks = clean_columns(tasks)
    resources = clean_columns(resources)
    risks = clean_columns(risks)

    if "tasks" in tasks.columns:
        tasks["tasks"] = tasks["tasks"].apply(clean_task_name)

    if "dependency" in tasks.columns:
        tasks["dependency"] = tasks["dependency"].apply(clean_dependency_field)

    # --- DATE PARSING ---
    date_cols_deployments = ["start_date", "end_date_planned", "end_date_actual"]
    date_cols_tasks = ["start_date", "due_date", "actual_completion_date"]

    for col in date_cols_deployments:
        if col in deployments.columns:
            deployments[col] = pd.to_datetime(deployments[col], errors="coerce")

    for col in date_cols_tasks:
        if col in tasks.columns:
            tasks[col] = pd.to_datetime(tasks[col], errors="coerce")

    if "status" in tasks.columns:
        tasks["status"] = tasks["status"].str.strip().str.lower()

    if "status" in deployments.columns:
        deployments["status"] = deployments["status"].str.strip().str.lower()

    if "deployment" in tasks.columns:
        tasks["deployment_name"] = tasks["deployment"].apply(clean_task_name)

    return deployments, tasks, resources, risks
