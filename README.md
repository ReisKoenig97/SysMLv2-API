# SysMLv2-API
Source Code and Documentation of SysMLv2 API to other engineering domain models

After cloning git repo to local: Install python requirements: pip install -r requirements.txt

- 'config/': Contains default config files. 

- 'utils/': Contains helper functions for standardized methods that are be used frequently.

- 'main.py': Starting point of the application with GUI logic, API and Data Management classes

- 'file_parser.py' : Contains all file parser classes (one for each file format). Some have additional writing to mapping.json due to extending information inside the mapping e.g. index from STEP

- 'metadata_manager.py': Manages metadata between SysMLv2 and domain models with mapping.json. Creates mapping.json template and checks values if they're changing inside domain files to update mapping and sysml model file