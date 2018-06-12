#!/bin/bash
export HOME=/home/pi
source $HOME/.virtualenvs/dk/bin/activate
uwsgi --http :8000 --chdir $HOME/donkeycar_console  --module donkeycar_console.wsgi --check-static /home/pi/donkeycar_console/console/
exit $?
