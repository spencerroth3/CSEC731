The following repo contains a docker-compose file to deploy the web server and proxy architecture. 

To launch the containers, install ansible on the target system with `apt install ansible` and then download the `playbook.yml` file in the /ansible folder.

Then simply run `sudo ansible-playbook playbook.yml` to lauch the containers.
