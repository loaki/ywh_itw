### Usage
> edit .env as the env.sample with your variables  
> `docker-compose up`

### Containers
> **mongodb** for data storage  
> **redis** for data queuing  
> **ywh_programs** to fetch programs on YesWeHack API  
> **inject_programs** to insert programs to db  

### Application
> Fetch all the public programs on YesWeHack API every 10 min  
> Push program's title and reports_count to a redis queue  
> Publish a message to a redis channel  
> A thread listen redis channel and pop the program  
> The program is saved to mongodb  
