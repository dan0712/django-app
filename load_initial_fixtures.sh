#!/bin/bash
# Loads the initial fixtures for a fresh database
./manage.py loaddata main/fixtures/groups.json
./manage.py loaddata main/fixtures/investmenttype.json
./manage.py loaddata main/fixtures/assetclass.json
./manage.py loaddata main/fixtures/portfolioset.json
./manage.py loaddata main/fixtures/region.json
./manage.py loaddata main/fixtures/ticker.json
./manage.py loaddata main/fixtures/riskprofilequestion.json
./manage.py loaddata main/fixtures/riskprofileanswer.json
