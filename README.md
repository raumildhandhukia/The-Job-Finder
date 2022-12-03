# SER531-Team30Project

<h3>Job Recommendation Web App</h1>

<ul>
  <li>GitHub: https://github.com/raumildhandhukia/SER531-Team30Project</li>
  <li>YouTube: https://youtu.be/ETGPqOGw7BQ</li>
</ul>


Installation Steps:-

  a) Setup Fuseki Server:
  - Install JRE latest version and set JAVA and JAVA_HOME path (if java -version or java --version works in your terminal than skip this step).
  - Download Apache Jena Fuseki and Unzip it.
  - Go to the Apache Jema Fuseki source folder using terminal and type "fuseki-server" for windows or "./fuseki-server" for Mac and Linux.
  - Open any browser and open link <a href="http://localhost:3030/">http://localhost:3030/<a/>.
  - Click on manage. Click on new dataset. Give name 'user_info'. Select Persistant storage. Click on create dataset.
  - Again clock on new dataset. Give name 'jobs'. Select Persistant storage. Clock on create dataset.
  - You will see list view of datasets. On 'user_info' dataset row, click on add data. Select userinfo.owl file. Click upload now.
  - Go to the list view of datasets again. On 'jobs' dataset ro, click on add data. Select jobs.owl file. Click upload now.
  - Fuseki server is ready to use.
  
  b) Setup Project:
  - Clone the project to local directory or download it and unzip it to local directory.
  - Through terminal, go to the project directory(where app.py file is situated).
  - Run command 'pip install -r requirements.txt' or 'pip3 install -r requirements.txt'. (This will install all the requirements)
  - Run command 'python3 app.py' or 'python app.py'
  - Open browser and open link <a href="http://127.0.0.1:5000/">http://127.0.0.1:5000/<a/>
  
 Running the web app
 - Register with email, add preferences.
 - Job recommendations will be listed.
