# Gaze

Developed as part of TK, this series of scripts processes a combination of raw data from an EyeMotions tracker and defined experimental parameters to output data for later statistical analysis. In particular, these scripts track pupil movement throughout a series of tasks and output data such as Markov chains and the proportion of time spent looking at certain AOIs. While these scripts were designed for a specific task, the modules and methods may be more broadly applicable.

## Prerequisite Folder Organization & Input Format

The script requires the existence of 3 designated folders containing the EyeMotions data (data_folder), the trial parameter data (timestamp_folder), and eventually the results (results_folder).  These folders do not need to be in a particular order (no required nesting etc.).  As a result, it may be helpful to define folders in the script with global paths.  Having the 2 data folders contain only their respective files is also recommended. 

<ins>Folder Contents</ins>
- data_folder/EyeMotions
  - Naming: Should all be .csv files with the naming scheme "{index number}_{participant number}CE {Letter or Arrow} {mm-dd-yy} {hours}h{minutes}m.csv" i.e. 001_109CE Letter 03-08-22 14h22m.csv
  - File characteristics:
    - The file should contain approximately 30 lines of header ending with the line "#DATA"
    - Among others, the file should contain the columns "Timestamp", "ET_PupilLeft", and "ET_PupilRight" in the row immediately under "#DATA"
    - 
