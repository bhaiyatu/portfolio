Overview
========

This is a very simple ETL Pipeline that extracts weather data using the Open Meteo API, does a transform and pushes the transformed data into a Postgres database. This is all done using Docker and Airflow.

Project Contents
================

- dags: This folder contains the Python files for the Airflow DAGs. It contains an example DAG as well as:
    - `etlweatherdag.py`: This contains the connection ids, dag_id and tasks for the dag to extract, transform, and load the data.
- Dockerfile: This file contains a versioned Astro Runtime Docker image that provides a differentiated Airflow experience.
- docker-compose: This file contains the definition to run the postgres database in a Docker container. 
- airflow_settings.yaml: Use this local-only file to specify Airflow Connections, Variables, and Pools instead of entering them in the Airflow UI as you develop DAGs in this project. For my project I manually input them using the Airflow UI.
