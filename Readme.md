## Setup spiders cluster in the cloud

Pre-requisites:
-   Terraform
-   Ansible
-   scrapyd-client (`pip install scrapyd-client`)

Steps:

`python3 setup.py`
initialize the Infrastructure <br>
`python3 deploy.py`
deploy the project to scrapyd servers<br>
`python3 project/push.py`
push the urls to Redis<br>

