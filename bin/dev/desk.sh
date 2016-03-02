# emi.sh
# 
# Description: desk for doing work on ASpamBlocker
# (see https://github.com/jamesob/desk)

# To install this file, symlink it to your local desks directory:
#   ln -s <ABSOLUTE PATH TO THIS FILE> ~/.desk/desks/emi.sh
# You can then switch to the desk with the command:
#   desk . emi

# Find the directory this script lies in, even when the script is called via a
# symlink, as per the installation instructions above. Copied from
# http://stackoverflow.com/a/246128/1839209:
SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do
  DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE"
done
THIS_SCRIPT_DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"

SRC_DIR="$THIS_SCRIPT_DIR/../.."

cd "$SRC_DIR"
source venv/bin/activate

PS1="(emi) \h:\W \u\$ "

# Django shell
alias shell='python manage.py shell'

# Django tests
alias test='python manage.py test'

# Django makemigrations
alias makemigrations='python manage.py makemigrations'

# Django migrate
alias migrate='python manage.py migrate'

# Django runserver
alias runserver='python manage.py runserver'

# Release current version
alias release='bin/dev/release.sh'

# git checkout
alias checkout='git checkout'

# git add
alias add='git add'

# git commit
alias commit='git commit'

# git push
alias push='git push'