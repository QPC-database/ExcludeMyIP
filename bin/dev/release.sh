#!/bin/bash

# Abort on any error:
set -e

git checkout live
git merge master
git push -u origin live
ssh root@excludemyip.com '/home/emi/src/bin/git-update.sh'
git checkout master