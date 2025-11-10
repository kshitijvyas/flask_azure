#!/bin/bash

# Azure startup script
python -m flask db upgrade
gunicorn --bind=0.0.0.0:8000 --timeout 600 run:app
