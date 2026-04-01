from src.load_data import load_data
from src.metrics import (
    compute_task_metrics,
    compute_deployment_metrics,
    compute_health_score
)
from src.graph import (
    build_task_graph,
    propagate_delays,
    get_top_bottlenecks
)
from src.graph import compute_critical_path

from src.insights import generate_insights

from src.insights import generate_recommendations

def main():
    # --- LOAD DATA ---
    deployments, tasks, resources, risks = load_data()

    # --- METRICS ---
    tasks = compute_task_metrics(tasks)

    deployment_metrics = compute_deployment_metrics(tasks)
    deployment_metrics = compute_health_score(deployment_metrics)

    print("\n=== DEPLOYMENT METRICS ===")
    print(deployment_metrics)

    # --- GRAPH ---
    G = build_task_graph(tasks)

    impact = propagate_delays(G)

    print("\n=== TOP BOTTLENECK TASKS ===")
    top_bottlenecks = get_top_bottlenecks(impact, top_n=5)

    for task, score in top_bottlenecks:
        print(f"{task} → Impact Score: {score}")
    # --- CRITICAL PATH ---
    path, length = compute_critical_path(G)

    print("\n=== CRITICAL PATH ===")
    print(" → ".join(path))
    print(f"Total Delay Impact: {length}")

    # --- INSIGHTS ---
    insights = generate_insights(deployment_metrics, top_bottlenecks, path)

    print("\n=== INSIGHTS ===")
    for i in insights:
        print(i)

    # --- RECOMMENDATIONS ---
    recommendations = generate_recommendations(top_bottlenecks, deployment_metrics)

    print("\n=== RECOMMENDATIONS ===")
    for r in recommendations:
        print(r)
if __name__ == "__main__":
    main()