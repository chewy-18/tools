#!/usr/bin/python3

import Evtx.Evtx as evtx
import json
import glob
import xmltodict
import json
import argparse
import sys

config = {
    "4624": {
        "Add": {
            "Message": "An account was successfully logged on."
        },
        "Enrich": {
            "LogonType": {
                "2": "2 - Interactive (logon at keyboard and screen of system)",
                "3": "3 - Network (i.e. connection to shared folder on this computer from elsewhere on network)",
                "4": "4 - Batch (i.e. scheduled task)",
                "5": "5 - Service (Service startup)",
                "7": "7 - Unlock (i.e. unnattended workstation with password protected screen saver)",
                "8": "8 - NetworkCleartext (Logon with credentials sent in the clear text. Most often indicates a logon to IIS with 'basic authentication')",
                "9": "9 - NewCredentials such as with RunAs or mapping a network drive with alternate credentials.  This logon type does not seem to show up in any events.",
                "10": "10 - RemoteInteractive (Terminal Services, Remote Desktop or Remote Assistance)",
                "11": "11 - CachedInteractive (logon with cached domain credentials such as when logging on to a laptop when away from the network)",
                }
        }
    },
    "1102": {
        "Add": {
            "Message": "The audit log has been cleared."
        }
    }
}

def main():

    # Parsing the arguments
    parser = argparse.ArgumentParser(description="Script to convert evtx to JSON")
    parser.add_argument("-f", required=True, help="File, directory (with \"/\" appended)  or file grouping to operate on")
    parser.add_argument("-w", action="store_true", help="Write output to file. Default is to stdout")
    parser.add_argument("-s", action="store_true", help="Write output to separate files. Default is one giant file")
    parser.add_argument("-r", action="store_true", help="Preserve raw XML output. Default cleans it up")
    parser.add_argument("-e", action="store_true", help="Enrich the data with prebuilt config")
    
    args = parser.parse_args()   
    
    if (args.s and not args.w):
        print("Error: You must use -w flag with -s flag")
        exit(1)

    # Handling directory case
    if args.f.endswith("/"):
        files_to_operate = glob.glob(args.f+"*")
    else:
        files_to_operate = glob.glob(args.f)

    final_list = [file for file in files_to_operate if file.endswith(".evtx")]

    if len(final_list) == 0:
        print("Error: Not a valid location or no files with evtx extension")
        exit(1)

    return_list = []
    for files in final_list:
        temp_list = process_file(files) 
        
        if not args.r:
            temp_list = clean_keys(temp_list)
            temp_list = sorted(temp_list, key=lambda k: int(k["EventRecordId"]))
        else: 
            temp_list = sorted(temp_list, key=lambda k: int(k.get("Event", {}).get("System", {}).get("EventRecordID", ""))) 
            
        if args.e:
            temp_list = enrich_data(temp_list, config)
            
        # Separete files to output
        if args.s:
            with open(files.replace(".evtx", ".json"), "w") as f:
                f.write(json.dumps(temp_list))
        else:
            return_list.extend(temp_list)

    if args.w:
        write_string = final_list[0].rsplit("/", 1)[0] + "/" + "combined.json"
        with open(write_string, "w") as f:
            f.write(json.dumps(return_list))
    else:
        print(json.dumps(return_list))


def process_file(file_location):
    results_list = [] 
    with evtx.Evtx(file_location) as log:
        for record in log.records():
            results_list.append(dict(xmltodict.parse(record.xml())))

    return results_list

def clean_keys(json_list):
    return_list = []
    for records in json_list:
        temp_dict = {"EventCode": records.get("Event", {}).get("System", {}).get("EventID", {}).get("#text", ""),
                    "EventTime": records.get("Event", {}).get("System", {}).get("TimeCreated", {}).get("@SystemTime", "").replace(" ", "T"),
                    "Log": records.get("Event", {}).get("System", {}).get("Channel", ""),
                    "ComputerName": records.get("Event", {}).get("System", {}).get("Computer", ""),
                    "EventRecordId": records.get("Event", {}).get("System", {}).get("EventRecordID", ""), 
                    "UserData": records.get("Event", {}).get("UserData", {})}
        temp_event_data_dict = {} 
        if records.get("Event", {}).get("EventData"):
            for entries in records.get("Event", {}).get("EventData", {}).get("Data", []):
                temp_event_data_dict[entries["@Name"]] = entries.get("#text", "")
        for keys, values in records.get("Event", {}).get("System", {}).get("Execution", {}).items():
            temp_dict[keys] = values
        temp_dict["EventData"] = temp_event_data_dict
        return_list.append(temp_dict)
        
    return return_list

def enrich_data(json_list, config):
    for records in json_list:
        if records["EventCode"] in config.keys():
            for keys, values in config[records["EventCode"]].get("Add", {}).items():
                records[keys] = values
            for keys, values in config[records["EventCode"]].get("Enrich", {}).items():
                temp_val = records["EventData"][keys]
                records["EventData"][keys] = values.get(temp_val, "")
    return json_list

main()

