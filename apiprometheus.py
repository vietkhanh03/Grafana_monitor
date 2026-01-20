from flask import Flask, jsonify
import requests
from datetime import datetime, timedelta
import time

app = Flask(__name__)

def fetch_and_process_data():
    url = 'http://172.16.2.87:9090/api/v1/query_range'

    # Calculate the start and end times for the last 7 days
    end_time = datetime.now()
    start_time = end_time - timedelta(weeks=1)

    # Convert to Unix timestamps
    end_timestamp = int(time.mktime(end_time.timetuple()))
    start_timestamp = int(time.mktime(start_time.timetuple()))

    # Query 1
    query_1 = 'node_filesystem_size_bytes{mountpoint="/"} - node_filesystem_avail_bytes{mountpoint="/"}'
    # Query 2
    query_2 = 'node_filesystem_size_bytes{fstype=~"ext.*|xfs",mountpoint="/"} - 0'

    # Prometheus query for range data
    params_1 = {
        'query': query_1,
        'start': start_timestamp,
        'end': end_timestamp,
        'step': '1h'  # Fetch data every 1 hour
    }

    params_2 = {
        'query': query_2,
        'start': start_timestamp,
        'end': end_timestamp,
        'step': '1h'  # Fetch data every 1 hour
    }

    # Make requests for both queries
    response_1 = requests.get(url, params=params_1)
    response_2 = requests.get(url, params=params_2)

    # Check if both responses were successful
    if response_1.status_code != 200 or response_2.status_code != 200:
        return {"error": f"Request failed with status code {response_1.status_code} or {response_2.status_code}"}

    data_1 = response_1.json()
    data_2 = response_2.json()

    print(data_1)  # Log the response from Prometheus for query 1
    print(data_2)  # Log the response from Prometheus for query 2

    # Process data for both queries
    result_list = []
    if 'data' in data_1 and 'result' in data_1['data']:
        for result in data_1['data']['result']:
            metric = result['metric']
            for value in result['values']:  # 'values' is an array of [timestamp, value]
                timestamp = datetime.fromtimestamp(value[0]).strftime('%Y-%m-%d %H:%M:%S')
                value = value[1]

                # Extract the IP from the 'instance' field
                ip_address = metric.get('instance', '').split(':')[0]

                result_list.append({
                    "query": "Disk Used",
                    "timestamp": timestamp,
                    "device": metric.get('device', 'N/A'),
                    "mountpoint": metric.get('mountpoint', 'N/A'),
                    "ip_address": ip_address,
                    "value": value
                })

    if 'data' in data_2 and 'result' in data_2['data']:
        for result in data_2['data']['result']:
            metric = result['metric']
            for value in result['values']:  # 'values' is an array of [timestamp, value]
                timestamp = datetime.fromtimestamp(value[0]).strftime('%Y-%m-%d %H:%M:%S')
                value = value[1]

                # Extract the IP from the 'instance' field
                ip_address = metric.get('instance', '').split(':')[0]

                result_list.append({
                    "query": "Disk Size",
                    "timestamp": timestamp,
                    "device": metric.get('device', 'N/A'),
                    "mountpoint": metric.get('mountpoint', 'N/A'),
                    "ip_address": ip_address,
                    "value": value
                })
    else:
        return {"error": "Invalid response format"}

    return result_list

@app.route('/api/prometheus', methods=['GET'])
def metrics():
    try:
        data = fetch_and_process_data()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
