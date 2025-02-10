import git # external library gitpython
from git import Repo 
import os
from utils.json_utils import load_json
import logging

class VersionControl:
    """
    A class to handle version control using Git for a specified repository.
    
    This class provides functionality to stage, commit, and push files based on 
    a mapping file. It is designed to ensure that only the relevant files are tracked 
    and versioned, promoting efficient and clear version control.

    Attributes:
        repo_path : String. The path to the Git repository.
        mapping_path : String. The path to the mapping.json file that defines files to version.
        repo : (git.Repo). The Git repository object for performing Git operations.
    """

    def __init__(self, config, mapping_path=None, repo_path=None):
        """
        Initializes the VersionControl class with the repository path and mapping file path.

        Parameters:
            repo_path (str): The path to the Git repository.
            mapping_path (str): Path to the mapping.json file.
        """
        self.logger = logging.getLogger(__name__)
        #MacOS: /Users/reiskoenig/Nextcloud/MASTER ARBEIT/Code
        #Windows: "C:\Users\tommy\Nextcloud\MASTER ARBEIT\Code\SysMLv2 API Code"
        self.config = config
        self.repo_path = self.config["repo_path"] #r"C:\Users\tommy\Nextcloud\MASTER ARBEIT\Code\SysMLv2 API Code" #absolute path to the git folder 
        self.mapping_path = mapping_path 
        self.repo = git.Repo(repo_path)

        self.branch_name = "automated-commits"

        try:
            self.repo = git.Repo(self.repo_path)
            self.logger.info(f"Successfully loaded Git repository: {self.repo_path}")
        except Exception as e:
            self.logger.error(f"Error loading the repository: {e}")
            raise

        self.logger.debug("VersionControl initialized.")
        

    def load_commit_history_from_file_path(self, file_path, treeview_widget):
        """Loads git commits from file path of the treeview widget and displays it inside given treeview_widget
        (Versionframe inside optionsframe)

        Parameters: 
            file_path : String. Contains file path to get the commit history from git. 
            text_widget : (tk) Text Widget. tkinter widget to fill information in string format.
        
        Returns: 
            treeview_widget updated/filled with git commits 
        """ 
        self.logger.debug(f"Loading commits from file path: {file_path}")
        # Calling git commands to get the commit history of the specific file (user given file path)
        
        try: 
            repo = Repo(self.repo_path) 
            self.logger.debug(f"repo: {repo}") 
            relative_path = os.path.relpath(file_path, self.repo_path) 
            self.logger.debug(f"relative path: {relative_path}") 
             # Letzter Commit-Hash (HEAD) 
            latest_commit_hash = repo.head.commit.hexsha 
            
            # Alle Commits für die Datei abrufen 
            for commit in repo.iter_commits(paths=relative_path): 
                if commit.hexsha == latest_commit_hash: 
                    continue  # skip latest commit 
                self.logger.debug(f"current commit: {commit}")
                commit_hash = commit.hexsha[:7] # only show the first 7 Hash numbers 
                message = commit.message.splitlines()[0]
                date = commit.committed_datetime.strftime('%Y-%m-%d %H:%M:%S')
                treeview_widget.insert("", "end", values=(commit_hash, message, date))
        except Exception as e: 
            self.logger.error(f"Failed to load commits: {e}")

    def get_diff_with_specific_commit(self, file_path, commit_hash):
        """
        Fetches the git diff between the selected commit and the latest version of the file.

        Parameters:
            file_path (str): Path to the file to compare.
            commit_hash (str): Hash of the selected commit.

        Returns:
            str: Git diff output as a string.
        """
        try:
            repo = Repo(self.repo_path)
            relative_path = os.path.relpath(file_path, self.repo_path)
            self.logger.debug(f"Calculating diff for file: {relative_path} and commit: {commit_hash}")

            # Generate git diff: diff between selected commit and working tree
            diff = repo.git.diff(commit_hash, '--', relative_path)
            return diff
        except Exception as e:
            self.logger.error(f"Failed to get diff: {e}")
            return f"Error fetching diff: {e}"

    def get_diff_with_latest(self, file_path): 
        """
        Checks if file (e.g. mapping.json) has changed since last git commit
        
        Returns: 
            BOOL. True if mapping.json has changed, False if not
        """
        self.logger.debug(f"Checking if mapping.json has changed since last git commit")    
        try: 
            relative_path = os.path.relpath(file_path, self.repo_path)
            #repo = Repo(self.repo_path)

            diff = self.repo.git.diff('HEAD', '--', relative_path)
            return bool(diff) # true if diff has changes 

        
        except Exception as e: 
            self.logger.error(f"Failed to check if mapping.json has changed: {e}")
            return False