# RASPBERRY  to PC and vice versa
to keep code updated, a local git server is made up in order to perform git-pull from a the local network. In my lab there's no internet connection.

to download data csv from Raspberry use wget and ftp 

## sync code from local network git repository
+ clone project directory:

'git clone userName@userIp:path/to/git/folder'

+ set up local remote:

'git remote rm origin'

'git remote add origin userName@userIp:path/to/git/folder'

+ set brach to syncronize:

'git branch --set-upstream-to=origin/master'

+ sync:

'git pull'

### note
user password will be required on git-pull

## download data from Raspberry: wget + ftp
from PC:
+ 'cd folder/to/save/data'
+ 'wget -r --user="userName" --password="userPassword" -nH  --cut-dirs=1 ftp://userIp/path/to/data/folder/in/Raspberry'

### note
+ '-r '

recursive
+ to remember pwd when log in with "userName" on Raspberry
example: /home/pi
+ '-nH --cut-dirs=1 '

avoid downloading folder structure from Raspberry

