#!/bin/bash

# Banana is the original text to search for, this seems optional.
# grep "banana" testfile.txt
#
# Banana is, again, the text to search for, and will be replaced by apple.
# Banana is the only thing that will get changed in the file.
# sed -i 's/banana/apple/g' testfile.txt

# Defining our arguments
new_server_link="$1"
version="$2" # Should be just numbers, like 0.0.45

# Make sure that the arguments are populated, if not, throw an error
if [[ $1 == "" || $2 == "" ]]; then
        echo "Error: Unassigned arguments. First should be server link download, and second should be version number using just numbers."
        echo "Example Syntax: ./server_updater.sh https://server_link.com/ 0.0.45"
        exit 1
fi

# Copy the original server files so that it won't get deleted if something goes wrong.
cd /home/minecraft

if [ -e "server_old/" ]; then
        echo "Error: File 'server_old/' already exists. Please remove it before running script again."
        exit 1
fi

cp server/ server_old/ -r
rm server/ -r

# Download new server files from the provided link and rename them new_server.zip
echo "Downloading new server files from: $new_server_link"
wget $new_server_link

# Unzip the server files and rename the unzipped folder to server
unzip ~/Server-Files-$version.zip
rm ~/Server-Files-$version.zip
mv ~/Server-Files-$version/ ~/server/
cd ~/server/

# Delete duplicate files: user_jvm_args.txt, defaultconfigs/ftbessentials-server.snbt)
rm ~/server/user_jvm_args.txt
rm ~/server/defaultconfigs/ftbessentials-server.snbt

# Move deleted files over, as well as other required ones
cp ~/server_old/user_jvm_args.txt ~/server/
cp ~/server_old/defaultconfigs/ftbessentials-server.snbt ~/server/defaultconfigs/
cp ~/server_old/eula.txt ~/server/
cp ~/server_old/ops.json ~/server/
cp ~/server_old/server.properties ~/server/
cp ~/server_old/world/ ~/server/ -r

# Change the server to include the newest version
sed -i "/motd/c\motd=Jays ATM9 Server v$version" ~/server/server.properties

# Change permissions to run start script
chmod +x ~/server/startserver.sh

# Run the server
~/start.sh
screen -r
