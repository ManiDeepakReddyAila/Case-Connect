# Case Connect

![Case Connect](https://github.com/ManiDeepakReddyAila/Case-Connect/blob/master/case_connect.jpg)

----- 

## Links

[![Application](https://img.shields.io/badge/Streamlit%20Application-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)](http://34.135.129.25:80/) [![Documentation](https://img.shields.io/badge/Documentation-4285F4?style=for-the-badge&logo=Google&logoColor=white)](https://github.com/PranithaPoosa/Legal_Insights_Engine/blob/main/assets/Legal%20Insights%20Engine_documentation.pdf)  [![Application Demo](https://img.shields.io/badge/Application_Demo-orange?style=for-the-badge&logo=YouTube&logoColor=white)](https://www.youtube.com/embed/ywKlXsZLMv4) 

## Overview
The Case Connect project is designed to streamline legal research and decision-making by leveraging advanced technologies for data processing, semantic search, and data analysis. This platform integrates multiple components to allow users to interact with comprehensive legal case data, perform in-depth analysis, and derive insights that inform decision-making.

A key component of the project is TiDB, a distributed SQL database that provides strong consistency, high availability, and horizontal scalability. TiDB is instrumental in managing and scaling the vast amounts of legal data processed by the platform. It also enhances the application’s search capabilities through TiDB Vector Search, which utilizes vector embeddings and similarity search. This enables more advanced, context-aware search functionalities, allowing users to perform deeper and more nuanced searches across the legal dataset.

The platform also incorporates OpenAI embeddings for semantic search, along with a robust frontend developed in Streamlit and a FastAPI backend, all containerized and deployed on Google Cloud Platform (GCP) for ease of deployment and scalability.

## Objectives
- Create an intuitive and scalable platform for analyzing and understanding legal case data.
- Implement TiDB to efficiently store and retrieve large volumes of legal case data, and leverage its vector search capabilities for advanced, AI-powered search functionalities.
- Leverage OpenAI's embedding capabilities to perform semantic searches and enhance data analysis, enabling more relevant and contextual insights.
- Containerize the entire application using Docker and deploy it on Google Cloud Platform (GCP), ensuring ease of deployment, scalability, and maintainability.
- Implement end-to-end automation of data processing workflows to enhance efficiency and scalability, using tools like FastAPI for the backend and Streamlit for the frontend.

## Technologies Used

![Python](https://img.shields.io/badge/python-grey?style=for-the-badge&logo=python&logoColor=ffdd54)
![](https://img.shields.io/badge/FastAPI-4285F4?style=for-the-badge&logo=fastapi&logoColor=white)
![](https://img.shields.io/badge/TiDb-red?style=for-the-badge&logo=tidb&logoColor=white)
![](https://img.shields.io/badge/GCP-blue?style=for-the-badge&logo=google-cloud&logoColor=white)
![](https://img.shields.io/badge/Apache_Airflow-green?style=for-the-badge&logo=apache-airflow&logoColor=white)
![](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![](https://img.shields.io/badge/Docker-blue?style=for-the-badge&logo=Docker&logoColor=white)

## Architecture Diagram

![Case Connect](https://github.com/ManiDeepakReddyAila/Case-Connect/blob/master/arch_diagram.png)

## Project Structure

```
  ├── backend           # FastAPI Component
  │   ├── tidbutils.py            # Utility functions for TiDb connection and querying    
  │   └── main.py                  # REST API endpoints 
  ├── streamlit           # Streamlit Component
  │   ├── pages            
  │   │    └── ... .py
  │   └── Home.py           
  ├── .gitignore   
  ├── README.md                         # ReadMe file
  └── requirements.txt                # Requirements for the project
```
