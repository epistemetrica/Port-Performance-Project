# Port Performance Index Project

This [repo](https://github.com/epistemetrica/Port-Performance-Project) represents the data work related to the [WSU TRG's](https://ses.wsu.edu/trg/) Port Performance Index project. The project is led by Hanouf Alhunayshil with support from Jake Wagner and Adam Wilson.

## Project Description

The TRG is building a port performance index for US maritime freight ports along with a database of port activity over time, including vessel and cargo throughput, various efficiency measures, and other economic indicators. 

## Data

Data for this project come from various sources, including:

- Vessel position, indentification, and status data from the [NOAA/BOEM/USCG Marine Cadastre](https://hub.marinecadastre.gov/pages/about) AIS database. 
- [Port locations](https://geodata.bts.gov/datasets/usdot::principal-ports/explore?location=20.769635%2C73.193702%2C2.00) from the Bureau of Transportation Statistics. 
- [Dock and anchorage](https://geospatial-usace.opendata.arcgis.com/datasets/0f4b16ba76e542e888343907eba91aea_0/explore?location=47.571978%2C-122.325576%2C12.73) locations and descriptions from the US Army Corp of Engineers.

NOTE Data files are note stored on the repo. 

## Files

The main repo folder contains this README, along with ...

## Python

Data processing and exploratory analysis are done mainly in Jupyter (5.5) notebooks with Python 3.12. 

Streaming?

Web dashboards...

The following libraries are used:
- numpy 1.26.2
- pandas 2.1.3
- polars 1.1.0
- scipy 1.11.4