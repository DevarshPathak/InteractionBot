A voice based Drug Interaction checker for Pharmacists & Physicians
====================================================================
## 1. Video for Downloading and running app into your system
Prequisite for downloading app : **Docker** installed

Your can find the video here : [Click me](https://github.com/harshalaptraise/InteractionBot/blob/main/Install.MP4)

## 2. Create Docker Images
### Docker Installation 
Following this link for installing [Docker](https://docs.docker.com/get-docker/).

### Download Github Code
Download repository [InteractionBot](https://github.com/harshalaptraise/InteractionBot/).

### Docker Commands
Following are some commands useful for Docker.

List of all the docker images
```console 
$ sudo docker images
```

### Docker Containers...

List of all the docker containers
```console 
$ sudo docker ps
```

List of all running docker containers
```console 
$ sudo docker ps -a
```

For starting Docker container use following command
```console 
$ sudo docker start <container_id1> <container_id2> <container_id3> ...
```


## 3. Pull & Run Docker Images
### Docker Images 
Follow this link for docker images list: 
1. [App Image](https://hub.docker.com/repository/docker/devarshpathak7/drug_img/general)
2. [Database Image](https://hub.docker.com/repository/docker/devarshpathak7/mysql_final/general)
### For pulling images use following command
```console 
$ docker pull devarshpathak7/drug_img
```
```console 
$ docker pull devarshpathak7/mysql_final
```
### For running images use following command
```console 
$ docker run <image_name>
```

## 4. Setting up app in one step

Download this file for pulling docker images and running containers automatically:[drug.sh](https://github.com/harshalaptraise/InteractionBot/blob/main/Docker/drug.sh)

Run the following commands after downloading
```console 
$ chmod +x drug.sh
```
```console 
$ /drug.sh
```
## 5. Getting GROQ API Key

Visit the following link, sign up and generate your key : [GROQ](https://groq.com/)

## 6. Getting ASSEMBLYAI API Key

Visit the following link, sign up and generate your key : [ASSEMBLY AI](https://www.assemblyai.com/)

## 7. Replacing your own database with existing database

Create your database by visiting [Neo4j](https://neo4j.com/)

After successfully creating database replace credentials of database in [cypher.py](https://github.com/harshalaptraise/InteractionBot/blob/main/app/tools/cypher.py) file.

## 8. Project extension guidelines

Thank you for your interest in extending the functionality of the Drug Interaction Checker project on GitHub. Below are some guidelines to help you contribute to the project effectively:

**Feature Suggestions** : If you have ideas for new features or improvements, please create an issue on the GitHub repository outlining the feature request in detail. This will allow for discussion and collaboration among contributors.

**Code Contributions** : If you'd like to contribute code to the project, please follow these steps:

* Fork the repository to your GitHub account.
* Create a new branch for your feature or bug fix.
* Make your changes and ensure that they adhere to the project's coding style and guidelines.
* Write unit tests to cover your changes, if applicable.
* Submit a pull request to the main repository, explaining the purpose of your changes and any relevant details.
* Make sure to create docker images of your improvements and according to the format of current app.

**Documentation** : Clear and comprehensive documentation is essential for the project's users and contributors. You can contribute by:

* Improving existing documentation.
* Adding documentation for new features or components.
* Providing usage examples and tutorials.

**Performance Optimization** : If you have expertise in optimizing code or improving system performance, you can contribute by:

* Identifying and addressing performance bottlenecks.
* Refactoring code for better efficiency.
* Implementing caching mechanisms where applicable.

**Community Engagement** : Engage with other contributors and users by participating in discussions, providing feedback, and helping resolve issues reported by users.

Remember to adhere to the project's licensing terms and code of conduct while contributing. Your contributions are valuable and will help improve the Drug Interaction Checker for pharmacists and physicians worldwide. Thank you for your interest and support!
