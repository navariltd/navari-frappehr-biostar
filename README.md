## Biostar Biometrics Integration for Frappe
FrappeHR integration with Biostar Biometrics

### Overview
This Frappe application provides integration with Biostar Biometrics to fetch attendance records bases on user-specified settings. The application uses a custom single doctype called "Biometic Settings" to securely store user credentials and configuration details needed for the integration.


#### Features
- Single doctype ("Biometric Settings") to store configurations.
- Fetch attendance records from Biostar Biometrics
- Automatic synchronization of attendance data into an ERPNext instance.

#### DocTypes
Biostar Settings

This doctype is used to store the following configuration details:


1. Username: The user id used to log in to this page
2. Password: The password used to log in to this page
3. TA URL: The time and attendance URL
4. API Key: API key generated for the user
5. API Secret: API Secret generated for the user
6. Start Date: The start date for fetching attendance records
7. End Date: The end date for fetching attendance records

Generate the API key and API secret and feed them in the TA Auth Details section.

![Screenshot from 2024-05-09 16-41-08](https://github.com/navariltd/navari-frappehr-biostar/assets/82759762/edbf8d78-3ad9-41ca-bdfb-fce7c2350ace)


 #### Fetching Attendance Records
Only two endpoints have been used to retrive attendance report from biostar server:
1. [Authentication](https://bs2api.biostar2.com/#0b54ae8b-6744-44dd-8556-8001ae3139ff)
2. [How to retrieve attendance report in json format](https://support.supremainc.com/en/support/solutions/articles/24000073530--biostar-2-ta-api-how-to-retrieve-report-in-json-format-via-biostar-2-ta-api)

One needs to assign shifts to users on the biostar server, set up schedules and schedule templates on the biostar server, [here is a summary](https://www.youtube.com/watch?v=lqp8OEcPRyI&t=1023s) of how to do it. <br>
This enables creation of checkin/checkout logs on the biostar server.

#### Installation
1. Ensure you have a working Frappe and ERPNext instance
2. Clone this repository into your Frappe bench apps directory.

 ``` 
 git clone https://github.com/navariltd/navari-frappehr-biostar.git
 ```

 3. Install the app into your site
 ``` 
 bench --site [your-site-name] install-app navari_frappehr_biostar
 ```
 4. Configure the "Biometric Settings" doctype with appropriate values.

 #### Usage
 This application includes scheduled tasks and manual functions that can be triggered to fetch and sync attendance data from Biostar Biometrics api based on the configurations you set in the "Biometric Settings"



#### Summary
Suprema Biostar is a web-based security platform that manages biometric access control systems and time attendance solutions.

##### Key features
1. Biometric Integration: Fingerprint, face recognition and card-based access for versatile and secure access control options.
2. Attendance Record Fetch: Fetch attendance records from the system

#### Key Functions
- BiostarConnect: Handles connection and data fetching from Biostar
- send_to_erpnext: Sends fetched attendance records to ERPNext instance

#### License
