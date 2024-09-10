#!/usr/bin/python3

# Run this script like below
# python3 reviewCodeDiff.py diff_files/diff_test_koushik 
# python3 reviewCodeDiff.py --diff-file="../../diff_files/diff_ankit_2" --code-path="/home/luser/hackfest/2024/codebase/build_28mx/master/packages/boxer/"
# python3 reviewCodeDiff.py --diff-file="../../diff_files/diff_ankit_2"

# Error Scenarios:
# Scenario-1 : No Diff File provided
#     python3 reviewCodeDiff.py
# Scenario-2 : Invalid Diff File provided
#     python3 reviewCodeDiff.py diff_test
# Scenario-3 : Empty diff file provided
#     python3 reviewCodeDiff.py diff_test_empty

# Fixed Response parsing fixed
# gptResponse = gptResponse
# print("\n\ngptResponse1", type(gptResponse), gptResponse)
# gptResponse = gptResponse.choices
# print("gptResponse2", type(gptResponse), gptResponse)
# gptResponse = gptResponse.choices[0]
# print("gptResponse3", type(gptResponse), gptResponse)
# gptResponse = gptResponse.choices[0].message
# print("gptResponse4", type(gptResponse), gptResponse)
# gptResponse = gptResponse.choices[0].message.content
# print("gptResponse5", type(gptResponse), gptResponse)
    

from GptApiHandler import *
from ContextHandler import *
from UtilityHandler import Util
import time
import sys

Util.listTimedCategory["overall_exec_time"] = "Overall Execution Time"
Util.debugFlags = {
        "DEBUG_DIFF": False,           # Displays the entire content of diff file
        "DEBUG_PATCH": True,          # Displays all Diff Patch data decoded from diff file
        "DEBUG_GPT_PROMPT": True,      # Dislays the GPT prompt sent and response received
        "DEBUG_TIMED_STATS": False     # Displays the statistics in the end how much time each process has taken
}
#print(Util.isDebugFlagSet("DEBUG_PATCH"))
#codePath = "/auto/nobackup-bgl-mitg8-dev11/ankaman/builds/build_28mx/master/packages/boxer"
#codePath1 = "/home/luser/hackfest/2024/codebase/build_28mx/master/packages/boxer/"
#diffFilePath = "/home/luser/hackfest/2024/diff_files"


def getGptPrompt(diffFileData, codeContext):
    Util.printRunningProcess("  > Setting GPT prompt based on Diff file data and code context")

  #  gptPrompt = "Please review the following c code and Generate a summary table of recent code changes. The table should have two columns: one for the file name and the other for a brief description of the changes made\n"
    #gptPrompt = "Please review the following c code and also provide additional suggestions:\n"
   # gptPrompt = "Please review the following c code.Suggest alternate or modified code change clearly with code if there are any syntactic, semantic or logical errors.  Generate a summary table of recent code changes. the table should have 2 columns, one for file name and other for brief description of changes made.Ensure that the table is  clean and aligned properly for readability.Include a brief overview above table to describe the overall context of the changes. Provide some suugestions for code improvement, optimizations possible\n"
    gptPrompt = "Please review the following c code. Provide alternate or modified code change n detail if there are any syntactic, semantic or logical errors.  Generate a summary table of recent code changes. the table should have 2 columns, one for file name and other for brief description of changes made.Ensure that the table is clean and aligned properly for readability.Include a brief overview or walkthrough above table to describe the overall context of the changes. Provide some suugestions for code improvement, optimizations possible\n"
    gptPrompt += diffFileData
    return gptPrompt

def getReviewResponse(diffFileData, codeContext=""):
    Util.printRunningProcess("  > Getting GPT response and formatting the review response")
    
    gptPrompt = getGptPrompt(diffFileData, codeContext)
    if not gptPrompt:
        print("PromptError: Empty prompt received")
        return None

    print("\n###########################################################################################")
  # print("GPT Prompt:\n\n", gptPrompt)
    print("###########################################################################################\n")

    print("Please wait while review is in progress..!")
    Util.setStartTime("get_gpt_response")
    gptResponse =  get_gpt_api_response(gptPrompt)
    if not gptResponse:
        print("Failed to review the code")
        sys.exit(1)

    gptResponseMsg = gptResponse.choices[0].message.content
    Util.setExecutionTime("get_gpt_response")

    print("\n###########################################################################################")
    print("GPT Response:\n\n", gptResponseMsg)
    print("###########################################################################################\n")
    return gptResponse

def reviewCode(reviewDiffFile, codePath):
    # Getting diff data and fetching code context for diff data
    print("\nProcessing: Parsing diff data and getting relevant context")
    Util.setStartTime("parse_diff_and_get_context")
    diffFileData = getDiffFileData(reviewDiffFile)
   # diffPatch = getDiffPatchWithUnidiff(reviewDiffFile)
    print("Returned")
    #codeContext = getCodeContext(diffPatch, diffFileData, codePath)
    Util.setExecutionTime("parse_diff_and_get_context")

    # Setting GPT prompt and fetching review on code change
    Util.printRunningProcess("Setting GPT prompt and getting Review Response")
    getReviewResponse(diffFileData, codeContext="")
    Util.printRunningProcess("Review complete. Exiting..!\n")



if __name__ == '__main__':
    # Execute all the code here
    reviewDiffFile, codePath = Util.checkArgumentSanity()
    
    Util.setStartTime("overall_exec_time")
    reviewCode(reviewDiffFile, codePath)
    Util.setExecutionTime("overall_exec_time")
    
    if Util.isDebugFlagSet("DEBUG_TIMED_STATS"):
        Util.printTimedStats()
    sys.exit(0)
