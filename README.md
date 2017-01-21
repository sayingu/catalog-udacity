# Catalog Web Application
   * Login user's can add items, edit and delete only permit to items owner

## Instructions on how to run the project
1. Before run your project you must need a google OAuth client ID.
At [Google Cloud Console](https://console.cloud.google.com/apis)
  * Make a new project that name is "Catalog App"
  * Save client ID information to "client_secrets.json".
  * Change your client ID at *span.g-signin*s attribute *data-clientid*s value from *login.html* 

2. Install "Vagrant" and run "fullstack-nanodegree-vm"

3. After run "fullstack-nanodegree-vm" change directory to project
> cd /vagrant/catalog

4. Run python code for database init
> python database_init.py

5. Run python code for weg server
> python project.py
