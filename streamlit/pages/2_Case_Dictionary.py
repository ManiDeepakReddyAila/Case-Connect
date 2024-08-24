import streamlit as st
import pandas as pd
import requests

definition = "a civil or criminal proceeding at law"
props = {
    'case_id': 'A unique identifier assigned to a legal case',
    'case_name': 'The title or name given to a legal case, reflecting key details or parties involved',
    'decision_date': 'The date on which a legal decision or judgment was made by a court',
    'citation': 'A reference or notation providing information about the source and location of a legal case within legal literature',
    'category': 'The classification of the case such as criminal, civil, family, etc.'
}
rels = {
    'source_case_id': 'The identifier of the case that cites another',
    'target_case_id': 'The identifier of the case being cited',
    'relationship_description': 'Describes the nature of the relationship, focusing on legal referencing or citation'
}

with st.sidebar:
    st.markdown("# **:blue[Case]**")
    st.markdown("_" + definition + "_")
    st.markdown("**Properties:**")
    for key, value in props.items():
        st.markdown("**:blue[" + key + "]** : " + value)
    st.markdown("**Relationships Details:**")
    st.write(f"**:blue[source_case_id]:** {rels['source_case_id']}")
    st.write(f"**:blue[target_case_id]:** {rels['target_case_id']}")
    st.write(f"**:blue[relationship_description]:** {rels['relationship_description']}")

BASE_URL = "http://localhost:8000/cypher_gds"

base_url = "http://localhost:8000"

entities_response = requests.get(f"{base_url}/entities")
if entities_response.status_code == 200:
    entities_data = entities_response.json()
    entities_df = pd.DataFrame(entities_data)
else:
    st.error("Failed to fetch entities data")

relationships_response = requests.get(f"{base_url}/relationships")
if relationships_response.status_code == 200:
    relationships_data = relationships_response.json()
    relationships_df = pd.DataFrame(relationships_data)
else:
    st.error("Failed to fetch relationships data")

st.header("Detailed Case Index")
if 'entities_df' in locals():
    st.dataframe(entities_df)

st.header("Legal Reference Network")
if 'relationships_df' in locals():
    st.dataframe(relationships_df)