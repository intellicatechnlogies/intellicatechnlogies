billable_dict = {
    "1": {
        "BILLABLE": "True",
        "MESSAGE": "Success"
    },
    "2": {
        "BILLABLE": "False",
        "MESSAGE": "Source Downtime"
    },
    "3": {
        "BILLABLE": "False",
        "MESSAGE": "Source Downtime"
    },
    "7": {
        "BILLABLE": "False",
        "MESSAGE": "Number of PANs exceeds the limit (5)"
    },
    "8": {
        "BILLABLE": "False",
        "MESSAGE": "Source Downtime"
    },
    "11": {
        "BILLABLE": "False",
        "MESSAGE": "Source Downtime"
    },
    "12": {
        "BILLABLE": "False",
        "MESSAGE": "Source Downtime"
    },
    "13": {
        "BILLABLE": "False",
        "MESSAGE": "Source Downtime"
    },
    "16": {
        "BILLABLE": "False",
        "MESSAGE": "Source Downtime"
    },
    "99": {
        "BILLABLE": "False",
        "MESSAGE": "Unknown Error"
    },
    "100": {
        "BILLABLE": "False",
        "MESSAGE": "Internal Error"
    },
    "101": {
        "BILLABLE": "True",
        "MESSAGE": "Success"
    },
    "102": {
        "BILLABLE": "False",
        "MESSAGE": "Invalid ID number or combination of inputs"
    },
    "103": {
        "BILLABLE": "True",
        "MESSAGE": "No records found for the given ID or combination of inputs"
    },
    "104": {
        "BILLABLE": "True",
        "MESSAGE": "Max retries exceeded"
    },
    "105": {
        "BILLABLE": "True",
        "MESSAGE": "Missing Consent"
    },
    "106": {
        "BILLABLE": "False",
        "MESSAGE": "RC number is registered under more than one office"
    },
    "107": {
        "BILLABLE": "False",
        "MESSAGE": "Invalid OTP"
    },
    "110": {
        "BILLABLE": "False",
        "MESSAGE": "Source Unavailable"
    },
    "200": {
        "BILLABLE": "True",
        "MESSAGE": "Success"
    },
    "304": {
        "BILLABLE": "False",
        "MESSAGE": "Access Denied(IP not whitelist)"
    },
    "401": {
        "BILLABLE": "False",
        "MESSAGE": "Your Key Has Been Expired"
    },
    "403": {
        "BILLABLE": "False",
        "MESSAGE": "Internal Server Error"
    },
    "500": {
        "BILLABLE": "False",
        "MESSAGE": "Internal server error"
    },
    "501": {
        "BILLABLE": "True",
        "MESSAGE": "Check the Parameters You have Passed"
    },
    "502": {
        "BILLABLE": "False",
        "MESSAGE": "Order submission failed"
    },
    "503": {
        "BILLABLE": "False",
        "MESSAGE": "Source Error"
    },
    "504": {
        "BILLABLE": "False",
        "MESSAGE": "OTP could not be validated"
    },
    "505": {
        "BILLABLE": "True",
        "MESSAGE": "Could not confirm order. Try Again"
    },
    "506": {
        "BILLABLE": "True",
        "MESSAGE": "Order does not belong to account"
    },
    "507": {
        "BILLABLE": "False",
        "MESSAGE": "Kindly first Create Transaction"
    },
    "510": {
        "BILLABLE": "False",
        "MESSAGE": "Internal server error"
    },
    "TXN": {
        "BILLABLE": "True",
        "MESSAGE": "Account details successfully verified"
    },
    "NNR": {
        "BILLABLE": "True",
        "MESSAGE": "Transaction Successful but no name returned from the bank"
    },
    "TUP": {
        "BILLABLE": "True",
        "MESSAGE": "Transaction under Process"
    },
    "DTX": {
        "BILLABLE": "False",
        "MESSAGE": "Duplicate Transaction. Try after 5 Minutes"
    },
    "IAN": {
        "BILLABLE": "False",
        "MESSAGE": "Invalid Account Number"
    },
    "SPE": {
        "BILLABLE": "False",
        "MESSAGE": "Service Provider Error. Account details could not be verified"
    },
    "SPD": {
        "BILLABLE": "False",
        "MESSAGE": "Bank Partner service is down. try after sometime"
    },
    "IPE": {
        "BILLABLE": "False",
        "MESSAGE": "Internal Processing Error. Try after sometime"
    },
    "ISE": {
        "BILLABLE": "False",
        "MESSAGE": "Internal System Error. try after sometime"
    },
    "SNA": {
        "BILLABLE": "False",
        "MESSAGE": "Service not Available"
    },
    "FAB": {
        "BILLABLE": "False",
        "MESSAGE": "Failure at Bank end"
    },
    "ERR": {
        "BILLABLE": "False",
        "MESSAGE": "Account could not be verified due to unexpected error"
    },
    "NRR": {
        "BILLABLE": "False",
        "MESSAGE": "Account details couldn't be verified. try after sometime"
    },
    "UNE": {
        "BILLABLE": "False",
        "MESSAGE": "Unknown Error"
    },
    "IE": {
        "BILLABLE": "False",
        "MESSAGE": "Internal Error"
    },
    "SUA": {
        "BILLABLE": "False",
        "MESSAGE": "Service Unavailable"
    },
    "ITM": {
        "BILLABLE": "False",
        "MESSAGE": "Invalid transaction Mode"
    },
    "DBD": {
        "BILLABLE": "False",
        "MESSAGE": "Beneficiary/Destination Bank/Switch is Down or Offline. Please try again later"
    },
    "DLC": {
        "BILLABLE": "False",
        "MESSAGE": "Daily Limit Crossed for a bank account. The limit is 10 transactions for an account within 12 hours"
    },
    "BFR004": {
        "BILLABLE": "True",
        "MESSAGE": "Payment received for the billing period - no bill due"
    }
}

def billable_and_response_msg(response_code:str=None):
    response_code = str(response_code)
    if response_code.strip().upper() in billable_dict.keys():
        return billable_dict[response_code]
    else:
        return billable_dict["500"]