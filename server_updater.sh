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
        echo "Error: Unassigned arguments. First should be server link download, and second should be ve>
        echo "Example Syntax: ./server_updater.sh https://server_link.com/ 0.0.45"
        exit 1
fi

# Copy the original server files so that it won't get deleted if something goes wrong.
cd /home/minecraft

if [ -e "server_old/" ]; then
        echo "Error: File 'server_old/' already exists. Please remove it before running script again."
        exit 1
fi

cp server/ server_old/


# Download new server files from the provided link and rename them new_server.zip
echo "Downloading new server files from: $new_server_link"
wget -o new_server.zip $new_server_link

# Unzip the server files and rename the unzipped folder to server
unzip new_server.zip
mv Server-Files-$version/ server/
cd server/

# Delete duplicate files: user_jvm_args.txt, defaultconfigs/ftbessentials-server.snbt)
rm user_jvm_args.txt
rm defaultconfigs/ftbessentials-server.snbt

# Move deleted files over, as well as other required ones
cp ~/server_old/user_jvm_args.txt .
cp ~/server_old/defaultconfigs/ftbessentials-server.snbt ./defaultconfigs/
cp ~/server_old/eula.txt .
cp ~/server_old/ops.json .
cp ~/server_old/server.properties .
cp ~/server_old/world/ .
