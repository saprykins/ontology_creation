# APPLICATION TO CREATE ONTOLOGY FROM ArXiv ARTICLES  


# OVERVIEW

The application consists of two parts:  

1/ API that receives and saves pdf file, extracts and saves its text and meta-data in local database.  
The API also allows to retrieve text and meta-data of a pdf-file previously uploaded via its id.  

2/ Main controller that sends requests to previously mentioned API and creates ontology.  

No authentication required  


# MORE DETAILS

## What it can 
It can receive and analyse 'PDF' and 'pdf' files. Other files are rejected.  
In case user starts to request empty database, the user receives an error message.  
In case user requests unsupported id like character or a digit which is not in database range, the user receives an error message. 


## Application structure  

```
ontology_building/  
├── flaskr  
│   ├── init.py  
│   ├── controller.py  
│   └── model.py  
├── tests  
│   └── test_**.py   (files contain code to test the app)  
├── uploads          (pdf-files storage, created automatically after app launch)  
├── venv             (virtual environment folder)  
├── main.py          (controller that sends requests to API)  
├── onto_output.owl  (ontology file that will be created by the main.py)  
├── pdf.db           (database file, created automatically after app launch)  
├── readme.md  
├── requirements.txt (list of required libs and packages)  
├── sample.pdf       (pdf file for tests)  
└── wsgi.py          (application entry point)  
```


# INSTALLATION (UBUNTU OS)

The application requires Python installed.  

 * For more details about Python installation, check the following link:  
 https://www.python.org/downloads/  

In folder "Ontology_building" create vitual environment  

* You can create it from command line:  
  ```
  virtualenv <my_env_name>
  ```
  where <my_env_name> is the name of the virtual environment you would like to create.  

  As an example, to create a virtual environment 'venv' you should type in terminal: 
  ```
  virtualenv venv
  ```
* If you do not have virtual environment tool installed, you can install it from command line:    
  ```
  sudo apt install python3-virtualenv
  ```

Activate the virtual environment you have just created:  
In Ubuntu:
```
source <my_env_name>/bin/activate
```
* In case you created virtual environment "venv" you activate it as follows:  
  ```
  source ./venv/bin/activate
  ```

* For more details about virtual environment, check the following link:  
  https://docs.python.org/3/tutorial/venv.html  

Install the packages that application requires by typing in command line:  
```
pip install -r requirements.txt
```

Activate the same virtual environment in a second terminal window.  
In Ubuntu:
```
source <my_env_name>/bin/activate
```
* In case you created virtual environment "venv" you activate it as follows:  
  ```
  source ./venv/bin/activate
  ```
The second terminal window will be used to launch main.py file.  


# TUTORIAL

## Run the server  

To run the application after installation, stay in folder "ontology_building" and type the following in command line where you activated virtual environment:  
```
python wsgi.py
```
The application runs while the command line window is open.  

* You can check in your web-browser that the application works by typing in address line of your browser:  

  http://localhost:5000/  

  You should see text "Index page" in your browser


## Transefer articles from ArXiv to API and Create ontology file  

Open the second terminal window where you activated virtual environment.  

Usage of the second terminal window will let your server run in previous terminal window  

Launch the controller in new terminal window by the command:  
```
python main.py
```
By default, only a few articles will be sent. The parameter can be modified.    

The progress is displayed in the following way  
```
Id link  
1 http://arxiv.org/pdf/cs/9308101v1  
2 http://arxiv.org/pdf/cs/9308102v1  
3 http://arxiv.org/pdf/cs/9309101v1
```
where  
* Id-column is the order of article and its id in relational database  
* link-column is the link that was transfered to API  

File with ontology "onto_output.owl" was created.  


## What has happened  

1/ From each article metadata and text were extracted and saved to local relational database file "pdf.db".  

The database can be accessed in several ways:  

* using applications such as DBeaver or others  

* with curl command (the detailed description is in "Working with database" paragraph)

2/ The extracted text is transferred to main.py, enriched with data from ArXiv API and saved to ontology file.  


# Working with database  

## Pre-requirements

The method descibed below uses curl tool.  

* In case curl tool is not installed you can install it from command line:  
  ```
  sudo apt install curl   
  ```
  

## Get metadata  

To retrive metadata about a file, you need its id. It was mentioned with link during transfert process.  
```
curl -s http://localhost:5000/documents/<document_id>
```
* where document_id should be replaced by a number.  

* In case you sent at least one file, you can retrieve metadata related to the record 1 in database by typing:  
  ```
  curl -s http://localhost:5000/documents/1
  ```
  
The standard response is in the following format:
```
{
  "author": "GPL Ghostscript SVN PRE-RELEASE 8.62",
  "creation_date": "D:20080201104827-05'00'",
  "creator": "dvips(k) 5.86 Copyright 1999 Radical Eye Software",
  "file_id": "tpvtajdvrlrqdecv",
  "link_to_content": "http://localhost:5000/text/1.txt",
  "modification_date": "D:20080201104827-05'00'",
  "status": "success"
}
```

Instead of curl, you can also retrieve metadata via web-browser  

Type in address line http://localhost:5000/documents/<document_id>  

* where document_id should be replaced by a number.  

* In case you sent at least one file, you can retrieve metadata related to the record 1 in database by typing:  

  http://localhost:5000/documents/1  


## Get text  

To retrive text from database, you need its document_id. Type the following in command line to retrieve it:  
```
curl -s http://localhost:5000/text/<document_id>.txt
```
* where document_id should be replaced by a number.  

* In case you sent at least one file, you can retrieve metadata related to the record 1 in database by typing:  
  ```
  curl -s http://localhost:5000/text/1.txt
  ```
* Keep in mind ".txt" after <document_id>

Standard response returns in the following format:  
```
{
    "text": "text from pdf"
}
```

Instead of curl, you can also retrieve text via web-browser  

Type in address line http://localhost:5000/text/<document_id>.txt 

* where document_id should be replaced by a number.  

* In case you sent at least one file, you can retrieve metadata related to the record 1 in database by typing:  

  http://localhost:5000/text/1.txt  


## Stop the application

The controller finishes its work and stop automatically.  

API server should be shut down manually.  

To stop the application, type "ctr + C" in terminal window where it was launched or close the terminal window.  
