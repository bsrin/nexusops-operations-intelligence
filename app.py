import streamlit as st

from src.load_data import load_data
from src.metrics import (
    compute_task_metrics,
    compute_deployment_metrics,
    compute_health_score
)
from src.graph import (
    build_task_graph,
    propagate_delays,
    get_top_bottlenecks,
    compute_critical_path
)
from src.insights import generate_insights, generate_recommendations


st.set_page_config(page_title="NexusOps", layout="wide")

st.title("🚀 NexusOps")
st.caption("Operations Intelligence Dashboard")


deployments, tasks, resources, risks = load_data()

tasks = compute_task_metrics(tasks)
deployment_metrics = compute_deployment_metrics(tasks)
deployment_metrics = compute_health_score(deployment_metrics)

G = build_task_graph(tasks)
impact = propagate_delays(G)
top_bottlenecks = get_top_bottlenecks(impact, top_n=5)

critical_path, critical_length = compute_critical_path(G)

insights = generate_insights(deployment_metrics, top_bottlenecks, critical_path)
recommendations = generate_recommendations(top_bottlenecks, deployment_metrics)


st.subheader("📌 System Overview")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Deployments", len(deployment_metrics))
c2.metric("Avg Health", round(deployment_metrics["health_score"].mean(), 1))
c3.metric("Tasks", len(tasks))
c4.metric("Delayed", int(tasks["is_delayed"].sum()))


st.subheader("🎛️ Deployment Focus")

selected = st.selectbox(
    "Select Deployment",
    ["All"] + list(deployment_metrics["deployment_name"])
)

if selected != "All":
    filtered = deployment_metrics[
        deployment_metrics["deployment_name"] == selected
    ]
else:
    filtered = deployment_metrics


st.subheader("📊 Deployments")


def health_status(score):
    if score < 70:
        return "🔴 Critical"
    elif score < 85:
        return "🟠 Warning"
    else:
        return "🟢 Healthy"


for _, row in filtered.iterrows():
    with st.container():
        col1, col2 = st.columns([5, 1])

        with col1:
            st.markdown(f"### {row['deployment_name']}")
            st.caption(
                f"Delay: {row['delay_percent']*100:.0f}% | "
                f"Tasks: {row['completed_tasks']}/{row['total_tasks']} | "
                f"Avg Delay: {row['avg_delay']:.1f} days"
            )

        with col2:
            st.metric("Health", int(row["health_score"]))

        st.progress(row["health_score"] / 100)


col1, col2 = st.columns(2)

with col1:
    st.subheader("⛔ Bottlenecks")

    for task, score in top_bottlenecks:
        st.warning(f"{task} → Impact: {score}")


with col2:
    st.subheader("📍 Critical Path")

    if critical_path:
        st.success(" → ".join(critical_path))
        st.write(f"Total Impact: {critical_length}")
    else:
        st.write("No critical path detected")


col1, col2 = st.columns(2)

with col1:
    st.subheader("💡 Insights")
    for i in insights:
        st.info(i)

with col2:
    st.subheader("👉 Recommendations")
    for r in recommendations:
        st.success(r)
