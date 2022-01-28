#!/bin/bash
nohup python3 main.py 127.0.0.1 5678 --ssl "cert/cert.pem" "cert/privkey.pem" &
