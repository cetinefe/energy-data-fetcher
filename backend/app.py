from flask import Flask, request, jsonify
from flask_cors import CORS
import datetime
import pandas as pd
import mysql.connector
from mysql.connector import Error
import requests
import os
import signal
import threading

app2 = Flask(__name__)
CORS(app2)

status = {
    'print_content_1': '',
    'print_content_2': '',
    'print_content_3': '',
    'newly_inserted_rows': [],
    'area_types': []
}

def data_main(day_range, area_type_input, areas):
    global status
    try:
        status = {
            'print_content_1': status.get('print_content_1', ''),  # Preserve print_content_1
            'print_content_2': '',
            'print_content_3': '',
            'newly_inserted_rows': []
        }

        day_range = int(day_range)
        raw_today = datetime.datetime.now()
        today = raw_today.strftime("%Y-%m-%d")
        start_day = (raw_today - datetime.timedelta(days=day_range)).strftime("%Y-%m-%d")

        status['print_content_2'] = f'-Fetching Interval: {start_day} to {today}\n'

        # Filter the selected areas
        areas_filtered = [area for area in areas if area['code'][:3] == area_type_input]

        # Prompt Extraction Initiation
        status['print_content_3'] += f"Extracting Data for:\n"

        # Data Extraction for Area Type one by one for each Area
        table = {}
        extracted_areas = set()
        for area in areas_filtered:  # add [:4] to the right if you want to test a sample of size 4
            if area['code'] not in extracted_areas:
                status['print_content_3'] += f" ... {area['name']} ... {area['code']} ...\n"
                extracted_areas.add(area['code'])
                table[(area['name'], area["code"])] = extract_data(area["code"], start_day, today)

        status['print_content_2'] += '\n-Extraction Complete...\n'
        transformed_data = transform(table, start_day, today, day_range)
        status['print_content_2'] += '\n-Transformation Complete...\n'

        inserted_keys = load(transformed_data)
        loaded_data = transformed_data.values.tolist()

        unignored_rows = [row for row in loaded_data if row[0] not in inserted_keys]

        status['newly_inserted_rows'] = unignored_rows
        if not status['newly_inserted_rows']:
            status['print_content_2'] += 'No new data inserted.\n'
        else:
            status['print_content_2'] += f'{len(status["newly_inserted_rows"])} new rows inserted.\n'
    except Exception as e:
        status['print_content_2'] += f"Error: {e}\n"
        print(f"Error: {e}")

def extract_init():
    cookies = {'cookieConsent': 'true', 'uu.app.bpl': '0'}
    headers = {
        'Accept': 'application/json',
        'Accept-Language': 'en-US,en;q=0.9,tr;q=0.8',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json; charset=utf-8',
        'Origin': 'https://newtransparency.entsoe.eu',
        'Referer': 'https://newtransparency.entsoe.eu/load/total/dayAhead?appState=%7B%22sa%22%3A%5B%22CTY%7C10YPL-AREA-----S%22%5D%2C%22st%22%3A%22CTY%22%2C%22mm%22%3Atrue%2C%22ma%22%3Afalse%2C%22sp%22%3A%22HALF%22%2C%22dt%22%3A%22CHART%22%2C%22df%22%3A%5B%222024-07-17%22%2C%222024-07-17%22%5D%7D',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        'X-Request-Id': '170749f0-33e382c1-ae4a43df-0000',
        'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
    }
    return cookies, headers

def extract_area_codes():
    global status
    status['print_content_1'] = ""
    status['print_content_1'] += f"\n-Extracting Area Types & Codes... \n"
    cookies, headers = extract_init()
    json_data = {'attributeList': [dict(useCase=None, code='AREA', strict=True)]}
    response = requests.post('https://newtransparency.entsoe.eu/enum/list', cookies=cookies, headers=headers, json=json_data)
    response.raise_for_status()
    areas = response.json()["enumList"][0]["attributeEnum"]
    print(areas)
    return areas
    
def transform_area_codes(areas):
    global status
    status['print_content_1'] += f"\n-Transforming Area Types & Codes... \n"
    area_types = list({area['code'][:3] for area in areas})
    area_types.sort()
    area_type_table = {}
    max_length = 0
    for at in area_types:
        area_type_table[at] = list({ant[0] for ant in list({(area['name'], area['code'][:3]) for area in areas})
                               if ant[1] == at})
        max_length = max(max_length, len(area_type_table[at]))

    # Ensure all lists are of the same length by padding with None
    for key in area_type_table:
        while len(area_type_table[key]) < max_length:
            area_type_table[key].append(None)

    att = pd.DataFrame(area_type_table).T
    att = att.reindex(sorted(att.columns), axis=1)
    pd.options.display.width = 0 
    status['print_content_1'] += f"\n{att}"
    status['area_types'] = area_types  # Update status with area types
    return area_types

def input_area_code(area_type_input, area_types):    
    while True:
        try:
            if area_type_input not in area_types:
                raise ValueError(f"\n Invalid area type selected. Please select one from {area_types}.\n")
            break  # Exit the loop if the input is valid
        except ValueError as ve:
            print(ve)  # Print the error message and loop again

    return area_type_input

def extract_data(area_code, start_day, end_day):
    cookies, headers = extract_init()
    json_data = {
        'dateTimeRange': {'from': f'{start_day}T22:00:00.000Z', 'to': f'{end_day}T22:00:00.000Z'},
        'areaList': [area_code],
        'timeZone': 'CET',
        'sorterList': [],
        'filterMap': {}
    }
    response = requests.post('https://newtransparency.entsoe.eu/load/total/dayAhead/load', cookies=cookies, headers=headers, json=json_data)
    response.raise_for_status()
    content_json = response.json()
    data_json = content_json["instanceList"][0]["curveData"]["periodList"][0]["pointMap"]
    return data_json

def transform(table, start_day, end_day, day_range):
    flattened_table = []
    for (area_name, area_code), data in table.items():
        freq = "15min" if len(data) == (day_range * 96) else "30min" if len(data) == (day_range * 48) else "60min"
        date_time = pd.date_range(start=start_day, end=end_day, freq=freq, inclusive='left')
        for i, (key, values) in enumerate(data.items()):
            if i >= len(date_time):
                break
            dt = date_time[i]
            total_load = values[0] if isinstance(values[0], str) else values[0].get('alt', None)
            da_forecast = values[1] if isinstance(values[1], str) else values[1].get('alt', None)
            flattened_table.append((dt, total_load, da_forecast, area_code, area_name))
    load_frame = pd.DataFrame(flattened_table, columns=["DateTime", "Total_Load", "DA_Forecast", "Area_Code", "Area_Name"])
    load_frame["DATE_AREA_KEY"] = load_frame["DateTime"].astype(str) + "_" + load_frame["Area_Code"]
    load_frame = load_frame[["DATE_AREA_KEY", "DateTime", "Total_Load", "DA_Forecast", "Area_Code", "Area_Name"]]
    load_frame['Total_Load'] = load_frame["Total_Load"].apply(lambda x: float(x) if isinstance(x, (int, float, str)) and str(x).replace('.', '', 1).isdigit() else None)
    load_frame['DA_Forecast'] = load_frame["DA_Forecast"].apply(lambda x: float(x) if isinstance(x, (int, float, str)) and str(x).replace('.', '', 1).isdigit() else None)
    load_frame.dropna(subset=["Total_Load", "DA_Forecast"], inplace=True)
    return load_frame

def load(load_frame):
    db_config = {
        'user': 'root',
        'password': '4512Pk__',
        'host': '127.0.0.1',
        'database': 'gender_schema'
    }
    data_to_insert = []
    inserted_keys = []
    try:
        with mysql.connector.connect(**db_config) as connection:
            if connection.is_connected():
                print("Connected to MySQL database")
                data_to_insert = load_frame.values.tolist()
                cursor = connection.cursor()

                # Fetch the inserted rows
                for row in data_to_insert:
                    cursor.execute("SELECT * FROM power WHERE DATE_AREA_KEY = %s", (row[0],))
                    result = cursor.fetchone()
                    if result:
                        inserted_keys.append(row[0])

                # Inserting data
                insert_query = """INSERT IGNORE INTO power 
                                  (DATE_AREA_KEY, Date_Time, Total_Load, DA_Forecast, Area_Code, Area_Name) 
                                  VALUES (%s, %s, %s, %s, %s, %s)"""               
                cursor.executemany(insert_query, data_to_insert)
                connection.commit()
                print("Data inserted into MySQL database successfully!")
                print(inserted_keys)
                
    except Error as e:
        print(f"Error: {e}")
        
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection closed")
    return inserted_keys

@app2.route('/')
def index():
    return "React Frontend"

@app2.route('/fetch_area_codes', methods=['POST'])
def fetch_area_codes():
    try:
        areas = extract_area_codes()
        area_types = transform_area_codes(areas) # Print Area Type Table
        return jsonify({'status': 'success', 'area_types': area_types, 'areas': areas})
    except Exception as e:
        print(f"Error: {e}")  # Print the error message for debugging
        return jsonify({'status': 'error', 'message': str(e)})

@app2.route('/fetch_data', methods=['POST'])
def fetch_data():
    try:
        data = request.json
        day_range = data['day_range']
        area_type = data['area_type']
        areas = data['areas']
        thread = threading.Thread(target=data_main, args=(day_range, area_type, areas))
        thread.start()
        return jsonify({'status': 'success'})
    except Exception as e:
        print(f"Error: {e}")  # Print the error message for debugging
        return jsonify({'status': 'error', 'message': str(e)})

@app2.route('/status', methods=['GET'])
def get_status():
    return jsonify(status)

@app2.route('/restart', methods=['POST'])
def restart():
    global status
    status = {
        'print_content_1': '',
        'print_content_2': '',
        'print_content_3': '',
        'newly_inserted_rows': []
    }
    os.kill(os.getpid(), signal.SIGINT)
    return jsonify({'status': 'success', 'message': 'Server is restarting...'})

if __name__ == '__main__':
    app2.run(debug=True, port=5001)
