import streamlit as st
import functions as f

st.set_page_config(page_title="TOBOLA Medication Errors", layout='wide')

tab1, tab2, tab3 = st.tabs(["Submission", "Analyze & Review", "Archive"])

# Submission Form
with tab1:

    st.header('TOBOLA Med Error Reporting Form')

    # Program Selection
    program = st.selectbox("Program", options=f.current_locations, key="Work Locations")

    # Columns for data collections
    l, c, r = st.columns(3)

    # Individual, Date, & Error Type Selection
    with l:
        individual_list = f.location_filter(program)
        individual = st.radio("Select Individual", options=individual_list, key='Individual')
    with c:
        error_date = st.date_input("Date of Error", key='Date of Error')
    with r:
        error_type = st.selectbox("Type of Error", options=f.error_types, key="Error Type")
        if error_type == 'Other':
            other = st.text_area("Please Describe...", key='Other')

    # Divider
    st.write("---")

    # Selecting the staff members involved in the error
    staff = st.multiselect("Select the team members involved", options=f.ee, key="Staff Involved")

    # Divider
    st.write("---")

    # Incident description
    description = st.text_area("Please summarize what occurred with this medication error."
                               " Be sure to include the medication name/strength", key="Description")

    # Corrective actions description
    description = st.text_area("Please describe what Corrective Actions were taken:", key="Corrective Action")
    ca_date = st.date_input("What was the date that the corrective action was carried out?", key="CA Date")

    # Submission
    submit = st.button("Submit Form", use_container_width=True)
    if submit:
        with st.spinner("Submitting Report. Please Wait."):
            ee_list = f.staff_selection(staff)
            f.submission(ss=st.session_state, individual=individual, ee=ee_list, date=error_date, ca_date=ca_date)
            st.success("Report Submitted!")

# Data Visualization
with tab2:
    # Filters
    with st.container():
        l, c, r = st.columns(3)
        with l:
            site = st.selectbox("Program", options=f.current_locations)
        with c:
            service_recipient = st.multiselect("Service Recipient", options=f.location_filter(site))
        with r:
            grouping = st.radio("Show data by:", options=f.viz_options)
    st.write(site)
    f.viz_filters(site, service_recipient, grouping)


with tab3:
    st.dataframe(f.med_errors)
