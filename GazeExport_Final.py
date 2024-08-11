import pandas as pd
import numpy as np

def gazeExport(data, CSV_out):
    """
    Converts all of the relevant JSON data to a CSV format for subsequent analysis via transcribing the data to a simplified dictionary -> dataframe

    Parameters
    ----------
    data : A dictionary containing all of the outlined data (as per EyeMotionsIntake_Final.py)
    CSV_out : The name of the file where the data should be written to
    """
    participants = list(data.keys())
    #COLUMNS
    out_template = {
        "Participant": [],
        "Letter_Code": [],
        
        "Row": [],
        "Column": [],
        
        "First_Look": [],
        "First_Look_Time": [],
        "First_Valid_Look": [],
        "First_Valid_Look_Time": [],
        "Last_Look":[],
        "Last_Look_Time": [],
        "Last_Valid_Look": [],
        "Last_Valid_Look_Time":[],
        
        "Total_Time": [],
        "%L": [],
        "L_Time": [],
        "%R": [],
        "R_Time": [],
        "%NaN": [],
        "NaN_Time": [],
        "%Neither": [],
        "Neither_Time": [],
        
        "L_to_L": [],
        "L_to_R": [],
        "L_to_NaN": [],
        "L_to_Neither": [],
        
        "R_to_L": [],
        "R_to_R": [],
        "R_to_NaN": [],
        "R_to_Neither": [],
        
        "NaN_to_L": [],
        "NaN_to_R": [],
        "NaN_to_NaN": [],
        "NaN_to_Neither": [],
        
        "Neither_to_L": [],
        "Neither_to_R": [],
        "Neither_to_NaN": [],
        "Neither_to_Neither": [],
        
        ####
        
        "Adj_L_to_L": [],
        "Adj_L_to_R": [],
        "Adj_L_to_NaN": [],
        "Adj_L_to_Neither": [],
        
        "Adj_R_to_L": [],
        "Adj_R_to_R": [],
        "Adj_R_to_NaN": [],
        "Adj_R_to_Neither": [],
        
        "Adj_NaN_to_L": [],
        "Adj_NaN_to_R": [],
        "Adj_NaN_to_NaN": [],
        "Adj_NaN_to_Neither": [],
        
        "Adj_Neither_to_L": [],
        "Adj_Neither_to_R": [],
        "Adj_Neither_to_NaN": [],
        "Adj_Neither_to_Neither": [],
        
        ####
        
        "Nei_L_to_L": [],
        "Nei_L_to_R": [],
        "Nei_L_to_NaN": [],
        "Nei_L_to_Neither": [],
        
        "Nei_R_to_L": [],
        "Nei_R_to_R": [],
        "Nei_R_to_NaN": [],
        "Nei_R_to_Neither": [],
        
        "Nei_NaN_to_L": [],
        "Nei_NaN_to_R": [],
        "Nei_NaN_to_NaN": [],
        "Nei_NaN_to_Neither": [],
        
        "Nei_Neither_to_L": [],
        "Nei_Neither_to_R": [],
        "Nei_Neither_to_NaN": [],
        "Nei_Neither_to_Neither": [],
        
        "Participant_NaN_Ratio": [],
        "Trial_NaN_Ratio": []
        }
    
    for i,participant in enumerate(participants):
        trials = data[participant]["TrialError"].keys()
        for trial in trials:
            out_template["Participant"].append(participant.split("CE")[0])
            
            if "Arrow" in participant:
                out_template["Letter_Code"].append("A")
            elif "Letter" in participant:
                out_template["Letter_Code"].append("L")
            else:
                return 0
        
            out_template["Row"].append(trial.split("-")[0])
            out_template["Column"].append(trial.split("-")[1])
            
            out_template["First_Look"].append(data[participant]["FirstLook"][trial].split(": ")[0])
            out_template["First_Look_Time"].append(data[participant]["FirstLook"][trial].split(": ")[1][:-2])
            out_template["Last_Look"].append(data[participant]["LastLook"][trial].split(": ")[0])
            out_template["Last_Look_Time"].append(data[participant]["LastLook"][trial].split(": ")[1][:-2])
            
            if data[participant]["FirstValid"][trial] != "err":
                out_template["First_Valid_Look"].append(data[participant]["FirstValid"][trial].split(": ")[0])
                out_template["First_Valid_Look_Time"].append(data[participant]["FirstValid"][trial].split(": ")[1][:-2])
            else:
                out_template["First_Valid_Look"].append(np.nan)
                out_template["First_Valid_Look_Time"].append(np.nan)
            if data[participant]["LastValid"][trial] != "err":
                out_template["Last_Valid_Look"].append(data[participant]["LastValid"][trial].split(": ")[0])
                out_template["Last_Valid_Look_Time"].append(data[participant]["LastValid"][trial].split(": ")[1][:-2])
            else:
                out_template["Last_Valid_Look"].append(np.nan)
                out_template["Last_Valid_Look_Time"].append(np.nan)
                
            out_template["Total_Time"].append(data[participant]["Ratios"][trial]["Total"])
            out_template["%L"].append(data[participant]["Ratios"][trial]["L"][0])
            out_template["L_Time"].append(data[participant]["Ratios"][trial]["L"][1])
            out_template["%R"].append(data[participant]["Ratios"][trial]["R"][0])
            out_template["R_Time"].append(data[participant]["Ratios"][trial]["R"][1])
            out_template["%NaN"].append(data[participant]["Ratios"][trial]["NaN"][0])
            out_template["NaN_Time"].append(data[participant]["Ratios"][trial]["NaN"][1])
            out_template["%Neither"].append(data[participant]["Ratios"][trial]["Neither"][0])
            out_template["Neither_Time"].append(data[participant]["Ratios"][trial]["Neither"][1])
            
            out_template["L_to_L"].append(data[participant]["Markov"][trial]["Left"]["Left"][0])
            out_template["L_to_R"].append(data[participant]["Markov"][trial]["Left"]["Right"][0])
            out_template["L_to_NaN"].append(data[participant]["Markov"][trial]["Left"]["NaN"][0])
            out_template["L_to_Neither"].append(data[participant]["Markov"][trial]["Left"]["Neither"][0])
            
            out_template["R_to_L"].append(data[participant]["Markov"][trial]["Right"]["Left"][0])
            out_template["R_to_R"].append(data[participant]["Markov"][trial]["Right"]["Right"][0])
            out_template["R_to_NaN"].append(data[participant]["Markov"][trial]["Right"]["NaN"][0])
            out_template["R_to_Neither"].append(data[participant]["Markov"][trial]["Right"]["Neither"][0])
            
            out_template["NaN_to_L"].append(data[participant]["Markov"][trial]["NaN"]["Left"][0])
            out_template["NaN_to_R"].append(data[participant]["Markov"][trial]["NaN"]["Right"][0])
            out_template["NaN_to_NaN"].append(data[participant]["Markov"][trial]["NaN"]["NaN"][0])
            out_template["NaN_to_Neither"].append(data[participant]["Markov"][trial]["NaN"]["Neither"][0])
            
            out_template["Neither_to_L"].append(data[participant]["Markov"][trial]["Neither"]["Left"][0])
            out_template["Neither_to_R"].append(data[participant]["Markov"][trial]["Neither"]["Right"][0])
            out_template["Neither_to_NaN"].append(data[participant]["Markov"][trial]["Neither"]["NaN"][0])
            out_template["Neither_to_Neither"].append(data[participant]["Markov"][trial]["Neither"]["Neither"][0])
            
            
            out_template["Adj_L_to_L"].append(data[participant]["Adj_Markov"][trial]["Left"]["Left"][0])
            out_template["Adj_L_to_R"].append(data[participant]["Adj_Markov"][trial]["Left"]["Right"][0])
            out_template["Adj_L_to_NaN"].append(data[participant]["Adj_Markov"][trial]["Left"]["NaN"][0])
            out_template["Adj_L_to_Neither"].append(data[participant]["Adj_Markov"][trial]["Left"]["Neither"][0])
            
            out_template["Adj_R_to_L"].append(data[participant]["Adj_Markov"][trial]["Right"]["Left"][0])
            out_template["Adj_R_to_R"].append(data[participant]["Adj_Markov"][trial]["Right"]["Right"][0])
            out_template["Adj_R_to_NaN"].append(data[participant]["Adj_Markov"][trial]["Right"]["NaN"][0])
            out_template["Adj_R_to_Neither"].append(data[participant]["Adj_Markov"][trial]["Right"]["Neither"][0])
            
            out_template["Adj_NaN_to_L"].append(data[participant]["Adj_Markov"][trial]["NaN"]["Left"][0])
            out_template["Adj_NaN_to_R"].append(data[participant]["Adj_Markov"][trial]["NaN"]["Right"][0])
            out_template["Adj_NaN_to_NaN"].append(data[participant]["Adj_Markov"][trial]["NaN"]["NaN"][0])
            out_template["Adj_NaN_to_Neither"].append(data[participant]["Adj_Markov"][trial]["NaN"]["Neither"][0])
            
            out_template["Adj_Neither_to_L"].append(data[participant]["Adj_Markov"][trial]["Neither"]["Left"][0])
            out_template["Adj_Neither_to_R"].append(data[participant]["Adj_Markov"][trial]["Neither"]["Right"][0])
            out_template["Adj_Neither_to_NaN"].append(data[participant]["Adj_Markov"][trial]["Neither"]["NaN"][0])
            out_template["Adj_Neither_to_Neither"].append(data[participant]["Adj_Markov"][trial]["Neither"]["Neither"][0])
            
            
            out_template["Nei_L_to_L"].append(data[participant]["Nei_Markov"][trial]["Left"]["Left"][0])
            out_template["Nei_L_to_R"].append(data[participant]["Nei_Markov"][trial]["Left"]["Right"][0])
            out_template["Nei_L_to_NaN"].append(data[participant]["Nei_Markov"][trial]["Left"]["NaN"][0])
            out_template["Nei_L_to_Neither"].append(data[participant]["Nei_Markov"][trial]["Left"]["Neither"][0])
            
            out_template["Nei_R_to_L"].append(data[participant]["Nei_Markov"][trial]["Right"]["Left"][0])
            out_template["Nei_R_to_R"].append(data[participant]["Nei_Markov"][trial]["Right"]["Right"][0])
            out_template["Nei_R_to_NaN"].append(data[participant]["Nei_Markov"][trial]["Right"]["NaN"][0])
            out_template["Nei_R_to_Neither"].append(data[participant]["Nei_Markov"][trial]["Right"]["Neither"][0])
            
            out_template["Nei_NaN_to_L"].append(data[participant]["Nei_Markov"][trial]["NaN"]["Left"][0])
            out_template["Nei_NaN_to_R"].append(data[participant]["Nei_Markov"][trial]["NaN"]["Right"][0])
            out_template["Nei_NaN_to_NaN"].append(data[participant]["Nei_Markov"][trial]["NaN"]["NaN"][0])
            out_template["Nei_NaN_to_Neither"].append(data[participant]["Nei_Markov"][trial]["NaN"]["Neither"][0])
            
            out_template["Nei_Neither_to_L"].append(data[participant]["Nei_Markov"][trial]["Neither"]["Left"][0])
            out_template["Nei_Neither_to_R"].append(data[participant]["Nei_Markov"][trial]["Neither"]["Right"][0])
            out_template["Nei_Neither_to_NaN"].append(data[participant]["Nei_Markov"][trial]["Neither"]["NaN"][0])
            out_template["Nei_Neither_to_Neither"].append(data[participant]["Nei_Markov"][trial]["Neither"]["Neither"][0])
            
            out_template["Participant_NaN_Ratio"].append(data[participant]["ParticipantError"])
            out_template["Trial_NaN_Ratio"].append(data[participant]["TrialError"][trial])
    
    result = pd.DataFrame(data = out_template)
    result.to_csv(CSV_out, index = False)
    
