#!/bin/bash

# Banana is the original text to search for, this seems optional.
# grep "banana" testfile.txt
#
# Banana is, again, the text to search for, and will be replaced by apple.
# Banana is the only thing that will get changed in the file.
# sed -i 's/banana/apple/g' testfile.txt

# Defining our arguments
new_server_link="$1"
filename=$(basename "$new_server_link")
filename_without_extension="${filename%.zip}"
pattern="Server-Files-(.*).zip"

echo "new_server_link = $new_server_link"
echo "filename = $filename"
echo "filename_without_extension = $filename_without_extension"

# Make sure that the arguments are populated, if not, throw an error
if [[ $1 == "" ]]; then
        echo "Error: Unassigned arguments. You need to include the server download link."
        echo "Example Syntax: ./server_updater.sh https://edge.forgecdn.net/files/4861/3/Server-Files-0.2.18b.zip"
        exit 1
fi

# Check if there is currently a screen open. If there is, cancel the script
if screen -ls | grep -q "There is a screen"; then
        echo "There is currently an open screen session. Please close it before trying to run the script again in order to prevent data loss."
        exit 1
fi

# Determine the version number
if [[ $filename =~ $pattern ]]; then
        version="${BASH_REMATCH[1]}"
        echo "Version successfully detected: $version"
else
        echo "$version"
        echo "Version not successfully detected. This means that the server download URL doesn't end with 'Server-Files-VERSION.zip'"
        exit 1
fi

# Copy the original server files so that it won't get deleted if something goes wrong.
cd /home/minecraft

if [ -e "server_old/" ]; then
        echo "Error: File 'server_old/' already exists. Please remove it before running script again."
        exit 1
fi

mv server/ server_old/

# Download new server files from the provided link and rename them new_server.zip
echo "Downloading new server files from: $new_server_link"
wget $new_server_link

# Unzip the server files and rename the unzipped folder to server
unzip ~/$filename
rm ~/$filename
mv ~/$filename_without_extension/ ~/server/
cd ~/server/

# Delete duplicate files: user_jvm_args.txt
rm ~/server/user_jvm_args.txt

# Move deleted files over, as well as other required ones
cp ~/server_old/user_jvm_args.txt ~/server/
cp ~/server_old/eula.txt ~/server/
cp ~/server_old/ops.json ~/server/
cp ~/server_old/server.properties ~/server/
cp ~/server_old/world/ ~/server/ -r
cp ~/server_old/server-icon.png ~/server/

# Change the server to include the newest version
sed -i "/motd/c\motd=Jays ATM9 Server v$version" ~/server/server.properties

# Change permissions to run start script
chmod +x ~/server/startserver.sh

# Run the server
~/start.sh
screen -r
