# SysMLv2-API
Source Code and Documentation of SysMLv2 API to other engineering domain models

To generate requirements.txt : "pip freeze > requirements.txt" OR CONDA: "conda list --export > requirements.txt"
After cloning git repo to local: Install python requirements: pip install -r requirements.txt
To install and activate virtual environment:
            "To create a venv, run: 'python -m venv your_env_name'\n"
            "To activate (Windows): 'your_env_name\\Scripts\\activate'\n"
            "To activate (Linux/macOS): 'source your_env_name/bin/activate'\n"
            "To create a Conda env, run: 'conda create --name your_env_name python=3.x'\n"
            "To activate Conda env: 'conda activate your_env_name'


- 'config/': Contains default config files. 

- 'utils/': Contains helper functions for standardized methods that are be used frequently.

- 'main.py': Starting point of the application with GUI logic, API and Data Management classes

- 'file_parser.py' : Contains all file parser classes (one for each file format). Some have additional writing to mapping.json due to extending information inside the mapping e.g. index from STEP

- 'metadata_manager.py': Manages metadata between SysMLv2 and domain models with mapping.json. Creates mapping.json template and checks values if they're changing inside domain files to update mapping and sysml model file

## Unit Tests and Validation
- python -m unittest tests/test_mapping.py
