#!/bin/bash
nohup python3 main.py svcrafted.com 5678 --ssl "cert/cert.pem" "cert/privkey.pem" &
