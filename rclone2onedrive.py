import json
from configparser import ConfigParser
import argparse
import os
import logging

def get_rclone_details(remote_name: str, rclone_path: str = "~/.config/rclone/rclone.conf") -> tuple[str,str]:

    #open file
    rclone = ConfigParser()
    rclone.read_file(open(os.path.expanduser(rclone_path)))

    #sanity checks
    if not remote_name in rclone:
        logging.warn("An invalid rclone remote was requested. Here are the valid remotes in that file: ")
        for section in rclone.sections:
            if section["type"]=="onedrive":
                logging.warn('\t'+str(section))
        raise Exception

    remote = rclone[remote_name]

    if not remote["type"]=="onedrive":
        logging.warn("An rclone remote was requested of some type other than Onedrive. ")
        raise Exception
    
    #extract data

    drive_id = remote["drive_id"]
    refresh_token = str(json.loads(remote["token"])['refresh_token'])
    
    return drive_id, refresh_token

def make_config_from_rclone_remote(remote_name: str, rclone_path: str = "~/.config/rclone/rclone.conf") -> tuple[ConfigParser,str]:
    config = ConfigParser()
    (drive_id, refresh_token) = get_rclone_details(remote_name=remote_name,rclone_path=rclone_path)
    config['drive_id'] = drive_id
    return config, refresh_token

def print_shell_commands(remote_name: str, rclone_path: str = "~/.config/rclone/rclone.conf") -> None:
    return

parser = argparse.ArgumentParser()
parser.add_argument('--rcloneconfig', default=os.path.expanduser('~/.config/rclone/rclone.conf'), help='The rclone config file to draw from')
parser.add_argument('--remote', help='The rclone args.remote to import')
parser.add_argument('--syncpath', help='The directory to which to sync')
parser.add_argument('--output', help='The desired output format. One of "bash" or "onedrive".')
args = parser.parse_args()

if not args.syncpath:
    args.syncpath = "~/"+args.remote

if(args.output == "bash"):
    (drive_id,refresh_token) = get_rclone_details(args.remote, args.rcloneconfig)

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
    print("ln -s ~/.config/onedrive/refresh_token ~/.config/onedrive/" + args.remote + "/refresh_token #reuses a \"parent\" onedrive token") 
    print("cat << EOF > ~/.config/onedrive/" + args.remote + "/refresh_token" + "#reuses rclone's token")
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
elif(args.output=="onedrive"):
    (config, refresh_token) = make_config_from_rclone_remote(args.remote, args.rcloneconfig)
    print("onedrive config: ")
    print(config) #TODO can I do this
    print("refresh_token:")
    print(refresh_token)

exit(0)