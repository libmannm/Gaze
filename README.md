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
- timestamp_folder
  - Naming: Should all be .xlsx with the naming scheme "{participant number}CE{letter code}_Resps_Scenes.xlsx" i.e. 4CEJ_Resps_Scenes.xlsx
  - File characteristics:
    - Should be an Excel workbook containing two sheets.  The first should be titled "Resps" and the second should be titled "Times"
    - Resps: Should be a large array with notable columns "Trial", "row, and "column"
    - Times: An array with fewer columns including "Trial", "Start (seconds)", and "End"

## Script Output
The script will output 3 files: two files of processed data (a .csv and a .json) and a .txt that tracks any errors throughout the processing pipeline.  By default, these files are all named as derivatives of the date the script was run, so it is recommended to provide the script with alternative specific names if you plan on running the script multiple times on a given day.

- .csv Results
  - The .csv output is the most reduced form of the data.  Aside from identifiers, the data contained in the CSV can best be grouped into the first and last AOIs looked at, the proportion of time spent in each AOI, and the data required to construct a Markov chain.  There are a variety of permutations to each of these result groups.
  - Notable columns/column naming:
    - "Valid": When used in a column heading, the term Valid refers to the first instance of the given requirement when the participant was not looking at Neither or NaN (and was looking at L or R)
    - "Adj": When describing the Markov chain columns, Adj refers to the Markov chain data where a recorded event consists of a participant looking to a new AOI rather than over the standard 5ms time intervals
    - "Nei": The Nei Markov chain data is similar to the Adj data, but Neither periods where the participant is transitioning between L and R that are shorter than a given time are filtered out as potential byproducts of there being a gap between the AOIs
- .json Results
  - In addition to the data required for the .csv, the .json notably contains a "Timeline" subkey, which shows the overall progression of where a participant looked throughout a trial.
  - The dictionary is generally structured as follows: "Participant + Arrow or Letter" : {data category: {trial : data}}}
- .txt Errors
  - A simple list of each missing participant/trial and the reason for exclusion (i.e. missing timestamp data, missing data file, or both)
 
## Running the Script
From this repository, it should only be necessary to interact with the script "GazeAOI_Final.py".  Once all variables and folder paths are defined in GazeAOI_Final.py, it will call all necessary classes and functions from the other scripts.  It is important though to ensure that all scripts are available to your environment.  This can usually be done by simply keeping all scripts in the same folder.  This script is intended to be run in an IDE rather than on a command line. However, it is well structured for adaptation to a callable script if it fits your needs.

<ins>General Process</ins>

1. For each participant, find relevant information such as the start and end point of a trial as well as the relevant subset of the EyeMotions data
2. Calculate the AOI the person is focusing on at every point in time
3. From these data subsets, calculate all relevant statistics (First looks, Ratios, Markov chains, etc.)
4. Convert .json data to a .csv


