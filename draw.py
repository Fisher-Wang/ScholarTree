import os

import networkx as nx
import plotly.graph_objects as go
from networkx.drawing.nx_agraph import graphviz_layout

from utils.common import safe_get

DATABASE_ID = os.getenv("NOTION_DATABASE_ID")


def draw(notion):
    db_rows = notion.databases.query(database_id=DATABASE_ID)

    nodes = []
    edges = []

    id2name = {
        row["id"]: safe_get(row, "properties.Name.title.0.plain_text")
        for row in db_rows["results"]
    }

    for row in db_rows["results"]:
        name = safe_get(row, "properties.Name.title.0.plain_text")
        affiliation = safe_get(row, "properties.Affiliations.rich_text.0.plain_text")
        citation = safe_get(row, "properties.Citations.number")
        nodes.append(
            {
                "name": name,
                "affiliation": affiliation,
                "citations": citation if citation else 1000,
            }
        )

    for row in db_rows["results"]:
        name = safe_get(row, "properties.Name.title.0.plain_text")
        phd_student_items = safe_get(row, "properties.PhD Students.relation")
        postdoc_items = safe_get(row, "properties.PostDoc Students.relation")
        student_items = phd_student_items + postdoc_items
        edges.extend(
            [(name, id2name[student_item["id"]]) for student_item in student_items]
        )

    G = nx.DiGraph()
    for node in nodes:
        G.add_node(
            node["name"], affiliation=node["affiliation"], citations=node["citations"]
        )
    G.add_edges_from(edges)

    # pos = graphviz_layout(G, prog="dot")
    pos = graphviz_layout(G, prog="neato")

    node_x = []
    node_y = []
    node_text = []
    node_hovertext = []
    node_sizes = []
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_text.append(node)
        node_hovertext.append(G.nodes[node].get("affiliation", None))

        citation_count = G.nodes[node].get("citations", None)
        node_size = 2 * (citation_count / 100 if citation_count else 1) ** 0.5
        node_sizes.append(node_size)

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers+text",
        text=node_text,
        hovertext=node_hovertext,
        marker=dict(showscale=False, color="skyblue", size=node_sizes, line_width=2),
    )

    edge_x = []
    edge_y = []
    edge_annotations = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
        edge_annotations.append(
            dict(
                x=x1,
                y=y1,
                ax=x0,
                ay=y0,
                xref="x",
                yref="y",
                axref="x",
                ayref="y",
                showarrow=True,
                arrowhead=2,
                arrowsize=1,
                arrowwidth=2,
                arrowcolor="#888",
            )
        )

    edge_trace = go.Scatter(
        x=edge_x,
        y=edge_y,
        line=dict(width=1, color="#888"),
        hoverinfo="none",
        mode="lines",
    )

    fig = go.Figure(
        data=[edge_trace, node_trace],
        layout=go.Layout(
            title="Scholar Network",
            titlefont_size=16,
            showlegend=False,
            hovermode="closest",
            margin=dict(b=20, l=5, r=5, t=40),
            annotations=edge_annotations,
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        ),
    )

    fig.show()
