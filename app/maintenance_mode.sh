#!/bin/bash
case "$1" in
  on)
    python3 manage.py maintenance on
    echo "http://127.0.0.1:8000/adminlogin/"
    ;;
  off)
    python3 manage.py maintenance off
    ;;
  *)
    echo "Usage: $0 {on|off}"
    exit 1
esac
