# WikiChat
![version info](https://img.shields.io/badge/Python-3.8.10-blue)
![liscence](https://img.shields.io/badge/license-MIT-green)


**WikiChat** is a retrieval based Twitter direct message chatbot written in Python 3.8.10. WikiChat can answer questions with informaiton from Wikipedia (hence the name) and can provide a local weather report.

## Set-Up
Before running WikiChat, please ensure that all the required libraies and dependancies are installed:
```
pip install -r requirements.txt
```
## Launch
To run WikiChat, simply add your Twitter API Consumer, Consumer Secret, Access Token and Access Token Secret Keys, along with your Twitter User ID and Open Weather Map API key, to  the batch file (for Windows) or shell script (for Unix systems) in the root directory of the project and run it.

Windows:
```
cd C:\Path\to\project\WikiChat
.\launch.bat
```
Unix/Bash
```
cd /path/to/project/WikiChat
chmod +x ./launch.sh
./launch.sh
```
