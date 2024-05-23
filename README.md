## FrappeHR to Suprema Biostar Biometric Integration

### Introduction
**Suprema Biostar** is a leading provider of biometric solutions specializing in advanced technologies for time and attendance management, access control, and workforce management.

Their solutions leverage biometric authentication methods such as fingerprint recognition, facial recognition, and iris scanning to provide accurate and secure identification of individuals.

**Frappe HR** on the other hand is an independent, fully-featured people management system that offers a comprehensive suite of HR functionalities. Originally part of the ERPNext ecosystem, Frappe HR has evolved into a standalone solution focused on meeting the diverse needs of modern HR departments and organizations.

### Overview
This Frappe application offers a robust integration with Suprema Biostar Biometrics, enabling seamless synchronization of employee check in records based on specific user configurations. It features a dedicated single doctype, "Biometric Settings," which securely manages user credentials and essential configuration details required for effective integration.

##### Key features
2. **Automatic Data Sync**: Seamlessly sync employee check in data from Biostar Biometrics to Frappe HR, simplifying the attendance management process.
3. **Configurable Settings**: Utilize the "Biometric Settings" doctype to easily configure and manage integration settings such as API keys, user credentials, and synchronization intervals.
4. **Manual and Scheduled Fetching**: Options to manually trigger data fetching or set up scheduled tasks for automatic updates, providing flexibility in how data is retrieved and managed.

#### Key Functions
1. **BiostarConnect**: This function is crucial as it establishes and manages the connection to the Biostar Biometrics system. It handles all communications between Frappe HR and Biostar, ensuring secure and reliable data transfer.

2. **fetchAttendanceRecords**: This function fetches employee check in data from Biostar, using date ranges provided by the user. It efficiently processes this data, readying it for synchronization with the Frappe HR database.

3. **sendToFrappeHR**: After fetching the data from Biostar, this function sends it to the FrappeHR instance. It ensures that check in records are accurately reflected in the ERP system, aligning with HR and payroll modules for comprehensive management.

4. **scheduleSync**: Automates the process of data synchronization. Users can configure the frequency at which the synchronization occurs, whether daily, weekly, or monthly, ensuring that the data in Frappe HR is always up to date without manual intervention.

5. **encryptCredentials**: Given the sensitive nature of user credentials and API keys, this function encrypts this information before storing it in the database. This practice enhances the security of the system, protecting it from unauthorized access.

6. **updateSettings**: Allows users to update or modify the Biometric Settings directly from the Frappe interface, including API keys, user credentials, and synchronization settings, making the system adaptable to changes in the operational environment or in user requirements.

#### DocTypes
<h4>Biostar Settings</h4>

This doctype is used to store the following configuration details:

1. **Username**: The user id used to log in to this page
2. **Password**: The password used to log in to this page
3. **TA URL**: The time and attendance URL
4. **API Key**: API key generated for the user
5. **API Secret**: API Secret generated for the user
6. **Start Date**: The start date for fetching attendance records
7. **End Date**: The end date for fetching attendance records

#### Usage
This application provides both scheduled tasks and manual functions to fetch and synchronize check in data from Biostar Biometrics API based on the configurations set in the "Biometric Settings" doctype.
### Manual Trigger for Biostar Settings

#### Biostar Settings Doctype

1.  **Navigate to the "Biometric Settings" doctype.**
2.  **Fill in the required configuration details:**
    -   Username
    -   Password
    -   API Key
    -   API Secret
    -   Callback URL
    -   Start Date
    -   End Date
3.  **Save the settings.**
4.  **To manually trigger attendance data synchronization:**
    -   Call the `add_checkin_logs_for_current_day()` function to fetch attendance records for the current day.
    -   Call the `add_checkin_logs_for_specified_dates(start_date, end_date)` function to fetch attendance records for a specified date range.

#### Employee Doctype

1.  **Navigate to the "Employee" doctype.**
2.  **Choose the respective employee whose attendance you want to fetch.**
3.  **Click on the "Fetch Attendance" button.** In the dialog, enter the dates for which you want to fetch the attendance. By default, the start date will be the last sync date (you can change this if needed).
4.  **Check the "Employee Checkins" for the retrieved data.**
![image (2)](https://github.com/navariltd/navari-frappehr-biostar/assets/60258622/df3caae8-d1d3-4231-9c47-2a7721a1a19a)

### Fetching Attendance for Multiple Employees

If you want to fetch attendance for employees who belong to the same department or a specific list:

1.  **Navigate to the "Employee" doctype.**
2.  **Use filters to get the respective employees you want to fetch.**
3.  **Click on the "Action" button and choose "Fetch Attendance".** This will queue the job in the background and trigger the function to fetch the attendance.
   ![image](https://github.com/navariltd/navari-frappehr-biostar/assets/60258622/619bc34c-bf92-4f3a-a4ea-c4e9cc6590a8)

  
#### Fetching Attendance Records
Only two endpoints have been used to retrive attendance report from biostar server:
1. [Authentication](https://bs2api.biostar2.com/#0b54ae8b-6744-44dd-8556-8001ae3139ff)
2. [How to retrieve attendance report in json format](https://support.supremainc.com/en/support/solutions/articles/24000073530--biostar-2-ta-api-how-to-retrieve-report-in-json-format-via-biostar-2-ta-api)

One needs to assign shifts to users on the biostar server, set up schedules and schedule templates on the biostar server, [here is a summary](https://www.youtube.com/watch?v=lqp8OEcPRyI&t=1023s) of how to do it. <br>
This enables creation of checkin/checkout logs on the biostar server.

#### Impact
This integration not only enhances security and operational efficiency but also supports compliance with labor regulations by maintaining accurate and verifiable attendance records. It reduces the administrative burden of manually managing attendance data, thus allowing HR personnel to focus on more strategic tasks.

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

Generate the API key and API secret and feed them in the TA Auth Details section.

```
To generate the keys above navigate to the "My Account" section
```

![Screenshot from 2024-05-10 12-49-05](https://github.com/navariltd/navari-frappehr-biostar/assets/82759762/ec9144e5-8ffd-4f0b-a5da-73ef8fcf2216)

```
Go to "Settings" 

Click on "API Access" and Generate Keys
```
![Screenshot from 2024-05-10 12-49-19](https://github.com/navariltd/navari-frappehr-biostar/assets/82759762/ee40e69d-5b3a-48c1-b6f7-af9a2dae5849)

```
Add the generated keys to the Biometric Settings Form and save
```

![Screenshot from 2024-05-09 16-41-08](https://github.com/navariltd/navari-frappehr-biostar/assets/82759762/edbf8d78-3ad9-41ca-bdfb-fce7c2350ace)
 
