from fastapi import FastAPI, HTTPException
from typing import Dict, Any
from .tidb_utils import *
from sqlalchemy import text

load_dotenv()
openai_api_key = os.environ.get("OPENAI_API_KEY")

app = FastAPI()

def row_to_dict(row, result):
    return {col: row[idx] for idx, col in enumerate(result.keys())}

@app.get("/case_details/{case_id}")
def get_case_details(case_id: int):
    try:
        with engine.connect() as connection:
            case_query = text("SELECT * FROM entities WHERE case_id = :case_id")
            case_details = connection.execute(case_query, {"case_id": case_id}).fetchone()
            if case_details is None:
                raise HTTPException(status_code=404, detail="Case not found")
            case_details_dict = dict(case_details._mapping)
            rel_query = text("""
                SELECT e.*, r.relationship_description FROM `entities` AS e JOIN `relationships` AS r ON e.`case_id` = r.`target_case_id` WHERE r.`source_case_id` = :case_id
            """)
            relationships = connection.execute(rel_query, {"case_id": case_id}).fetchall()

            related_cases = [dict(relationship._mapping) for relationship in relationships]


        return {"case_details": case_details_dict, "related_cases": related_cases}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/entities")
def get_entities():
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT * FROM entities"))
            entities = [row_to_dict(row, result) for row in result]
        return entities
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/relationships")
def get_relationships():
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT * FROM relationships"))
            relationships = [row_to_dict(row, result) for row in result]
        return relationships
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))



@app.post("/graph_query")
def query_chain(query_params: Dict[str, Any]):
    question = query_params.get("question")
    if not question:
        return {"error": "Question parameter is required"}

    try:
        query, answer = textToSQL(question)
        return {"query": query, 'answer': answer}
    except Exception as e:
        return {"error": str(e)}


@app.post("/semantic_query")
def query_index(query_params: Dict[str, Any]):
    question = query_params.get("question")
    if not question:
        return {"error": "Question parameter is required"}

    try:
        question_embedding = get_query_embedding(question)
        entities, relationships = retrieve_entities_relationships(question_embedding)
        result = generate_result(question, entities, relationships)
        return {"answer": result}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
