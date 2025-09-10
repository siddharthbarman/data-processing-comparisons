create database ParentChildSample on primary
( 
    name=N'ParentChildSample_Data', 
    filename=N'd:\temp\ParentChildSampleDB.mdf', 
    size=500MB, maxsize=UNLIMITED, filegrowth=10MB
)
log on
( 
    name=N'ParentChildSample_Log', 
    filename=N'd:\temp\ParentChildSampleDB..ldf', 
    size=200MB, maxsize=2GB, filegrowth=16MB 
);

use ParentChildSample;

create table RawData
(
	ParentName varchar(50) not null,
	ChildName varchar(50) null,
	EntryDate datetime not null,
	ExpectedChildrenCount int null,
	ActionType varchar(10) not null
);

create table ProcessedData
(
	ParentName varchar(50) not null,
	ChildName varchar(50) not null,
	EntryDate datetime not null	
);

SET STATISTICS TIME ON;
DBCC DROPCLEANBUFFERS; 
DBCC FREEPROCCACHE;

select A.ParentName, A.ExpectedChildrenCount, B.ChildrenFoundCount from 
(
	select ParentName, ExpectedChildrenCount from RawData where ActionType = 'FirstEntry'
) A
inner join
(
	select ParentName, count(1) as ChildrenFoundCount from ProcessedData
	group by ParentName
) B
on A.ParentName = B.ParentName
-- Total time: 1 sec. CPU time = 2874 ms,  elapsed time = 1102 ms.

select * from RawData r
left outer join ProcessedData p on p.ParentName = r.ParentName and p.ChildName = r.ChildName
where r.ActionType = 'Child' and p.ChildName is null;
-- Total time: 2 sec, CPU time = 9717 ms,  elapsed time = 1778 ms.
-- Server taking up: 17,39,804K. Server started with 3,49,176K


-- Contrain resources
EXEC sp_configure 'show advanced options', 1;
RECONFIGURE;

-- Set maximum server memory (MB)
EXEC sp_configure 'max server memory (MB)', 3072;  -- 3 GB
RECONFIGURE;

SELECT 
    physical_memory_in_use_kb / 1024 AS MemoryUsed_MB,
    large_page_allocations_kb / 1024 AS LargePage_MB,
    locked_page_allocations_kb / 1024 AS LockedPage_MB,
    page_fault_count,
    memory_utilization_percentage,
    available_commit_limit_kb / 1024 AS AvailableCommitLimit_MB,
    process_physical_memory_low,
    process_virtual_memory_low
FROM sys.dm_os_process_memory;

SELECT 
    type AS MemoryClerkType,
    SUM(pages_kb) / 1024 AS MemoryUsed_MB
FROM sys.dm_os_memory_clerks
GROUP BY type
ORDER BY MemoryUsed_MB DESC;


---
-- ==============================================================
-- SQL Server Memory Usage: Buffer Pool vs Outside Buffer Pool
-- ==============================================================

-- 1. Total process memory (matches Task Manager "Working Set")
SELECT 
    physical_memory_in_use_kb / 1024 AS MemoryUsed_MB,
    locked_page_allocations_kb / 1024 AS LockedPages_MB,
    large_page_allocations_kb / 1024 AS LargePages_MB,
    available_commit_limit_kb / 1024 AS AvailableCommitLimit_MB,
    memory_utilization_percentage
FROM sys.dm_os_process_memory;

-- 2. Breakdown by memory clerk
;WITH ClerkUsage AS (
    SELECT 
        type,
        SUM(pages_kb) / 1024 AS MemoryUsed_MB
    FROM sys.dm_os_memory_clerks
    GROUP BY type
)
SELECT 
    CASE 
        WHEN type = 'MEMORYCLERK_SQLBUFFERPOOL' THEN 'Buffer Pool (subject to max server memory)'
        ELSE 'Outside Buffer Pool (NOT capped by max server memory)'
    END AS MemoryCategory,
    type AS ClerkType,
    MemoryUsed_MB
FROM ClerkUsage
ORDER BY MemoryUsed_MB DESC;


---



select count(*) from RawData;
select count(*) from ProcessedData;
truncate table RawData;
