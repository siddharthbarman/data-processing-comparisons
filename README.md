# Overview
Compare data processing performance across various technologies.

# Tools

## generate_raw.py
This program generates a csv file containing records with the following fields:
- ParentName (string, may be null)
- ChildName (string)
- EntryTime (datetime)
- ExpectedChildrenCount (int, may be null)
- ActionType (string, possible values: FirstEntry, ChildCount, Child)

The 'Action' field determines how to interpret the record:
Command:
```
python generate_raw.py rawdata.csv 5000 1000
```
Total execution time seen was: 22944.802 ms.

| Value      | Description                                                              |
| ---------- | ------------------------------------------------------------------------ |
| FirstEntry | Entry for the parent. Child count is till unknown.                       |
| ChildCount | Entry for a parent record sent earlier. Update the ExpectedChildrenCount.|
| Child      | Entry for a child record, the ParentFilename field will also be present. |

The program refers to a parents.csv file for a list of unique Parent names.
The output is stored in a rawdata.csv file.

Command:
```
python generate_raw.py rawdata.csv 5000 1000
```

## copyraw.bat
This program uses the bcp utility to insert the raw csv entries into the RawData table.

5005000 records were copied in 13.172 seconds.

## generate_processed.py
This program reads the rawdata.csv to generate a CSV file named 'available.csv'  which has the following columns:
- Child (string)
- Parent (string)
- EntryDate (datetime)

Command:
```
python generate_processed.py processed.csv 5000 1000
```

## copyprocessed.bat
This program copies CSV records into the ProcessedData table. 
5000000 rows copied in 10.031 seconds.


## pandas_processor.py
- This program reads the 'rawdata.csv' file & the 'available.csv' files. 
- It creates a parent dataset from the data present in the 'rawdata.csv' by extracing the parent information for rows having Action = 'FirstEntry' and a child dataset containing all the child records.
- It then updates the dataset with the ExpectedChildCount for each parent by extracting rows where the Action = 'ChildCount'
- It then reads all rows from the 'available.csv' files and updates the rows in the child dataset with Found = 1 if the child was found in the available.csv.
- It adds up all the children where Found = 1 and updates the ChildrenFoundCount field of the parent dataset.
- It stores the parent dataset and the child dataset. 

It counts the number of children per parent in the available.csv and matches it with the 'ExpectedChildCount' field present in the 

Command:
```
python pandas_processor.py ..\generate_raw\rawdata.csv ..\generate_processed\processed.csv
```

# Observations

## Pandas
Running the pandas_processor.py which essentially executes the same logic i.e.:
1. Loading the csv datasets
   - rawdata.csv (312 MBs)
   - rawdata.csv (277 MBs)
2. Filtering the raw records for ActionType = "First" & extract the "ParentName" and "ExpectedChildrenCount" fields.
3. Grouping records in the processes csv by ParentName and counting the number children.
4. Joining '2' and '3'
5. Listing raw records where ActionType = "Child" which do not exist in the processed csv records.

Executing all the steps took 5.4 seconds & consumed 1.600 GB of memory. 

## SQL Server
The following steps are involved in getting the results from SQL Server:

1. Loading the rawdata.csv file into RawData table using BCP. 5005000 records were copied in 13.172 seconds.
2. Loading the processed_data.csv file into the ProcessedData.csv table using BCP. 5000000 rows copied in 10.031 seconds.
3. Query for extracting the "ParentName" & "ExpectedChildrenCount" fields from RawData table where ActionType = 'FirstEntry' along with joining with the query which groups the records in ProcessedData table by ParentName took 1 sec.
4. Query for selecting those records in RawData where ActionType='Child' but not exist in the ProcessedRecord table took 2 seconds to execute.

Total time taken including data loading from the two csv was: 26.20 seconds and Task Manager reported SQLSVR consuming 16 GB of memory.

# Summary
The result are summarized as follows:

| Test       | Time taken (sec) | Memory consumed (GBs) |
| ---------- | ---------------- | --------------------- |
| Pandas     |              5.4 |                   1.6 |
| SQL Server |            26.20 |                    16 |

# References
<a href="https://github.com/siddharthbarman/data-processing-comparisons">The sample code on Github</a>