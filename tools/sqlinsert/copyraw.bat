set STARTTIME=%TIME%
bcp ParentChildSample.dbo.RawData in "..\generate_raw\rawdata.csv"  -c -t, -F 2 -b 10000 -h "TABLOCK" -S localhost -U sa -P password123
set STOPTIME=%TIME%
echo Started at: %STARTTIME%, completed at: %STOPTIME%