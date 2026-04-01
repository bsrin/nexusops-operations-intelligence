import pandas as pd

def compute_task_metrics(tasks):
    tasks["delay_days"] = (
        tasks["actual_completion_date"] - tasks["due_date"]
    ).dt.days

    today = pd.Timestamp.today()

    tasks.loc[tasks["actual_completion_date"].isna(), "delay_days"] = (
        today - tasks["due_date"]
    ).dt.days

    tasks["delay_days"] = tasks["delay_days"].clip(lower=0)

    tasks["is_delayed"] = tasks["delay_days"] > 0

    return tasks

def compute_deployment_metrics(tasks):
    deployment_metrics = tasks.groupby("deployment_name").agg(
        total_tasks=("tasks", "count"),
        completed_tasks=("status", lambda x: (x == "completed").sum()),
        delayed_tasks=("is_delayed", "sum"),
        avg_delay=("delay_days", "mean")
    ).reset_index()

    deployment_metrics["delay_percent"] = (
        deployment_metrics["delayed_tasks"] /
        deployment_metrics["total_tasks"]
    )

    return deployment_metrics

def compute_health_score(df):
    df["health_score"] = (
            100
            - (df["delay_percent"] * 50)
            - (df["avg_delay"].fillna(0) * 2)
    )

    df.loc[df["completed_tasks"] == 0, "health_score"] -= 20

    df["health_score"] = df["health_score"].clip(0, 100)

    return df
