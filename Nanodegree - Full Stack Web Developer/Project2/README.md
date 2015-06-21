# P2: Tournament Results

### Usage
1) Install Vagrant and VirtualBox ny following the instructions at:
https://www.udacity.com/wiki/ud197/install-vagrant

2) After successfuly connecting to the virtual machine with "vagrant ssh" command, connect and update database
```sh
cd /vagrant/tournament
psql
\i tournament.sql
\q
```
3) Finally, run the tests
```sh
python tournament_test.py
```

### What's included

```sh
Project2/
├── vagrant/tournament/tournament.py
├── vagrant/tournament/tournament.sql
├── vagrant/tournament/tournament_test.py
```

