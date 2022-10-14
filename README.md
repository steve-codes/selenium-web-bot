# selenium-web-bot

A script that enters data from an excel file into a website.

**VIDEO TUTORIAL/EXPLANIATION:**

https://www.youtube.com/watch?v=S0FF1fgepwQ


**Note:** This tutorial assumes you have:
  1. Python 3.9.5 
  2. pip3
  3. Visual Studio Code (VSC)


#### STEPS
1. Change default profile within VSC:
    * CTRL + SHIFT + P
    * Search "Terminal: Select Default Profile"
    * Click "Command Prompt" 
   
2. Create and activate the virtual environment + install library (run commands in a new CMD terminal)
   1. py -m venv venv 
      * (Creates virtual environment)
   2. venv\Scripts\activate                   
      * (activates virtual environment)
   3. python -m pip install --upgrade pip     
      * (Upgrade pip in virtual environment)
   4. pip3 install -r requirements.txt
      * (Install the required libraries for this project)
   

#### IMPORTANT
A lot of other varaibles go into making a good web bot. I only covered a short list of them due to time and the nature of the website. If you are looking to improve the detection of a web bot you will need to research other areas such as rotating proxies. There are numerous of YT videos that explain this in detail.
