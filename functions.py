import datetime

import streamlit as st
import pandas as pd
import notion_df as nd
import keys

nd.pandas()

try:
    api_key = st.secrets["notion_keys"]["api_key"]
    errors_url = st.secrets["notion_keys"]["errors_url"]
    errors_id = st.secrets["notion_keys"]["errors_id"]
    locations_db_id = st.secrets["notion_keys"]["locations_db_id"]
    individuals_db_id = st.secrets["notion_keys"]["individuals_db_id"]
    employees_id = st.secrets["notion_keys"]["employees_id"]
except:
    api_key = keys.api_key
    errors_url = keys.errors_url
    errors_id = keys.errors_id
    locations_db_id = keys.locations_db_id
    individuals_db_id = keys.individuals_db_id
    employees_id = keys.employees_id

locations_db = pd.read_notion(locations_db_id, api_key=api_key, resolve_relation_values=True)
current_locations = locations_db["Name"][locations_db.Status == "Active"]
current_locations = current_locations.to_list()
all = ["ALL"]
all += current_locations
current_locations = all


med_errors = pd.read_notion(errors_id, api_key=api_key, resolve_relation_values=True)


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
               "Error Type"]


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
    submission["ID"] = individual
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

    location_filter = med_errors

    if site == "ALL":
        location_filter = location_filter
    else:
        location_filter = location_filter[med_errors["Site"] == site]

    all = "ALL"
    if all in individuals:
        sr_filter = location_filter
    else:
        sr_filter = location_filter[location_filter["SR."].isin(individuals)]

    filtered_errors = pd.DataFrame()  # Initialize an empty DataFrame

    for i, row in sr_filter.iterrows():
        dsps = row["Staff Involved"]
        for dsp in dsps:
            new_row = row.copy()  # Create a copy of the current row
            new_row["Staff Involved"] = dsp  # Update the "Staff Involved" value
            filtered_errors = pd.concat([filtered_errors, new_row.to_frame().T], ignore_index=True)

    for i, row in filtered_errors.iterrows():
        ee_code = row["Staff Involved"]
        date = row["Date of Error"]
        full_name = employees_db.loc[employees_db["EE Code"] == ee_code, "Full Name"].iloc[0]
        filtered_errors.at[i, "Staff"] = full_name

    try:
        filtered_errors = filtered_errors[["Site",
                                       "SR.",
                                       "Staff",
                                       "Date of Error",
                                       "Error Type"]]
        st.dataframe(filtered_errors, use_container_width=True)
    except:
        pass

    try:
        filtered_errors["Month"] = pd.to_datetime(filtered_errors["Date of Error"]).dt.month
    except KeyError:
        pass

    try:
        if grouping == "Program":
            program_counts = filtered_errors.groupby("Site").size().reset_index(name="Med Errors")
            return st.bar_chart(data=program_counts, x="Site",  y="Med Errors")
        elif grouping == "Staff Member":
            program_counts = filtered_errors.groupby("Staff").size().reset_index(name="Med Errors")
            return st.bar_chart(data=program_counts, x="Staff", y="Med Errors")
        elif grouping == "Month":
            program_counts = filtered_errors.groupby("Month").size().reset_index(name="Med Errors")
            return st.bar_chart(data=program_counts, x="Month", y="Med Errors")
        elif grouping == "Error Type":
            program_counts = filtered_errors.groupby("Error Type").size().reset_index(name="Med Errors")
            return st.bar_chart(data=program_counts, x="Error Type", y="Med Errors")
    except:
        pass


# TODO Archive Filters (tab3)

