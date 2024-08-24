import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config
import requests

st.header("What Can You Discover About This Case and Its Legal Web?")

base_url = "http://localhost:8000"

case_id = st.number_input("Enter the Case ID:", min_value=1, step=1)


if st.button("Get Case Details"):
    response = requests.get(f"{base_url}/case_details/{case_id}")
    if response.status_code == 200:
        data = response.json()

        case_details = data["case_details"]
        related_cases = data["related_cases"]

        nodes = []
        edges = []

        category_nodes = {}

        main_case_node = Node(id=f"case_{case_id}", label=f"Case {case_details['case_id']}", size=30, color="blue")
        nodes.append(main_case_node)

        category = case_details["category"]
        if category not in category_nodes:
            category_node = Node(id=f"category_{category}", label=f"Category: {category}", size=20, color="orange")
            nodes.append(category_node)
            category_nodes[category] = category_node.id
        else:
            category_node = Node(id=category_nodes[category], label=f"Category: {category}", size=20, color="orange")

        edges.append(Edge(source=f"case_{case_id}", target=category_node.id))
        edges.append(Edge(source=f"case_{case_id}", target=f"court_{case_id}"))

        for related_case in related_cases:
            related_case_id = related_case["case_id"]
            related_case_node = Node(id=f"case_{related_case_id}", label=f"Case {related_case_id}", size=20)
            nodes.append(related_case_node)

            edges.append(Edge(source=f"case_{case_id}", target=f"case_{related_case_id}"))

            related_category = related_case["category"]
            if related_category not in category_nodes:
                related_category_node = Node(id=f"category_{related_category}", label=f"Category: {related_category}",
                                             size=15, color="orange")
                nodes.append(related_category_node)
                category_nodes[related_category] = related_category_node.id
            else:
                related_category_node = Node(id=category_nodes[related_category], label=f"Category: {related_category}",
                                             size=15, color="orange")

            edges.append(Edge(source=f"case_{related_case_id}", target=related_category_node.id))
        config = Config(width=800, height=600, directed=True, nodeHighlightBehavior=False, highlightColor="#F7A7A6",
                        collapsible=True)
        agraph(nodes=nodes, edges=edges, config=config)

        st.subheader("Case Details")
        st.write(f"**:blue[Case ID]**: {case_details['case_id']}")
        st.write(f"**:blue[Opinion]**: {case_details['opinion']}")
        st.write(f"**:blue[Category]**: {case_details['category']}")
        st.write(f"**:blue[Decision Date]**: {case_details['decision_date']}")
    else:
        st.error("Failed to fetch case details")



