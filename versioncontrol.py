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

    def __init__(self, mapping_path=None, repo_path=None):
        """
        Initializes the VersionControl class with the repository path and mapping file path.

        Parameters:
            repo_path (str): The path to the Git repository.
            mapping_path (str): Path to the mapping.json file.
        """
        self.logger = logging.getLogger(__name__)
        #MacOS: /Users/reiskoenig/Nextcloud/MASTER ARBEIT/Code
        #Windows: "C:\\Users\\user\\projects\\my_git_repo"
        self.repo_path = "/Users/reiskoenig/Nextcloud/MASTER ARBEIT/Code/SysMLv2 API Code" #absolute path to the git folder 
        self.mapping_path = mapping_path 
        self.repo = git.Repo(repo_path)

    def get_files_from_mapping(self):
        """
        Reads the mapping.json file to extract the list of files to be versioned.

        Returns:
            list: A list of file paths specified in the mapping.json.
        """
        
        mapping_data = load_json(self.mapping_path)

        files = set()
        for category in mapping_data.values():
            for item in category:
                files.add(item["filePath"])
        return list(files)

    def stage_files(self):
        """
        Stages files listed in the mapping.json for committing.
        """
        files_to_commit = self.get_files_from_mapping()
        for file_path in files_to_commit:
            full_path = os.path.join(self.repo_path, file_path)
            if os.path.exists(full_path):
                self.repo.git.add(full_path)
                print(f"Staged file: {full_path}")
            else:
                print(f"File not found, skipping: {full_path}")

    def commit_and_push(self, commit_message="Automated Commit"):
        """
        Commits and pushes the staged changes to the remote repository.

        Args:
            commit_message (str): The commit message for the changes.
        """
        try:
            # Stage relevant files
            self.stage_files()

            # Check if there are changes to commit
            if self.repo.index.diff("HEAD"):
                # Commit changes
                self.repo.index.commit(commit_message)
                print(f"Commit successful: {commit_message}")

                # Push to remote
                origin = self.repo.remote(name="origin")
                origin.push()
                print("Changes pushed to remote repository.")
            else:
                print("No changes to commit.")
        except Exception as e:
            print(f"Error during commit and push: {e}")

    def load_commit_history_from_file_path(self, file_path, treeview_widget):
        """Loads git commits from file path of the treeview widget and displays it inside given treeview_widget
        (Versionframe inside optionsframe)

        Parameters: 
            file_path : String. Contains file path to get the commit history from git. 
            text_widget : (tk) Text Widget. tkinter widget to fill information in string format.
        
        Returns: 
            treeview_widget updated/filled with git commits 
        """ 
        #file_path = file_path.get() # Convert entry widget information to string 
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

    def get_diff_with_latest(self, file_path, commit_hash):
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
