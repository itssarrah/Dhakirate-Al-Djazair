# Backend app for **Dhakirate-Al-Djazair** project
This is the backend app for the **Dhakirate-Al-Djazair** project. It is a Flask app that provides an API for the frontend app to consume.

Most of this app's code came from the many notebooks that we tested using our data and the many many many different approachs we tested to get this project to be the way we wanted it to be. 

after being satisfied with the results we had on the notebooks, i started to bring the code to backedn and link it to front end functionality by functionality and really testing and fixing the workflow for the Learning platform that is **Dhakirate-Al-Djazair**  to be as smooth as possible.

i encountered many shortcomings that we were not aware of when using only notebooks, and i had to fix them and make the app as efficient as possible. so in this backend is the most up-to-date version of the project. and some details for our approaches mainly the chat bot and the RAG method were enhanced, i added history embedding to feed it to the rag model so that the chatbot always gets relevant context and not switch to a different topic suddenly.

also all the prompts have beeen more detailed and more informative, and the chatbot is now more interactive and more human-like. and the quiz generation is now more efficient and less repertitvie and the answers are more relevant.

this is only a brief overview of the backend, now the installation.

**NOTE:** running this app will download around 3gb of data, mainly for the SentenceTransformers Package using pip, and the RAG model from huggingface. so make sure you have enough space on your machine. and not using mobile data.

# On both operational systems: 
First thing is to have python installed, either with anaconda or without, then to install the required packages, you can use the requirements.txt file to install all the required packages by running the following command in the terminal:

**in the project directory**
```bash
pip install -r requirements.txt
```
then you can run the app by running the following command in the terminal:
```bash
python run.py
```
or 
```bash
python3 run.py
```
or 
```bash
py run.py
```