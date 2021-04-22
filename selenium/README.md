# Baserow Selenium Tests

In this repository you will find our early selenium tests, to run them you should:
1. from the root of the baserow repo `cd selenium`
1. `pip -m venv venv`
1. `source venv/bin/activate`
1. `pip install -r requirements.txt` 
1. `ENVS=all BUILD=on CLEANUP=on pytest --capture=tee-sys`

