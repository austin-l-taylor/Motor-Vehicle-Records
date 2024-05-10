# Docusign\MVR API Process

## This process uses the Docusign API to send and process MVR requests and update them through Smartsheet.

### Introduction

This process should shows how you can utilize the **Docusign API** to send envelopes, check an envelopes status, and download signed envelopes as an attachment. The Docusign API portion of the process is handled using **Python** while the status changes in Smartsheet are handled using **Seth's Smartsheet Activities.** <br />
Please Note: All credentials can be found VIA keeper under MVR.

### Basic Functions:

- Sends an MVR request from stored procedure in Smartsheet using the Docusign API.
  - Current envelope status is recorded in a csv and updated in Smartsheet.
- Checks the status of all envelopes using the Envelope ID from smartsheet.
  - Downloads .pdf signed forms.
  - changes name to match the correct Envelope ID.
  - Attaches the signed envelope to Smartsheet.
- Checks for approved envelopes in MVR and changes them to "Approved" in FRMS.

### Flowchart
![LucidChart Diagram](MVR%20Process%20Flowchart.jpg)

### Technologies used:

- Python
  - Docusign API.
  - Pandas.
  - Keeper.
  - powershell.
- Ui Path
  - Basic activities
  - Seth's Smartsheet Activities.

### Installation Guide

1. Docusign SDK guide click [here](https://developers.docusign.com/docs/esign-rest-api/quickstart/) and follow the on screen prompts.

   - Name your project.
   - Pick your programming language.
   - Select JWT Grant Remote signing example.
   - Download.

2. Install Dependencies
```
pip install -r requirements.txt
```

### API Documentation

- After setting up your project from the QuickStart guide click [here](https://developers.docusign.com/docs/esign-rest-api/how-to/) to search through different functions that can be added directly to your project.
- For a more in depth Github Docusign API documetation guide click [here](https://docusign.github.io/docusign-esign-python-client/docusign_esign/apis/envelopes_api.html)
- How to Go Live Guide click [here](https://developers.docusign.com/docs/esign-rest-api/go-live/)

### Account Information
#### Production Environment
- Admin Portal: https://admin.docusign.com
- Account Portal: https://apps.docusign.com/

#### Sandbox Environment
- Admin Demo Portal: https://admindemo.docusign.com/
- Account Demo Portal: https://appdemo.docusign.com

### Account Rep
Name: Trent Tornincasa  
Email: trent.tornincasa@docusign.com  
Phone: 219-730-0222  
