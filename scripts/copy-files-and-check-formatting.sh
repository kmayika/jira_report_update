#!/bin/bash
set -eo pipefail
RED=$'\033[0;91m'
NORMAL=$'\033[0m'
if ! [ -d .git ]; then
    printf $RED
    echo 'Expected to find a .git folder'
    printf $NORMAL
    exit 1
fi

mkdir -p tmp_copy
rsync -a --include '*/' --include '*.py' --exclude '*' --exclude 'tmp_copy' --exclude 'tmp_copy2' ./ tmp_copy/
cd tmp_copy
git init > /dev/null
git add .
git commit -a -m init > /dev/null
SUCCESS=true
if ! ../scripts/enforce-formatting.sh; then
    SUCCESS=false
fi
cd  ..
rm -rf tmp_copy
if [[ "$SUCCESS" != "true" ]]; then
    exit 1
fi
