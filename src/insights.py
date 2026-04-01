def generate_insights(deployment_metrics, bottlenecks, critical_path):
    insights = []

    risky = deployment_metrics[deployment_metrics["health_score"] < 70]

    for _, row in risky.iterrows():
        insights.append(
            f"🚨 Deployment '{row['deployment_name']}' is at risk (Health: {row['health_score']:.1f})"
        )

    if bottlenecks:
        top_task, impact = bottlenecks[0]
        insights.append(
            f"⛔ Task '{top_task}' is the biggest bottleneck (Impact: {impact})"
        )

    if critical_path:
        path_str = " → ".join(critical_path)
        insights.append(
            f"📍 Critical execution path: {path_str}"
        )

    return insights

def generate_recommendations(bottlenecks, deployment_metrics):
    recommendations = []

    if bottlenecks:
        task, impact = bottlenecks[0]
        recommendations.append(
            f"👉 Prioritize resolving '{task}' — it impacts {impact} downstream delay units."
        )

    risky = deployment_metrics[deployment_metrics["health_score"] < 70]

    for _, row in risky.iterrows():
        recommendations.append(
            f"👉 Immediate attention needed: '{row['deployment_name']}' (Health: {row['health_score']:.1f})"
        )

    return recommendations
