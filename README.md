# SNMP GUI Tool

## Overview
This project is a Python-based GUI tool for interacting with SNMP agents. It supports both **Get Next** and **Get Bulk** SNMP operations. The tool is designed to fetch and display SNMP data in a user-friendly table format using a tree-based OID navigation panel.

## Features
- **OID Navigation Tree**: Navigate predefined OID categories like System, IP, and UDP.
- **SNMP Operations**:
  - Get Next: Fetches the next SNMP object based on the provided OID.
  - Get Bulk: Retrieves multiple SNMP objects in bulk.
- **Interactive Table**: Displays fetched SNMP data in a table format.
- **Pagination**: Allows efficient handling of bulk SNMP responses.
- **Clear Data**: Reset the table for a fresh query.
- **Error Handling**: Displays meaningful error messages for SNMP or connection issues.

## Technologies Used
- Python 3.x
- PySNMP: For SNMP operations
- Tkinter: For the graphical user interface

## Installation
1. Clone the repository:
   git clone https://github.com/aannieys/SNMP_NwMnmTool.git

2. Install required dependencies:
   pip install pysnmp

3. Run the script:
   python main_pj4.py

## How to Use
1. Enter the Target (IP address of the SNMP agent).
2. Specify the Community string (default: public).
3. Input the desired OID to start with.
4. Select an operation:
   - Get Next: Fetch the next object.
   - Get Bulk: Fetch multiple objects.
5. Click Go to fetch and display the data in the table.
6. Navigate OIDs using the tree on the left and click on them to populate the OID input box.
7. Clear the table using the Clear Table button.

## Team Members
- Sirapath Thainiyom - ID: 6488108
- Suphavadee Cheng - ID: 6488120
- Jidapa Moolkaew - ID: 6488176

## Contributions
- Designing the GUI
- Implementing SNMP functionalities
- Debugging and testing the application
