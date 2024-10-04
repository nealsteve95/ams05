#!/bin/bash

export LOCAL_IP=$(hostname -I | awk '{print $1}')

docker compose up -d

