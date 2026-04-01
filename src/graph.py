import pandas as pd
import networkx as nx


def build_task_graph(tasks: pd.DataFrame) -> nx.DiGraph:
    """
    Build directed graph:
    dependency → task
    """
    G = nx.DiGraph()

    for _, row in tasks.iterrows():
        task = row.get("tasks")

        if pd.isna(task):
            continue

        task = str(task).strip()

        # Safe delay handling
        delay = row.get("delay_days", 0)
        if pd.isna(delay):
            delay = 0

        G.add_node(task, delay=delay)

        # Dependencies
        dep_field = row.get("dependency")

        if pd.notna(dep_field):
            dependencies = str(dep_field).split(",")

            for dep in dependencies:
                dep = dep.strip()

                if dep:
                    G.add_node(dep)  
                    G.add_edge(dep, task)

    return G


def propagate_delays(G: nx.DiGraph) -> dict:
    """
    Compute downstream delay impact for each task
    """
    impact = {}

    for node in G.nodes:
        descendants = nx.descendants(G, node)

        total_delay = 0
        for d in descendants:
            delay = G.nodes[d].get("delay", 0)
            if pd.isna(delay):
                delay = 0
            total_delay += delay

        impact[node] = total_delay

    return impact


def get_top_bottlenecks(impact_dict, top_n=5):
    """
    Return top N tasks by impact
    """
    sorted_tasks = sorted(
        impact_dict.items(),
        key=lambda x: x[1],
        reverse=True
    )

    return sorted_tasks[:top_n]

def compute_critical_path(G: nx.DiGraph):
    """
    Compute longest path based on delay weight
    """

    for node in G.nodes:
        delay = G.nodes[node].get("delay", 0)
        if pd.isna(delay):
            delay = 0
        G.nodes[node]["weight"] = delay

    for u, v in G.edges:
        G[u][v]["weight"] = G.nodes[v]["weight"]

    try:
        path = nx.dag_longest_path(G, weight="weight")
        length = nx.dag_longest_path_length(G, weight="weight")
    except:
        path = []
        length = 0

    return path, length
