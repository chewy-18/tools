#!/usr/bin/python3

import json
import argparse
import os

def main():
    
    
    # Parsing the arguments
    parser = argparse.ArgumentParser(description="Script to parse output of evtx2json PS logs and output the raw scripts")
    parser.add_argument("-f", required=True, help="JSON file to operate on")
    parser.add_argument("-w", help="Output directory. Default is current directory.")
    parser.add_argument("-v", action="store_true", help="Verbose mode - per names of output to stdout")

    args = parser.parse_args()
    
    with open(args.f, "r") as f:
        ps_log = json.loads(f.read())
    
    if args.w: 
        output_dir = args.w
    else:
        output_dir = os.getcwd()
    
    if not output_dir.endswith("/"):
        output_dir += "/"
        
    offset = 0 
    for nums in range(len(ps_log)):

        # Event Code that has the data 
        if ps_log[nums + offset]["EventCode"] == "4104":
            if ps_log[nums].get("EventData", {}).get("Path", "") != "":
                temp_path = ps_log[nums + offset].get("EventData", {}).get("Path", "no_path.ps1").replace("\\", "__")
            else:
                temp_path = "no_path.ps1"

            script_name = ps_log[nums + offset]["EventTime"] + "__" + temp_path

            temp_output = ""
            for message_num in range(1, 1 + int(ps_log[nums + offset]["EventData"]["MessageTotal"])):
                temp_output += ps_log[nums + offset]["EventData"].get("ScriptBlockText", "")
                if message_num != 1:
                    offset += 1
            if args.v:
                print("Writing out file: " + script_name + " with " + ps_log[nums + offset]["EventData"]["MessageTotal"] + " blocks")
            with open(output_dir + script_name, "w") as f:
                f.write(temp_output)
        # Break loop if hit offset + nums
        if nums + offset == len(ps_log) - 1:
            break
            
            
main()