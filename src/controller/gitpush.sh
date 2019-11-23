#!/bin/bash

echo Enter Commit Message:

read cmesg

git add .

git commit $cmesg

git push
