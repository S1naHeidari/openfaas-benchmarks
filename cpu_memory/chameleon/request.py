import json
import requests

url = "http://192.168.56.11:31112/function/chameleon"
data = {"num_of_rows": 10, "num_of_cols": 10, "uuid": "1234"}

# Make the POST request
response = requests.post(url, json=data)

# Check if the request was successful (status code 200)
if response.status_code == 200:
    # Extract the last line of the response
    #last_line = response.text
    last_line = response.text.strip().splitlines()[-1]
    last_line = last_line.replace("'", "\"")
    #print(last_line)
    # Parse the JSON response
    try:
        json_response = json.loads(last_line)
        # Print or manipulate the JSON data as needed
        print(json_response)

        # Optionally, save the JSON data to a file
        with open("response.json", "w") as f:
            json.dump(json_response, f, indent=2)
    except json.JSONDecodeError as e:
        print(f'Error decoding JSON: {e}')
else:
    print(f"Error: {response.status_code}, {response.text}")

