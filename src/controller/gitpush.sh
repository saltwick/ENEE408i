#!/bin/bash

echo Enter Commit Message:

read cmesg

git add .

git commit -m $cmesg

git push
