# ExcludeMyIP
A Google Analytics tool to exclude your own (home/work) IP. See it live at
www.excludemyip.com.

## Deployment
This web application can be deployed on a bare Ubuntu 14.04 installation
by copying the script bin/install.sh to the server and executing it as root.
You will need to edit the global variables defined at the top of your script
to match your environment. Please also note that the current configuration
throughout the code base assumes that the server runs on domain
www.excludemyip.com. If you want to run it on a different domain, you need
to replace all occurrences of "excludemyip.com" in the code base with your
domain.