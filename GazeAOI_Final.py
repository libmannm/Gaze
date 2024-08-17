from EyeMotionsIntake_Final import check_files, Intake
from GazeExport_Final import gazeExport

from datetime import datetime
from tqdm import tqdm
import json



def GazeAOI(data_folder, timestamp_folder, results_folder, JSON_out = f"{datetime.now().date()}.json", CSV_out = f"{datetime.now().date()}.csv", error_out = f"Errors_{datetime.now().date()}.csv", neither_cutoff = 100):
    """
    Aggregates the process of checking the data, processing it, analyzing it, and then exporting it.
    
    Parameters
    ----------
    data_folder : Folder path containing EyeMotions data.
    timestamp_folder : Folder path containing the response files.
    results_folder : Folder path where you would like the results (CSV, JSONs, errs).
    JSON_out : output path for data in a JSON format.  The default is f"{datetime.now().date()}.json".
    CSV_out : output path for data in a CSV format.  The default is f"{datetime.now().date()}.csv".
    neither_cutoff : the maximum time spent looking at Neither between Ls or Rs to be considered a "transition" Neither. The default is 100.

    Returns
    -------
    dictionary : Same as the dictionary exported via JSON_out
    """
    dictionary = {}
    errs = []
    
    arr = check_files(data_folder, timestamp_folder)
     
    for row in tqdm(arr):
        a = Intake(row[0], row[1], neither_cutoff = neither_cutoff)
        errs = errs + a.err_list
        if a.check_err == True:
            dictionary.update(a.return_dict())
        
    gazeExport(data = dictionary, 
                CSV_out = results_folder + CSV_out)
    
    out_file = open(results_folder + JSON_out, "w")
    json.dump(dictionary, out_file, indent = 4)
    
    with open(results_folder + error_out, "w") as file:
        for item in errs:
            file.write(item + "\n")
            
    return dictionary

c = GazeAOI(data_folder = "M:/AResearch/Gaze_AOI2/Eye Tracking/",
        timestamp_folder= "M:/AResearch/Gaze_AOI2/Eye Tracking/Timestamps/",
        results_folder = "M:/AResearch/Gaze_AOI2/Results/",
        )

# JSONs = ["100ms_cutoff.json", "200ms_cutoff.json"]
# CSVs = ["100ms_cutoff.csv", "200ms_cutoff.csv"]
# COs = [100,200]

# for i in range(2):
#     c = GazeAOI(data_folder = "M:/AResearch/Gaze_AOI2/Eye Tracking/",
#             timestamp_folder= "M:/AResearch/Gaze_AOI2/Eye Tracking/Timestamps/",
#             results_folder = "M:/AResearch/Gaze_AOI2/Results/",
#             JSON_out= JSONs[i],
#             CSV_out= CSVs[i],
#             neither_cutoff= COs[i]
#             )