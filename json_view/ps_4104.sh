!/bin/bash

jq -r 'sort_by(.EventRecordId | 
                tonumber)[] | 
                select(.EventCode == "4104") | 
                    ["------------------------", 
                    ("EventTime: " + .EventTime), 
                    ("ScriptPath: " + .EventData.Path // "N/A"), 
                    ("ScriptBlockId: "+ .EventData.ScriptBlockId // "N/A"), 
                    ("Block " + (.EventData.MessageNumber // "N/A") + " out of " + (.EventData.MessageTotal // "N/A")), 
                    "------------------------", 
                    .EventData.ScriptBlockText] | 
                join("~~~")' |
sed -e 's/~~~/\n/g' 
