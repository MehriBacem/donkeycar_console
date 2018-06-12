#!/bin/bash
export HOME=/home/pi
source $HOME/.virtualenvs/dk/bin/activate
uwsgi --http :8000 --chdir $HOME/New/donkeycar_console  --module donkeycar_console.wsgi --check-static /home/pi/New/donkeycar_console/console/
exit $?
