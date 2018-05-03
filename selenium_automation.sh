#!/usr/bin/env bash

# Install requirements to run the automation
# echo "Installing testing requirements ... ..."
# pip install -r requirements/test.txt
# echo "Run build for webpack ... ..."
# sudo apt-get install nodejs npm -y
# npm install
# npm run build

# use the testcloud settings
cd ap
export DJANGO_SETTINGS_MODULE=ap.settings.testcloud

# populate initial data
echo "Populating initial data ... ..."
python manage.py populate
python manage.py populate_testers

# create a super user
echo "Creating superuser ... ..."
echo "from accounts.models import User; User.objects.filter(email='ap_test@gmail.com').delete(); User.objects.create_superuser('ap_test@gmail.com', 'ap')" | python manage.py shell

# run the server
echo "Loading webpack ... ..."
npm run start > run_webpack.log 2>&1 &
while ! grep -qw "webpack: Compiled successfully." run_webpack.log; do sleep 5; done
echo "Loading Django ... ..."
python manage.py runserver &
sleep 60

# run the regression
#! ENV VARIABLES FOR SAUCELAB IN TRAVIS SETTINGS !#
echo "run the selenium via saucelab"
cd ../selenium/automation
python run_regression.py
