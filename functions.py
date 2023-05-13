import datetime

import pandas as pd
import notion_df as nd
nd.pandas()


api_key = "secret_omL8nzIdOZySUeAtSOCHm0bUNh2ydXdohuePKPBXkxm"

# Connection to "Medication Errors" database for submission
errors_url = "https://www.notion.so/626b1e9dd8a842249bca94bf2d23a04b?v=7111baba14544c99be36fd58cfa2fa97&pvs=4"
errors_id = "626b1e9dd8a842249bca94bf2d23a04b"



# Connection to "Work Locations" database and creating a list of location names
locations_url = "https://www.notion.so/7bc4a3417151424ca8707f5a1b1d5e03?v=4f28dc82c13f490da06f962384736ede&pvs=4"
locations_db_id = "7bc4a3417151424ca8707f5a1b1d5e03"
locations_db = pd.read_notion(locations_db_id, api_key=api_key, resolve_relation_values=True)
current_locations = locations_db["Name"][locations_db.Status == "Active"]
current_locations = current_locations.to_list()

# Connection to "Service Recipients" database and creating a list of individual names
individuals_url = "https://www.notion.so/63d18ada53dd4fe195684bfa4c1faf94?v=31e11034cc2342f8b77b18a9767c1525&pvs=4"
individuals_db_id = "63d18ada53dd4fe195684bfa4c1faf94"
individuals_db = pd.read_notion(individuals_db_id, api_key=api_key, resolve_relation_values=True)


# Location filter to find the relevant individuals
def location_filter(program):

    db = individuals_db[["First Name", "Program"]]
    options = []

    for i, row in db.iterrows():
        formatted_site = format(row['Program'])[2:-2]
        if program == formatted_site:
            name = format(row["First Name"])
            options += [name]

    return options


# List of error types
error_types = ["Wrong Dose",
                "Wrong Client",
                "Wrong Time",
                "Wrong Route",
                "Wrong Medication",
                "Medication Ommission",
                "Other"]

# Connection to "Employee" database and creating a list of staff names
employees_url = "https://www.notion.so/03764697bdf74f2b938313815cf62069?v=b558a6f4b7ab49e99608fa960fb6d941&pvs=4"
employees_id = "03764697bdf74f2b938313815cf62069"
employees_db = pd.read_notion(employees_id, api_key=api_key)
employees_db = employees_db[employees_db.Status == "Active"]
ee = []

for i, row in employees_db.iterrows():
    name = fr"{row['First Name']} {row['Last Name']}"
    ee += [name]

# Collecting the selected staff through their names and attaching them to their employee codes
def staff_selection(staff):

    ee_code = employees_db[["Full Name", "EE Code"]]

    ee_list = []

    for name in staff:
        for i, row in ee_code.iterrows():
            if row["Full Name"] == name:
                ee_list += [row["EE Code"]]


    return ee_list

# Corrective Action Options
corrective_actions = ["Paycom Performance Discussion Form",
                      "In house retraining",
                      "Sent back for LLAM retraining"]


# Submission function to close the report
def submission(ss, individual, date, ee, ca_date):
    import random
    import string

    def get_random_string(length):
        # choose from all lowercase letter
        letters = string.ascii_uppercase
        result_str = ''.join(random.choice(letters) for i in range(length))
        return result_str

    id = format(individual[0]+format([ss["Work Locations"][0]])[2:-2]+get_random_string(6))
    date = format(date)


    submission = pd.DataFrame()
    submission["Individual"] = [individual]
    submission["ID"] = id
    submission["Work Locations"] = [ss["Work Locations"]]
    submission["Date of Error"] = date
    submission["Error Type"] = [ss["Error Type"]]
    submission["Staff Involved"] = [ee]
    submission["Description"] = ss["Description"]
    submission["Corrective Action"] = ss["Corrective Action"]
    submission["CA Date"] = ca_date
    try:
        submission["Other"] = ss["Other"]
    except:
        pass
    submission.to_notion(errors_url, title=individual, api_key=api_key, resolve_relation_values=True)
