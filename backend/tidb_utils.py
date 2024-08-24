import openai
import dspy
import os
from dotenv import load_dotenv

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from langchain_community.utilities import SQLDatabase
from langchain.chains import create_sql_query_chain
from langchain_openai import ChatOpenAI
from sqlalchemy import URL, or_
from typing import List
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, BigInteger, String
from sqlalchemy.dialects.mysql import LONGTEXT
from tidb_vector.sqlalchemy import VectorType

Base = declarative_base()

load_dotenv()

openai_api_key = os.environ.get("OPENAI_API_KEY")

open_ai_client = dspy.OpenAI(model="gpt-4o",
                             api_key=openai_api_key,
                             max_tokens=4096)
def get_db_url():
    return URL(
        drivername="mysql+pymysql",
        username=os.environ.get("TIDB_USERNAME"),
        password=os.environ.get("TIDB_PASSWORD"),
        host='gateway01.us-east-1.prod.aws.tidbcloud.com',
        port=4000,
        database=os.environ.get("TIDB_DB"),
        query={
            "ssl": {"cert_reqs": "CERT_NONE"}
        }
    )

dspy.settings.configure(lm=open_ai_client)
engine = create_engine(get_db_url(), pool_recycle=300)
Session = sessionmaker(bind=engine)

session = Session()


class DatabaseEntity(Base):
    __tablename__ = 'entities'

    case_id = Column(BigInteger, primary_key=True)
    decision_date = Column(String(50))
    citation = Column(String(512))
    case_name = Column(LONGTEXT)
    category = Column(String(512))
    opinion = Column(LONGTEXT)
    embedding = Column(VectorType(1536))

class DatabaseRelationship(Base):
    __tablename__ = 'relationships'

    source_case_id = Column(BigInteger, primary_key=True)
    target_case_id = Column(BigInteger, primary_key=True)
    relationship_description = Column(String(512))

def retrieve_entities_relationships(question_embedding) -> (List[DatabaseEntity], List[DatabaseRelationship]):
    session = Session()

    try:
        entity = session.query(DatabaseEntity) \
            .order_by(DatabaseEntity.embedding.cosine_distance(question_embedding)) \
            .limit(1).first()

        if not entity:
            return [], []

        entities = {entity.case_id: entity}

        relationships = session.query(DatabaseRelationship).filter(
            or_(
                DatabaseRelationship.source_case_id == entity.case_id,
                DatabaseRelationship.target_case_id == entity.case_id
            )
        ).all()

        for r in relationships:
            source_entity = session.query(DatabaseEntity).filter_by(case_id=r.source_case_id).first()
            target_entity = session.query(DatabaseEntity).filter_by(case_id=r.target_case_id).first()

            if source_entity:
                entities[source_entity.case_id] = source_entity
            if target_entity:
                entities[target_entity.case_id] = target_entity

        return list(entities.values()), relationships

    finally:
        session.close()

def get_query_embedding(query: str):
    open_ai_client = openai.OpenAI(api_key=openai_api_key)
    response = open_ai_client.embeddings.create(input=[query], model="text-embedding-3-small")
    return response.data[0].embedding

def generate_result(query: str, entities, relationships):
    open_ai_client = openai.OpenAI(api_key=openai_api_key)
    entities_prompt = '\n'.join(map(lambda e: f'(Case ID: "{e.case_id}, Citation: "{e.citation}", Decision Date:"{e.decision_date}", "Name: "{e.case_name}", Case Opinion: "{e.opinion}")', entities))
    relationships_prompt = '\n'.join(map(lambda r: f'"{r.relationship_description}"', relationships))

    response = open_ai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Please carefully think the user's " +
             "question and ONLY use the content below to generate answer, use the case details from below to generate answer, also make sure to include case id, citation in the answer:\n" +
             f"Entities: {entities_prompt}, Relationships: {relationships_prompt}"},
            {"role": "user", "content": query}
        ])

    return response.choices[0].message.content

def textToSQL(question):
    try:
        description = "Data summary for legal cases and relationships"
        data_summary_id, job_id = "313712", "15f3a1b600bd4aec8cb8c52d291edcf3"
        print(f"Data summary job created with ID: {job_id}")

        # Step 2: Wait for Data Summary Job to Complete
        summary_result = check_job_status(job_id)
        print(f"Data summary is ready with ID: {data_summary_id}")

        # Step 3: Generate SQL from Natural Language
        sql_job_id = generate_sql_query(data_summary_id, question)
        print(f"SQL generation job created with ID: {sql_job_id}")

        # Step 4: Wait for SQL Job to Complete
        sql_result = check_job_status(sql_job_id)
        sql_query = sql_result['result']['sql']
        answer = sql_result['result']['data']['rows']
        print(f"Generated SQL: {sql_query}")
        return sql_query, answer

    except Exception as e:
        print(f"An error occurred: {str(e)}")

import requests
import time
from requests.auth import HTTPBasicAuth

# API URLs
data_summary_url = "https://data.tidbcloud.com/api/v1beta/app/chat2query-KZusSqYQ/endpoint/v3/dataSummaries"
job_status_url_template = "https://us-east-1.data.tidbcloud.com/api/v1beta/app/chat2query-KZusSqYQ/endpoint/v2/jobs/{job_id}"
chat2data_url = "https://data.tidbcloud.com/api/v1beta/app/chat2query-KZusSqYQ/endpoint/v3/chat2data"

cluster_id = "10096770179376639404"
database = "legal_insights_engine"

username = "G1H8TS90"
password = "4f18541c-04e0-4cb3-bda5-a506988e0bfe"
data_summary_cache = {"data_summary_id": None}
# Step 1: Create Data Summary
def create_data_summary(description):
    if data_summary_cache["data_summary_id"] is None:
        data_summary_payload = {
            "cluster_id": cluster_id,
            "database": database,
            "description": description,
            "reuse": False,
            "default": False
        }
        response = requests.post(data_summary_url, json=data_summary_payload, auth=HTTPBasicAuth(username, password))
        response_data = response.json()
        if response_data['code'] == 200:
            data_summary_cache["data_summary_id"] = response_data['result']['data_summary_id']
            return response_data['result']['data_summary_id'], response_data['result']['job_id']
        else:
            raise Exception("Failed to create data summary")
    else:
        return data_summary_cache['data_summary_id']

# Step 2: Check Job Status
def check_job_status(job_id):
    job_status_url = job_status_url_template.format(job_id=job_id)
    while True:
        response = requests.get(job_status_url, auth=HTTPBasicAuth(username, password))
        response_data = response.json()
        if response_data['code'] == 200:
            job_result = response_data['result']
            if job_result['status'] == 'done':
                return job_result
            else:
                print(f"Job {job_id} is still running, checking again in 5 seconds...")
                time.sleep(5)
        else:
            raise Exception(f"Failed to check job status for job ID: {job_id}")

# Step 3: Generate SQL from Natural Language Query
def generate_sql_query(data_summary_id, question):
    chat2data_payload = {
        "cluster_id": cluster_id,
        "database": database,
        "data_summary_id": data_summary_id,
        "question": question,
        "sql_generate_mode": "direct"
    }
    response = requests.post(chat2data_url, json=chat2data_payload, auth=HTTPBasicAuth(username, password))
    response_data = response.json()
    if response_data['code'] == 200:
        return response_data['result']['job_id']
    else:
        raise Exception("Failed to generate SQL query from natural language")

# Example usage of the functions
