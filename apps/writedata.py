import os
import json
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import text
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env')

# Constants for SQL queries
DELETE_AMENITIES = "DELETE FROM Amenities"
DELETE_HOTEL = "DELETE FROM Hotel"
INSERT_HOTEL = """
    INSERT INTO Hotel (HotelID, Name, ChainCode, DupeId, IataCode, GeoCodeLat, GeoCodeLon, CountryCode, Distance, Unit, Rating, LastUpdate)
    VALUES (:HotelID, :Name, :ChainCode, :DupeId, :IataCode, :GeoCodeLat, :GeoCodeLon, :CountryCode, :Distance, :Unit, :Rating, :LastUpdate);
"""
INSERT_AMENITIES = "INSERT INTO Amenities (HotelID, AmenityName) VALUES (:HotelID, :AmenityName);"

def make_engine():
    # Retrieve database credentials
    host =  'db_host' # Pass the name of the variable as a string
    username = 'username'
    password = 'password'
    database = 'db_name'

    # Check for missing credentials
    if not all([host, username, password, database]):
        raise ValueError("Database credentials are missing in environment variables.")

    # Create connection string
    endpoint_id = host.split('.')[0]  # Extracting the endpoint ID
    conn_str = f'postgresql://{username}:{password}@{host}/{database}?sslmode=require&options=endpoint%3D{endpoint_id}'

    try:
        engine = create_engine(conn_str)
        with engine.connect() as conn:
            print("Successfully connected to the database.")
        return engine
    except SQLAlchemyError as e:
        raise ConnectionError(f"Failed to connect to database: {e}")


def load_data_to_database(engine, json_file_path):
    with open(json_file_path, 'r') as file:
        data = json.load(file)

    try:
        with engine.connect() as conn:
            trans = conn.begin()
            try:
                conn.execute(text(DELETE_AMENITIES))
                conn.execute(text(DELETE_HOTEL))

                for item in data['data']:
                    conn.execute(text(INSERT_HOTEL), prepare_hotel_data(item))
                    for amenity in item.get("amenities", []):
                        conn.execute(text(INSERT_AMENITIES), {"HotelID": item["hotelId"], "AmenityName": amenity})

                trans.commit()
                print("Data successfully reloaded to database.")
            except Exception as e:
                trans.rollback()
                raise RuntimeError(f"Failed to load data to database: {e}")
    except SQLAlchemyError as e:
        raise ConnectionError(f"Database operation failed: {e}")

def prepare_hotel_data(item):
    return {
        "HotelID": item["hotelId"],
        "Name": item.get("name", ""),
        "ChainCode": item.get("chainCode", ""),
        "DupeId": item.get("dupeId", None),
        "IataCode": item.get("iataCode", ""),
        "GeoCodeLat": item.get("geoCode", {}).get("latitude", None),
        "GeoCodeLon": item.get("geoCode", {}).get("longitude", None),
        "CountryCode": item.get("address", {}).get("countryCode", ""),
        "Distance": item.get("distance", {}).get("value", None),
        "Unit": item.get("distance", {}).get("unit", ""),
        "Rating": item.get("rating", None),
        "LastUpdate": item.get("lastUpdate", None)
    }

if __name__ == '__main__':
    try:
        engine = make_engine()
        json_file_path = 'data.json' 
        load_data_to_database(engine, json_file_path)
    except Exception as e:
        print(f"Error: {e}")



