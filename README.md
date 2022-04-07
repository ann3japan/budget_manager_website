## Budget Manager
---
### Provide an instrument that will allow users to  

* Control inflows
* Control outflow
* Check current balance

### Functionality  

* Sign up 
* Login
* Budget counter
* Add inflows and outflows
* Delete inflows and outflows


### Technology stack  

* Python3 (flask, jinja2)
* MongoDB
* Nginx
* Docker
* Github Actions

### Deployment  

Docker-compose exposes port 80 of Nginx and nginx proxies all requests to the app container.

To deploy the app run `docker-compose up -d`.
