#!/bin/bash

read -r -p "Enter Commit Message: " cmesg

git add .

git commit -m "$cmesg"

git push
