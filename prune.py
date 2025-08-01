import pandas as pd
from collections import defaultdict, deque

def build_graph(df):
    graph = defaultdict(set)
    for _, row in df.iterrows():
        tech = row['Skill']
        for dep in [row['Dependency 1'], row['Dependency 2'], row['Dependency 3'], row['Dependency 4']]:
            if pd.notna(dep) and dep:
                graph[tech].add(dep)
    return graph

def get_transitive_closure(graph, node):
    visited = set()
    queue = deque(graph[node])
    while queue:
        curr = queue.popleft()
        if curr not in visited:
            visited.add(curr)
            queue.extend(graph[curr])
    return visited

def remove_transitive_dependencies(df):
    graph = build_graph(df)
    cleaned_rows = []

    for _, row in df.iterrows():
        tech = row['Skill']
        direct_deps = [d for d in [row['Dependency 1'], row['Dependency 2'], row['Dependency 3'], row['Dependency 4']] if pd.notna(d) and d]
        indirect_deps = set()

        for dep in direct_deps:
            indirect_deps.update(get_transitive_closure(graph, dep))

        # Remove any direct dependencies that are also reachable transitively
        filtered_deps = [dep for dep in direct_deps if dep not in indirect_deps]
        filtered_deps += [""] * (4 - len(filtered_deps))  # pad to 4 dependencies

        cleaned_rows.append({
            "Skill": tech,
            "Category": row["Category"],
            "Dependency 1": filtered_deps[0],
            "Dependency 2": filtered_deps[1],
            "Dependency 3": filtered_deps[2],
            "Dependency 4": filtered_deps[3],
        })

    return pd.DataFrame(cleaned_rows)

file = "badminton_skill_dag.csv"

df = pd.read_csv(file)
clean_df = remove_transitive_dependencies(df)

clean_df.to_csv(file, index=False)
print("Saved:", file)
