#!/bin/bash

docker network create my-network


sudo docker run -dp 3306:3306 -e MYSQL_ROOT_PASSWORD=password -e MYSQL_DATABASE=drugInteraction --network my-network --name mysql_cont  devarshpathak7/mysql_final 



sudo docker run -dp 5000:5000   --name my_drug_container  --network my-network -v <GROQ_KEY_FILEPATH>:/run/secrets/GROQ_KEY   -v <ASSEMBLY_KEY_FILEPATH>:/run/secrets/ASSEMBLY_KEY  devarshpathak7/drug_img
