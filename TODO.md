# TODO

- [x] in Jupyter test if we can create a package/view etc by using filter or similar to provide standardized file format (sysml file)
- [x] Button 'Edit SysML Model' 
    - [x] Opens popup frame with sysmlv2 model using user input BUT saves the file path of user when given in previous script runs
    - [x] right side: other buttons and options to do with the sysmlv2 model file
        - functions in the right side:
            - [ ] Add new metadata tag -> name (e.g. that specific domain)
                - [ ]
                - [ ]
            - [ ] Tag elements (parts, attributes etc.) by given metadata tag (User has to select new or existing metadata)
            - [x] Highlight tagged elements by metadata (currently ALL metadata)
                - [x] Write and Connect the file_parser.py Sysml_parser class and functions to the button 
                - [x] Is a Class necessary or should file_parser.py be a utils? 
                - [ ]
            - [ ] Show only tagged elements by selected metadata
            - [ ] Save (versionscontrol)
            - [ ] OPTIONAL Button 'Make current path as default path' (überschreibt die config base paths)
            - [ ]   
            - [ ]   
- [x] Helper Functions REDO and highlight logic ! 
- [ ] Option frame for Map Data 
    - [ ] part, part def, attribute, attribute def mit data verlinken. 
    - [x] data von domain specific file per entry widget verlinken
    - [x] UID für values research
    - [x] mapping datei erschaffen / Template
- [ ]
- [ ]
- [x] UUID (Universally Unique Identifier) for program demonstration only tag mapped elements with uuid  
    - [x] When user selects two elements to map together create for both elements uuids and save them in mapping json
    - [x] Save inside Mapping.json
    - [ ]
- [ ] metadata manager and file parser functions to follow user given paths(generalspecs.size.x)
- [ ] 
- [ ]
- [ ]



