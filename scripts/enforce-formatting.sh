#!/bin/bash
# file name: enforce-formatting.sh

# The `black` python formatter screws up quotes, but does a good job in many
# other respects.
# To remedy it's annoying shortcomings, we run two other code formatters
# afterwards.

set -eo pipefail
RED=$'\033[0;91m'
NORMAL=$'\033[0m'
if ! [ -d .git ]; then
    printf $RED
    echo 'Only run this in a folder containing a .git subfolder (dangerous otherwise!)'
    printf $NORMAL
    exit 1
fi
PIP=pip
if ! pip -V &> /dev/null; then
    PIP=pip3
fi
if ! $PIP -V &> /dev/null; then
    # https://github.com/pypa/virtualenv/issues/596#issuecomment-411485104
    PIP='python3 -m pip'
fi
if [[ "$VIRTUALENV" -ne "" ]]; then
    PIPFLAGS=--user
fi

# Install some pip packages if they're not present
if ! black --version &> /dev/null; then
    $PIP install $PIPFLAGS black
fi
if ! double-quote-string-fixer -h &> /dev/null; then
    $PIP install $PIPFLAGS pre-commit-hooks
fi
# always try to upgrade isort
$PIP install --upgrade $PIPFLAGS isort

#  Run all 3 formatters
echo '[tool.black]
line-length = 79
' > pyproject.toml
if (set -x; \
    black . -q  \
    && (find . -name '*.py' -exec double-quote-string-fixer {} + || true) > /dev/null \
    && isort -m5 -q . \
) then
    echo 🍏 Formatters ran successfully
    rm -f pyproject.toml
else
    echo 🔴 Automatic formatting failed!
    rm -f pyproject.toml
    exit 1
fi

if [ -z "$(git status --untracked-files=no --porcelain)" ]; then 
  echo 🍏 Repo is aligned with formatter suggestions
else 
  echo 🔴 Please fix the following w.r.t formatting!
  GIT_PAGER=cat git diff
  exit 1
fi
