# donkeycar_console

## Getting Started

These instructions will get you a copy of the project up and running on your Raspberry Pi as a service.

### Installing

- git clone https://github.com/MehriBacem/donkeycar_console.git
- cd donkeycar_console/
- pip install -r requirements.txt


### Running as a service
- add your host to  ALLOWED_HOSTS  in "donkeycar_console/donkeycar_console/settings.py"
- sudo apt-get update
- sudo apt-get install supervisor
- create a file "donkeycar_console.conf" in /etc/supervisor/conf.d/ and copy this:
  
  
         
          [program:donkeycar_console]
          command=bash /home/pi/donkeycar_console/donkeycar_console.sh
          autostart=true  
          autorestart=true  
          stderr_logfile=/home/pi/donkeycar_console.err.log
          stdout_logfile=/home/pi/donkeycar_console.out.log
          user=pi  
       


- sudo service supervisor start  
- sudo reboot   
- open the console with "host:8000" (e.g  d2.local:8000)
