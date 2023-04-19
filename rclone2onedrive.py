import json
import configparser
import argparse
import os
print()

parser = argparse.ArgumentParser()
parser.add_argument('--rcloneconfig', default=os.path.expanduser('~/.config/rclone/rclone.conf'), help='The rclone config file to draw from')
parser.add_argument('--remote', help='The rclone args.remote to import')
parser.add_argument('--syncpath', help='The directory to which to sync')
args = parser.parse_args()

if not args.syncpath:
    args.syncpath = "~/"+args.remote

config = configparser.ConfigParser()
config.read_file(open(args.rcloneconfig))

if not args.remote in config:
    raise Exception

refresh_token = str(json.loads(config[args.remote]["token"])['refresh_token'])
drive_id = config[args.remote]["drive_id"]

print("# make directories")
print("mkdir ~/.config/onedrive/" + args.remote)
print("mkdir ~/" + args.remote)

print("")
print("# make config")
print("cat << EOF > ~/.config/onedrive/" + args.remote + "/config")
print("sync_dir = \"~/" + args.remote + "\"")
print("drive_id = \"" +drive_id + "\"")
print("EOF")

print("")
print("# make refresh token")
#print("ln -s ~/.config/onedrive/refresh_token ~/.config/onedrive/" + args.remote + "/refresh_token") #this reuses a "parent" token
print("cat << EOF > ~/.config/onedrive/" + args.remote + "/refresh_token")
print(refresh_token)
print("EOF")

print("")
print("# test")
print("onedrive --confdir=~/.config/onedrive/" + args.remote + " --display-config")

print("")
print("# system service")
print("sed 's#^\\(ExecStart.*\\)#\\1 --confdir=~/.config/onedrive/" + args.remote + "#' /usr/lib/systemd/user/onedrive.service | sudo tee /usr/lib/systemd/user/onedrive-" + args.remote + ".service")
print("systemctl --user enable onedrive-" + args.remote)
print("systemctl --user start onedrive-" + args.remote)
print("journalctl -f --user-unit=onedrive-" + args.remote)
