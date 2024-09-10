import subprocess
import re
import os

def get_last_commit_info():
#    """
 #   Retrieve the latest commit information from the git repository.
  #  """
    commit_hash = subprocess.check_output(["git", "rev-parse", "HEAD"]).strip().decode()
    commit_message = subprocess.check_output(["git", "log", "-1", "--pretty=%B"]).strip().decode()
    commit_author = subprocess.check_output(["git", "log", "-1", "--pretty=%an"]).strip().decode()
    commit_date = subprocess.check_output(["git", "log", "-1", "--pretty=%cd"]).strip().decode()

    return {
        "hash": commit_hash,
        "message": commit_message,
        "author": commit_author,
        "date": commit_date
    }

def get_last_commit_diff():
#    """
 #   Retrieve the diff of the latest commit.
  #  """
    commit_diff = subprocess.check_output(["git", "diff", "HEAD~1", "HEAD"]).decode()
    return commit_diff

def get_changed_filenames(commit_diff):
  #  """
  #  Extract the filenames from the commit diff.
  #  """
    filenames = re.findall(r'diff --git a/(.+?) b/', commit_diff)
    return filenames

def get_function_names(commit_diff):
  #  """
  #  Extract function names from the commit diff.
  #  """
    # This regex works for Python and similar C-like languages where functions start with 'def' or return type.
    function_names = re.findall(r'^\+.*(?:def|function|public|private|protected)\s+(\w+)', commit_diff, re.MULTILINE)
    return function_names

def extract_function_from_file(filename, function_name):
   # """
   # Extract the full function definition from the file.
   # """
    function_pattern = re.compile(
        r'(def|function|public|private|protected|static|final)\s+{}\s*\(.*?\)\s*{{.*?}}'.format(function_name), 
        re.DOTALL
    )
    with open(filename, 'r') as file:
        content = file.read()
        match = function_pattern.search(content)
        if match:
            return match.group(0)
        else:
            return None

def handle_commit():
  #  """
  #  Action to take after a commit.
  #  """
    commit_info = get_last_commit_info()
    commit_diff = get_last_commit_diff()
    filenames = get_changed_filenames(commit_diff)
    function_names = get_function_names(commit_diff)

    print("New commit detected!")
    print(f"Commit Hash: {commit_info['hash']}")
    print(f"Message: {commit_info['message']}")
    print(f"Author: {commit_info['author']}")
    print(f"Date: {commit_info['date']}")
    print("\nChanged Files:")
    print("\nChanged Files:", function_names)
     for filename in filenames:
        print(f" - {filename}")
        for function_name in function_names:
            full_function = extract_function_from_file(filename, function_name)
            if full_function:
                print(f"\nFull definition of {function_name} in {filename}:")
                print(full_function)
            else:
                print(f"Function {function_name} not found in {filename}.")
    print("\nCommit Diff:")
    print(commit_diff)
    # Perform other actions here, like saving the details to a file or sending notifications.

if __name__ == "__main__":
    handle_commit()

