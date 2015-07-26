# P3: Item Catalog

### Installation
1) Install Vagrant and VirtualBox by following the instructions at:
https://www.udacity.com/wiki/ud197/install-vagrant

2) After successfuly connecting to the virtual machine with "vagrant ssh" command, connect and run the application
```sh
vagrant ssh
cd /vagrant/catalog
python application.py
```
3) Open your browser to see the page
http://localhost:8080

4) If you want, you can populate DB with the test content
```sh
python database_populate.py 
```

### API Endpoints
| Method | Endpoint                                         | Description
|--------|--------------------------------------------------|--------------------------------------------------------
| GET    | /catalog                                         | Shows all current categories and the latest added items
| GET    | /catalog/{catalog_id}/items                      | Shows all items in the category
| GET    | /catalog/{catalog_id}/item/{item_id}             | Shows the item info
| GET    | /login                                           | Provides user login with Google or Facebook account
| GET    | /disconnect                                      | Logs out the user
| GET    | /catalog/add                                     | Shows input fields to add a new item
| POST   | /catalog/add                                     | Adds the new item
| GET    | /catalog/{catalog_id}/item/{item_id}/edit        | Shows input fields to edit an item
| POST   | /catalog/{catalog_id}/item/{item_id}/edit        | Updates the item
| GET    | /catalog/{catalog_id}/item/{item_id}/delete      | Shows input fields to delete an item
| POST   | /catalog/{catalog_id}/item/{item_id}/delete      | Deletes the item
| GET    | /catalog/json                                    | Returns the catalog in JSON format
| GET    | /catalog/xml                                     | Returns the catalog in XML format
