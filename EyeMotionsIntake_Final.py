import numpy as np
import pandas as pd
import os
import itertools
import warnings

warnings.filterwarnings("ignore")

def check_files(data_folder, timestamp_folder):
    """
    Gathers and confirms the existence of all data files in one place for subsequent analysis.

    Parameters
    ----------
    data_folder : The folder containing the raw EyeMotions files
    timestamp_folder : The folder containing the response files formated as per README

    Returns
    -------
    array : a 2 column array containing all raw data files and corresponding response files, respectively.
    """
    data_list = os.listdir(data_folder)
    ts_list = os.listdir(timestamp_folder)
    
    for item in data_list:
        if ".csv" not in item:
            data_list.remove(item)
    
    array = np.empty([len(data_list),2],dtype = object)

    for i,item in enumerate(data_list): #Based on naming scheme outlined in README
        array[i,0] = data_folder+item
        num = str(item.split("CE")[0]) + "CE"
        code = item.split(" ")[2][0].upper()
        
        if code == "A":
            code = "I"
        elif code == "L":
            code = "J"
        else:
            print(f"Error w/ naming for {item}")
    
        for j in ts_list:
            if num in j and code in j:
                array[i,1] = timestamp_folder+j
                break
            if j == (len(ts_list)-1):
                print(f"No Timestamp for {item}")
    return array
    
class Intake():
    def __init__(self, data_file, timestamp_file, neither_cutoff):
        """
        Given an EyeMotions file & corresponding response file calculates the following variables into a dictionary that is exported via self.return_dict():
            
            Timeline^: A list of where a participant looked and for how long
            FirstLook^: The first location a participant looked in a given trial and for how long
            LastLook^: The last location a participant looked in a given trial and for how long
            FirstValid^: Whether or not the participant looked at the Left or Right AOI first and for how long
            LastValid^: Whether or not the participant looked at the Left or Right AOI last and for how long
            Ratios: a 2 item list containing the percent time looking at a certain region (Left, Right, NaN, Neither) and the time spent looking at each AOI, respectively
                    Also contains the total time per trial
            Markov: A nested dictionary containing the raw data (%likelihood of a given movement & number of times a movement happened) necessary to construct a markov chain for every single data point
            Adj_Markov: The same as Markov but for overall eye movements (i.e. does not include a person looking at the same AOI for successive ~5ms data points, only when they change AOIs)
            Nei_Markov: The same as Adj_Markov but ignores "transition neithers"
            TrialError: The percent of a given trial not made up of NaN locations
            ParticipantError*: The percent of a given participant's total data not made of NaN locations
            
            *This variable is processed per participant, whereas all others are nested dictionaries containing data per trial per participant
            ^The data in this variable follows the following format: "{loc}: "x.yzms""
        """
        ID = data_file.split("/")[-1]
        ID = ID.split("CE")[0] +"CE"+ ID.split(" ")[2]
        self.ID = ID
        
        self.err_list = []
        
        df = pd.read_csv(data_file).to_numpy()[:,0]
        for i,j in enumerate(df):  #Finds starting point of relevant data within raw EyeMotions file
            if j == "#DATA":
                break
        i = i+2
        self.data = pd.read_csv(data_file, skiprows = i, usecols=["Timestamp", "Gaze X", "Gaze Y"]).to_numpy()
        self.data = np.hstack((np.arange(self.data.shape[0]).reshape(-1,1),self.data))
        self.IDs = {}  #a dictionary that links the trial number (1,2,3...144) to the row/column identifier (1-4 etc.)
        ID_sheet = pd.read_excel(timestamp_file, sheet_name = 0, usecols = ["Trial", " row", " column"]).to_numpy()

        for row in np.nditer(ID_sheet[1:,:], flags=['external_loop', "refs_ok"], order='C'):
            self.IDs[str(row[0])] = f"{int(row[1])}-{int(row[2])}"
        
        self.times = {}  #start and end times and indices for each trial
        times_sheet = pd.read_excel(timestamp_file, sheet_name = 1, usecols = ["Trial", "Start (seconds)", "End"]).sort_values(by = ["Start (seconds)"]).to_numpy()
        times_sheet = times_sheet[times_sheet[:,0]*0 == 0]
        times_sheet = times_sheet[times_sheet[:,1]*0 == 0]
        
        if self.data[-1,1] > times_sheet[-1,2]*1000:  #It is possible for the tracker to stop recording before the end of a trial, these participants are thrown out
            self.check_err = True
            for row in times_sheet:
                trial_name = self.IDs[str(int(row[0]))]
                
                self.times[trial_name] = {}
                self.times[trial_name]["start"] = row[1]
                self.times[trial_name]["end"] = row[2]
            
            self.trial_list = []
            for i in times_sheet[:,0]:
                self.trial_list.append(str(int(i)))
            overlap = self.find_times()  #Finds the indices of each start and end time
            
            if len(overlap) > 0:  #Overlapping trials are actually removed as part of the self.find_times() function, but are recorded here for user notice
                self.err_list.append(f"{ID} - Overlapping trials ({len(overlap)}):")
                print(f"{ID} contains overlapping trials, continuing with all non overlapping trials")
                for over in overlap:
                    self.err_list.append(f"    - {ID}: {over}")
            
            self.outDict = {ID:{}}  #Since the data is stored as nested dictionaries, the overall categories need to be instantiated before use
            self.outDict[ID]["Timeline"] = {}
            self.outDict[ID]["Raw_Timeline"] = {}
            self.outDict[ID]["LastLook"] = {}
            self.outDict[ID]["FirstLook"] = {}
            self.outDict[ID]["Ratios"] = {}
            self.outDict[ID]["Time_Total"] = {}
            self.outDict[ID]["LastValid"] = {}
            self.outDict[ID]["FirstValid"] = {}
            self.outDict[ID]["Markov"] = {}
            self.outDict[ID]["Adj_Markov"] = {}
            self.outDict[ID]["Nei_Markov"] = {}
            self.outDict[ID]["TrialError"] = {}
            
            errArray = np.zeros([len(self.times),2])
            
            for z,trial in enumerate(self.times):
                self.outDict[ID]["Ratios"][trial] = {}
    
                self.outDict[ID]["Time_Total"][trial] = (self.times[trial]["end"]-self.times[trial]["start"])*1000  #Probably redundant
                self.outDict[ID]["Ratios"][trial]["Total"] = (self.times[trial]["end"]-self.times[trial]["start"])*1000
                
                lookAOI = np.zeros([self.times[trial]["end_i"]-self.times[trial]["start_i"],3])  #Very important temporary array that stores the raw gaze location, the interpolated gaze location, and the time
                
                with np.nditer(self.data[self.times[trial]["start_i"]:self.times[trial]["end_i"],:], flags=['external_loop', 'refs_ok'], order='C') as it:
                    for i,row in enumerate(it):
                        lookAOI[i,0] = self.classify(row[2],row[3])  #Turns coordinates into the AOIs being looked at: Left, Right, Neither, or NaN (Error)
                        self.times[trial]["NaNIndices"] = np.where(lookAOI[:,0] == -1)[0]
                        
                        time_calc = (self.data[int(row[0])+1,1] - self.data[int(row[0])-1,1])/2  #Times and gaze loc are recorded simultaneously, but we technically want the time spent at each loc
                        lookAOI[i,2] = time_calc
                        
                
                lookAOI[:,1] = lookAOI[:,0]
                
                self.outDict[ID]["Raw_Timeline"][trial] = lookAOI  #now referenceable throughout the object, gets deleted upon export      
                
                NaN_remove_list = []
                for i,index in enumerate(self.times[trial]["NaNIndices"]):  #Ignore isolated NaNs, technically an extended period of time could suggest a person intentionally looking away from the screen, but that is unlikely in a single 5ms window
                    if i+1 != len(self.times[trial]["NaNIndices"]):
                        if abs(self.times[trial]["NaNIndices"][i+1]-index) != 1 and abs(self.times[trial]["NaNIndices"][i-1]-index) != 1:
                            self.NaN_replace(ID, trial, self.times[trial]["NaNIndices"][i])
                    else:
                        if abs(self.times[trial]["NaNIndices"][i-1]-index) != 1:
                            self.NaN_replace(ID, trial, self.times[trial]["NaNIndices"][i])
                self.times[trial]["NaN_remove_list"] = NaN_remove_list
                
                #Most of the calculations:
                self.ratios(ID, trial)  #Ratios spent in each AOI per trial plus total trial time
                times2 = self.timeline(ID, trial)  #returns the list as well as adds it to the dictionary
                self.looks(ID, trial)  #The first and last places a participant looked during a trial
                self.markov(ID, trial)  #Data for a Markov Chain
                self.adj_markov(ID, trial, times2)  #Markov Chain that goes on overall looks not individual timestamps (i.e. a person looking at the Left AOI is treated as one instance rather than multiple)
                self.nei_markov(ID, trial, times2, neither_cut= neither_cutoff)  #Same as adj but ignoring Neithers under a certain time, could potentially be just transition time as there is space between the Left and Right AOIs
                
                self.outDict[ID]["TrialError"][trial] = 1 - (lookAOI[:,0] == -1).sum()/np.shape(lookAOI)[0]  #Ratio of data that is not NaN
                errArray[z,0] = (lookAOI[:,0] == -1).sum()
                errArray[z,1] = np.shape(lookAOI)[0]
            
            self.outDict[ID]["ParticipantError"] = 1 - errArray[:,0].sum()/errArray[:,1].sum()
            
        else:  #When a trial is missing data
            self.check_err = False
            print(f"{ID} skipped: missing time")
            self.err_list.append(f"{ID} - Missing Data")
            
        
    def find_times(self):
        #Iterates through each start and end time (in seconds) and converts it to the indices where those times occur in the EyeMotions Data
        start_search = 0
        errs = []
        prev_trial = ""
        for trial in self.trial_list:
            trial_name = self.IDs[trial]
            with np.nditer(self.data[start_search:,:], flags=['external_loop', 'refs_ok'], order='C') as it:
                for row in it:
                    if self.data[start_search][1] > self.times[trial_name]["start"]*1000:
                        errs.append(prev_trial)
                        errs.append(trial_name)
                        
                    if row[1] >= self.times[trial_name]["start"]*1000:
                        self.times[trial_name]["start_i"] = int(row[0])
                        break
                for row in it:
                    if row[1] >= self.times[trial_name]["end"]*1000:
                        self.times[trial_name]["end_i"] = int(row[0])
                        start_search = int(row[0])+1
                        break
            prev_trial = trial_name
        
        ret_errs = []
        for i in errs:
            if i not in ret_errs:
                ret_errs.append(i)
                del self.times[i]
        return ret_errs
    
    
    def classify(self, x, y):
        #Change this if your AOIs change
        if x*0!=0 or y*0!=0:
            check = -1
        else:
            check = 0
            if y > 330 and y < 750:
                if x > 200 and x < 820:
                    check = 1
                if x > 1100 and x < 1720:
                    check = 2
        return check
    
    def number_decode(self,val):
        if val == 0:
            return "Neither"
        if val == 1:
            return "Left"
        if val == 2:
            return "Right"
        if val == -1:
            return "NaN"
    
    def NaN_replace(self,ID, trial, index):
        #Replace the NaN loc with either the loc of the instance immediately before or after it
        try:
            self.outDict[ID]["Raw_Timeline"][trial][index,1] = self.outDict[ID]["Raw_Timeline"][trial][index-1,0]
        except:
            self.outDict[ID]["Raw_Timeline"][trial][index,1] = self.outDict[ID]["Raw_Timeline"][trial][index+1,0]
    
    def ratios(self, ID, trial):
        #Sums instances of each and then divides by the total number of instances
        self.outDict[ID]["Ratios"][trial]["L"] = [None,None]
        self.outDict[ID]["Ratios"][trial]["R"] = [None,None]
        self.outDict[ID]["Ratios"][trial]["NaN"] = [None,None]
        self.outDict[ID]["Ratios"][trial]["Neither"] = [None,None]
        
        L_temp = sum(self.outDict[ID]["Raw_Timeline"][trial][self.outDict[ID]["Raw_Timeline"][trial][:,1] == 1][:,2])
        R_temp = sum(self.outDict[ID]["Raw_Timeline"][trial][self.outDict[ID]["Raw_Timeline"][trial][:,1] == 2][:,2])
        NaN_temp = sum(self.outDict[ID]["Raw_Timeline"][trial][self.outDict[ID]["Raw_Timeline"][trial][:,1] == -1][:,2])
        Nei_temp = sum(self.outDict[ID]["Raw_Timeline"][trial][self.outDict[ID]["Raw_Timeline"][trial][:,1] == 0][:,2])
        total_temp = L_temp + R_temp + NaN_temp + Nei_temp

        self.outDict[ID]["Ratios"][trial]["L"][1] = L_temp
        self.outDict[ID]["Ratios"][trial]["R"][1] = R_temp
        self.outDict[ID]["Ratios"][trial]["NaN"][1] = NaN_temp
        self.outDict[ID]["Ratios"][trial]["Neither"][1] = Nei_temp
        
        self.outDict[ID]["Ratios"][trial]["L"][0] = L_temp/total_temp
        self.outDict[ID]["Ratios"][trial]["R"][0] = R_temp/total_temp
        self.outDict[ID]["Ratios"][trial]["NaN"][0] = NaN_temp/total_temp
        self.outDict[ID]["Ratios"][trial]["Neither"][0] = Nei_temp/total_temp
        
    def timeline(self, ID, trial):
        #Converts each row of LookAOI to a more easily digestible string, combines a series of instances in the same AOI into one instance (i.e. 3 5ms instances at Left -> 15 ms at Left)
        temp_df = self.outDict[ID]["Raw_Timeline"][trial][:,1:]
        temp_code = temp_df[0,0]
        temp_time = temp_df[0,1]
        temp_list = []
        
        with np.nditer(temp_df[1:,:], flags=['external_loop', 'refs_ok'], order='C') as it:
            for row in it:
                if row[0] != temp_code:
                    temp_list.append(f"{self.number_decode(temp_code)}: {temp_time}ms")
                    temp_code = row[0]
                    temp_time = row[1]
                else:
                    temp_time += row[1]    
                    
        if temp_code == temp_df[-1,0]:
                    temp_list.append(f"{self.number_decode(temp_code)}: {temp_time}ms")

        self.outDict[ID]["Timeline"][trial] = temp_list
        return temp_list
    
    def looks(self, ID, trial):
        self.outDict[ID]["FirstLook"][trial] = self.outDict[ID]["Timeline"][trial][0]
        self.outDict[ID]["LastLook"][trial] = self.outDict[ID]["Timeline"][trial][-1]
        self.outDict[ID]["FirstValid"][trial] = "err"
        self.outDict[ID]["LastValid"][trial] = "err"
        
        for entry in self.outDict[ID]["Timeline"][trial]:
            if "NaN" not in entry and "Neither" not in entry:
                self.outDict[ID]["FirstValid"][trial] = entry
                break
        for i in range(-1, -(len(self.outDict[ID]["Timeline"][trial])+1), -1):
            entry = self.outDict[ID]["Timeline"][trial][i]
            if "NaN" not in entry and "Neither" not in entry:
                self.outDict[ID]["LastValid"][trial] = entry
                break
    
    
    def markov(self, ID, trial):
        #This and all subsequent Markov calculations work by finding the start and end point of a transition and using them as indices.  These changes are summed up before being divided by the total number of transitions
        self.outDict[ID]["Markov"][trial] = {"Left":{"Left":[0,0], "Right":[0,0], "NaN":[0,0],"Neither":[0,0]},
                                                       "Right":{"Left":[0,0], "Right":[0,0], "NaN":[0,0],"Neither":[0,0]},
                                                       "NaN":{"Left":[0,0], "Right":[0,0], "NaN":[0,0],"Neither":[0,0]},
                                                       "Neither":{"Left":[0,0], "Right":[0,0], "NaN":[0,0],"Neither":[0,0]}}
        
        temp_df = self.outDict[ID]["Raw_Timeline"][trial][:,1:]
        with np.nditer(temp_df, flags=['external_loop', 'refs_ok'], order='C') as it:
            for i,row in enumerate(itertools.islice(it, (len(temp_df)-1))):
                self.outDict[ID]["Markov"][trial][self.number_decode(row[0])][self.number_decode(temp_df[i+1,0])][1] += 1

        for a in ["Left","Right","Neither","NaN"]:
            for b in ["Left","Right","Neither","NaN"]:
                self.outDict[ID]["Markov"][trial][a][b][0] = self.outDict[ID]["Markov"][trial][a][b][1]/np.nansum(a = [self.outDict[ID]["Markov"][trial][a]["Left"][1],
                                                                                                                                          self.outDict[ID]["Markov"][trial][a]["Right"][1],
                                                                                                                                       self.outDict[ID]["Markov"][trial][a]["NaN"][1],
                                                                                                                                          self.outDict[ID]["Markov"][trial][a]["Neither"][1]])
    
    def adj_markov(self, ID, trial, times):
        #Uses the condensed timeline rather than the more extensive LookAOI array
        self.outDict[ID]["Adj_Markov"][trial] = {"Left":{"Left":[0,0], "Right":[0,0], "NaN":[0,0],"Neither":[0,0]},
                                                       "Right":{"Left":[0,0], "Right":[0,0], "NaN":[0,0],"Neither":[0,0]},
                                                       "NaN":{"Left":[0,0], "Right":[0,0], "NaN":[0,0],"Neither":[0,0]},
                                                       "Neither":{"Left":[0,0], "Right":[0,0], "NaN":[0,0],"Neither":[0,0]}}
        
        for i,entry in enumerate(times[:-1]):
            first = entry.split(": ")[0]
            second = times[i+1].split(": ")[0]                        
            self.outDict[ID]["Adj_Markov"][trial][first][second][1] += 1
        
        for a in ["Left","Right","Neither","NaN"]:
            for b in ["Left","Right","Neither","NaN"]:
                self.outDict[ID]["Adj_Markov"][trial][a][b][0] = self.outDict[ID]["Adj_Markov"][trial][a][b][1]/np.nansum(a = [self.outDict[ID]["Adj_Markov"][trial][a]["Left"][1],
                                                                                                                                          self.outDict[ID]["Adj_Markov"][trial][a]["Right"][1],
                                                                                                                                       self.outDict[ID]["Adj_Markov"][trial][a]["NaN"][1],
                                                                                                                                          self.outDict[ID]["Adj_Markov"][trial][a]["Neither"][1]])
    
    def nei_markov(self, ID, trial, times, neither_cut = 100):
        self.outDict[ID]["Nei_Markov"][trial] = {"Left":{"Left":[0,0], "Right":[0,0], "NaN":[0,0],"Neither":[0,0]},
                                                       "Right":{"Left":[0,0], "Right":[0,0], "NaN":[0,0],"Neither":[0,0]},
                                                       "NaN":{"Left":[0,0], "Right":[0,0], "NaN":[0,0],"Neither":[0,0]},
                                                       "Neither":{"Left":[0,0], "Right":[0,0], "NaN":[0,0],"Neither":[0,0]}}
        
        i = 0
        while i < (len(times)-1):
            first = times[i].split(": ")[0]
            second = times[i+1].split(": ")[0]
            temp_time = float(times[i+1].split(": ")[1][:-2])
            
            i+=1
            
            if "Nei" in second and temp_time < 100 and i != 0 and i < len(times)-1:
                if "Left" in times[i-1] and "Right" in times[i+1]:
                    i += 1
                    second = times[i].split(": ")[0]
                elif "Right" in times[i-1] and "Left" in times[i+1]:
                    i += 1
                    second = times[i].split(": ")[0]
            
            self.outDict[ID]["Nei_Markov"][trial][first][second][1] += 1
                
        for a in ["Left","Right","Neither","NaN"]:
            for b in ["Left","Right","Neither","NaN"]:
                self.outDict[ID]["Nei_Markov"][trial][a][b][0] = self.outDict[ID]["Nei_Markov"][trial][a][b][1]/np.nansum(a = [self.outDict[ID]["Nei_Markov"][trial][a]["Left"][1],
                                                                                                                                          self.outDict[ID]["Nei_Markov"][trial][a]["Right"][1],
                                                                                                                                       self.outDict[ID]["Nei_Markov"][trial][a]["NaN"][1],
                                                                                                                                          self.outDict[ID]["Nei_Markov"][trial][a]["Neither"][1]])
    
    def return_dict(self):
        del self.outDict[self.ID]["Raw_Timeline"]  #Raw_Timeline is both redundant and also not exportable as a .json b/c it's a 2D array
        return self.outDict