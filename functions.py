import streamlit as st
import pandas as pd
import notion_df as nd
nd.pandas()

api_key = st.secrets["notion_keys"]["api_key"]
errors_url = st.secrets["notion_keys"]["errors_url"]
errors_id = st.secrets["notion_keys"]["errors_id"]
locations_db_id = st.secrets["notion_keys"]["locations_db_id"]
individuals_db_id = st.secrets["notion_keys"]["individuals_db_id"]
employees_id = st.secrets["notion_keys"]["employees_id"]

med_errors = pd.read_notion(errors_id, api_key=api_key, resolve_relation_values=True)


locations_db = pd.read_notion(locations_db_id, api_key=api_key, resolve_relation_values=True)
current_locations = locations_db["Name"][locations_db.Status == "Active"]
current_locations = current_locations.to_list()
current_locations += ["ALL"]

individuals_db = pd.read_notion(individuals_db_id, api_key=api_key, resolve_relation_values=True)

employees_db = pd.read_notion(employees_id, api_key=api_key)
employees_db = employees_db[employees_db.Status == "Active"]
ee = []

for i, row in employees_db.iterrows():
    name = row["Full Name"]
    ee += [name]


# List of error types
error_types = ["Wrong Dose",
                "Wrong Client",
                "Wrong Time",
                "Wrong Route",
                "Wrong Medication",
                "Medication Omission",
                "Other"]
# Corrective Action Options
corrective_actions = ["Paycom Performance Discussion Form",
                      "In house retraining",
                      "Sent back for LLAM retraining"]
# Visualization Options
viz_options = ["Program",
               "Staff Member",
               "Month",
               "Service Recipient"]


# Location filter to find the relevant individuals
def location_filter(program):

    db = individuals_db[["FN", "Program", "Active"]]
    options = []
    if program != "ALL":
        for i, row in db.iterrows():
            formatted_site = format(row['Program'])
            if program == formatted_site:
                name = format(row["FN"])
                options += [name]
    else:
        for i, row in db.iterrows():
            if row["Active"]:
                name = format(row["FN"])
                options += [name]
    return options


# Collecting the selected staff through their names and attaching them to their employee codes
def staff_selection(staff):

    ee_code = employees_db[["Full Name", "EE Code"]]

    ee_list = []

    for name in staff:
        for i, row in ee_code.iterrows():
            if row["Full Name"] == name:
                ee_list += [row["EE Code"]]

    return ee_list


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
    ca_date = format(ca_date)

    submission = pd.DataFrame()
    submission["Individual"] = individuals_db['MCI#'][individuals_db["FN"] == individual]
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


# Visiual Filters
def viz_filters(site, individuals, grouping):

    mci = individuals_db[["FN", "MCI#"]]

    location_filter = pd.DataFrame()
    if site == "ALL":
        location_filter = med_errors
    else:
        location_filter = (med_errors[med_errors["Work Locations"] == site])

    sr_filter = pd.DataFrame()
    for sr in individuals:
        for i, row in location_filter:
            if sr in row["SR"]:
                sr_filter = sr_filter.append(row)

    filtered_errors = pd.DataFrame()
    for i, row in sr_filter.iterrows():
        dsps = row["Staff Involved"]
        for dsp in dsps:
            row["Staff Involved"] = dsp
            filtered_errors = filtered_errors.append(row)

    if grouping == "Program":
        st.dataframe(filtered_errors)
        filtered_errors = filtered_errors.groupby(filtered_errors["Work Locations"]).count()
        return st.bar_chart(data=filtered_errors)
    elif grouping == "Service Recipient":
        return st.bar_chart(data=filtered_errors, x="SR")
