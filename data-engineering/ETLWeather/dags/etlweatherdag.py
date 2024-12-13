from airflow import DAG
from airflow.providers.http.hooks.http import HttpHook
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.decorators import task
from airflow.utils.dates import days_ago
import requests
import json

# Latitude and Longitude of the city (London in this case)
LATITUDE = 51.5074
LONGITUDE = -0.1278
POSTGRES_CONN_ID = "postgres_default"
API_CONN_ID = "open_meteo_api"

default_args = {
    "owner": "airflow",
    "start_date": days_ago(1),
}

## DAG definition
with DAG(
    dag_id="weather_etl_pipeline",
    default_args=default_args,
    schedule_interval="@daily",
    catchup=False,
) as dag:
    
    @task
    def extract_weather_data():
        """
        Extract weather data from the OpenMeteo API
        """
        # Use HTTP Hook to connection details from Airflow connection
        http_hook = HttpHook(http_conn_id=API_CONN_ID, method="GET")
        # URL
        url = "https://api.open-meteo.com"
        # Build the API endpoint
        endpoint = f"v1/forecast?latitude={LATITUDE}&longitude={LONGITUDE}&current_weather=true"
        # Make the API request via the HTTP Hook
        response = http_hook.run(endpoint)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to extract weather data: {response.status_code} - {response.text}")
        
    @task
    def transform_weather_data(weather_data):
        """
        Transform extractedweather data
        """
        current_weather = weather_data["current_weather"]
        transformed_data = {
            "latitude": LATITUDE,
            "longitude": LONGITUDE,
            "temperature": current_weather["temperature"],
            "windspeed": current_weather["windspeed"],
            "winddirection": current_weather["winddirection"],
            "weathercode": current_weather["weathercode"],
        }
        return transformed_data
    
    @task
    def load_weather_data(transformed_data):
        """
        Load transformed weather data into the postgres database
        """
        postgres_hook = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)
        conn = postgres_hook.get_conn()
        cursor = conn.cursor()
        
        # Create table if it doesn't exist
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS weather_data (
            latitude FLOAT,
            longitude FLOAT,
            temperature FLOAT,
            windspeed FLOAT,
            winddirection FLOAT,
            weathercode INT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
        )
        # Insert the transformed data into the table
        cursor.execute(
            """
            INSERT INTO weather_data (latitude, longitude, temperature, windspeed, winddirection, weathercode)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                transformed_data["latitude"],
                transformed_data["longitude"],
                transformed_data["temperature"],
                transformed_data["windspeed"],
                transformed_data["winddirection"],
                transformed_data["weathercode"]
            )
        )
        conn.commit()
        cursor.close()

    # DAG Workflow - ETL Pipeline
    weather_data = extract_weather_data()
    transformed_data = transform_weather_data(weather_data)
    load_weather_data(transformed_data)

