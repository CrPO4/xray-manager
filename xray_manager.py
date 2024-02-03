# by CrPO4
import os
import sys
import requests
import json
import zipfile
import subprocess
import datetime
import glob

def addXrayUser():
    newUserEmail = input("Enter new user's e-Mail address: ")
    uuidGenerator = subprocess.Popen(["/opt/xray/xray", "uuid"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    uuidGeneratorOutputEncoded, uuidGeneratorErrorEncoded = uuidGenerator.communicate()
    uuid = uuidGeneratorOutputEncoded.decode("ascii").strip()
    with open("/opt/xray/config.json", "r") as configFile:
        jsonString = str(configFile.read())
        jsonXrayConfig = json.loads(jsonString)
        jsonXrayConfig["inbounds"][0]["settings"]["clients"].append({})
        jsonXrayConfig["inbounds"][0]["settings"]["clients"][-1]["id"] = uuid
        jsonXrayConfig["inbounds"][0]["settings"]["clients"][-1]["email"] = newUserEmail
        jsonXrayConfig["inbounds"][0]["settings"]["clients"][-1]["flow"] = "xtls-rprx-vision"
        print("Writing changes to config..")
        with open("/opt/xray/config.json", 'w', encoding='utf-8') as writableConfigFile:
            json.dump(jsonXrayConfig, writableConfigFile, ensure_ascii=False, indent=4)  
    with open("/opt/xray/hostname", "r") as hostnameFile:
        hostname = hostnameFile.readline()
    with open("/opt/xray/public.key", "r") as publicKeyFile:
        publicKey = publicKeyFile.readline()
    with open("/opt/xray/short-id", "r") as shortIdFile:
        shortId = shortIdFile.readline()
    print("")
    print("Restarting Xray server..")
    xrayRestartProcess = subprocess.Popen(["systemctl", "restart", "xray"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    xrayRestartProcess.wait()
    print("")
    connectionString = "vless://" + uuid + "@" + hostname + ":443?security=tls&packetEncoding=xudp&sni=twitch.tv&alpn=h2&fp=chrome&pbk=" + publicKey + "&sid=" + shortId + "&type=tcp&flow=xtls-rprx-vision&encryption=none#" + newUserEmail + " on " + hostname
    print("This user can use this connection string:", connectionString)
    print("")
    with open("/opt/xray/no-qr", "r") as qrInstallFailedFile:
        if qrInstallFailedFile.readline() == "True":
            qrInstallFailed = True
        else:
            qrInstallFailed = False
    if not qrInstallFailed:
        qrRequired = input("Would you also like to get a QR-code (y/N)? ")
        match qrRequired:
            case "Y":
                print("")
                qrGenerationProcess = subprocess.Popen(["qrencode", "-t", "ansiutf8", connectionString], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                qrGenerationProcessOutputEncoded, qrGenerationProcessErrorEncoded = qrGenerationProcess.communicate()
                qrCode = qrGenerationProcessOutputEncoded.decode("utf-8").strip()
                print(qrCode)
            case "y":
                print("")
                qrGenerationProcess = subprocess.Popen(["qrencode", "-t", "ansiutf8", connectionString], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                qrGenerationProcessOutputEncoded, qrGenerationProcessErrorEncoded = qrGenerationProcess.communicate()
                qrCode = qrGenerationProcessOutputEncoded.decode("utf-8").strip()
                print(qrCode)
            case _:
                pass
    print("")

def removeXrayUser():
    with open("/opt/xray/config.json", "r") as configFile:
        jsonString = str(configFile.read())
        jsonXrayConfig = json.loads(jsonString)
        jsonClientsList = jsonXrayConfig["inbounds"][0]["settings"]["clients"]
        counter=0
        for client in jsonClientsList:
            print(str(counter) + ": " + client["email"])
            counter+=1
        print("")
        idToDelete = input("Which client to delete? ")
        try:
            idToDelete = int(idToDelete)
        except:
            print("No changes were made.")
            failureDuringScript("incorrect_id")
        popClient = jsonXrayConfig["inbounds"][0]["settings"]["clients"].pop(idToDelete)
        print("Writing changes to config..")
        with open("/opt/xray/config.json", 'w', encoding='utf-8') as writableConfigFile:
            json.dump(jsonXrayConfig, writableConfigFile, ensure_ascii=False, indent=4) 
    print("")

def editXrayUser():
    with open("/opt/xray/config.json", "r") as configFile:
        jsonString = str(configFile.read())
        jsonXrayConfig = json.loads(jsonString)
        jsonClientsList = jsonXrayConfig["inbounds"][0]["settings"]["clients"]
        counter=0
        for client in jsonClientsList:
            print(str(counter) + ": " + client["email"])
            counter+=1
        print("")
        idToEdit = input("Which client to edit? ")
        try:
            idToEdit = int(idToEdit)
        except:
            print("No changes were made.")
            failureDuringScript("incorrect_id")
        newEmail = input("Enter new e-Mail address: ")
        jsonXrayConfig["inbounds"][0]["settings"]["clients"][idToEdit]["email"] = newEmail
        print("Writing changes to config..")
        with open("/opt/xray/config.json", 'w', encoding='utf-8') as writableConfigFile:
            json.dump(jsonXrayConfig, writableConfigFile, ensure_ascii=False, indent=4)
    print("")

def showXrayUser():
    with open("/opt/xray/config.json", "r") as configFile:
        jsonString = str(configFile.read())
        jsonXrayConfig = json.loads(jsonString)
        jsonClientsList = jsonXrayConfig["inbounds"][0]["settings"]["clients"]
        counter=0
        for client in jsonClientsList:
            print(str(counter) + ": " + client["email"])
            counter+=1
        print("")
        idToShow = input("Which client to show? ")
        try:
            idToShow = int(idToShow)
        except:
            print("No changes were made.")
            failureDuringScript("incorrect_id")
    with open("/opt/xray/hostname", "r") as hostnameFile:
        hostname = hostnameFile.readline()
    with open("/opt/xray/public.key", "r") as publicKeyFile:
        publicKey = publicKeyFile.readline()
    with open("/opt/xray/short-id", "r") as shortIdFile:
        shortId = shortIdFile.readline()
    print("")
    uuid = jsonClientsList[idToShow]["id"]
    email = jsonClientsList[idToShow]["email"]
    connectionString = "vless://" + uuid + "@" + hostname + ":443?security=tls&packetEncoding=xudp&sni=twitch.tv&alpn=h2&fp=chrome&pbk=" + publicKey + "&sid=" + shortId + "&type=tcp&flow=xtls-rprx-vision&encryption=none#" + email + " on " + hostname
    print("This user's connection string:", connectionString)
    print("")
    with open("/opt/xray/no-qr", "r") as qrInstallFailedFile:
        if qrInstallFailedFile.readline() == "True":
            qrInstallFailed = True
        else:
            qrInstallFailed = False
    if not qrInstallFailed:
        qrRequired = input("Would you also like to get a QR-code (y/N)? ")
        match qrRequired:
            case "Y":
                print("")
                qrGenerationProcess = subprocess.Popen(["qrencode", "-t", "ansiutf8", connectionString], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                qrGenerationProcessOutputEncoded, qrGenerationProcessErrorEncoded = qrGenerationProcess.communicate()
                qrCode = qrGenerationProcessOutputEncoded.decode("utf-8").strip()
                print(qrCode)
            case "y":
                print("")
                qrGenerationProcess = subprocess.Popen(["qrencode", "-t", "ansiutf8", connectionString], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                qrGenerationProcessOutputEncoded, qrGenerationProcessErrorEncoded = qrGenerationProcess.communicate()
                qrCode = qrGenerationProcessOutputEncoded.decode("utf-8").strip()
                print(qrCode)
            case _:
                pass
    print("")
        

def installXrayServer():
    print("What is your domain name or IP address?")
    hostname = input("Your input: ")
    print("Stopping Xray server..")
    xrayStopProcess = subprocess.Popen(["systemctl", "stop", "xray"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    xrayStopProcess.wait()
    print("Installing QREncode..")
    noApt = False
    noYum = False
    qrInstallFailed = False
    if os.path.isfile("/bin/apt"):
        aptPath = "/bin/apt"
    elif os.path.isfile("/sbin/apt"):
        aptPath = "/sbin/apt"
    elif os.path.isfile("/usr/bin/apt"):
        aptPath = "/usr/bin/apt"        
    elif os.path.isfile("/usr/sbin/apt"):
        aptPath = "/usr/sbin/apt"
    else:
        noApt = True
    if os.path.isfile("/bin/yum"):
        yumPath = "/bin/yum"
    elif os.path.isfile("/sbin/yum"):
        yumPath = "/sbin/yum"
    elif os.path.isfile("/usr/bin/yum"):
        yumPath = "/usr/bin/yum"        
    elif os.path.isfile("/usr/sbin/yum"):
        yumPath = "/usr/sbin/yum"
    else:
        noYum = True    
    if not noApt:
            qrEncodeInstallProcess = subprocess.Popen(["apt", "-o", "Apt::Get::Assume-Yes=true", "install", "qrencode"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            qrEncodeInstallProcess.wait()
            if qrEncodeInstallProcess.returncode != 0:
                qrInstallFailed = True
    if not noYum:
            qrEncodeInstallProcess = subprocess.Popen(["yum", "--assumeyes", "install", "qrencode"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            qrEncodeInstallProcess.wait()
            if qrEncodeInstallProcess.returncode != 0:
                qrInstallFailed = True
    print("Creating directories..")
    os.makedirs("/opt/xray", exist_ok=True)
    with open("/opt/xray/no-qr", "w") as qrInstallFailedFile:
        if qrInstallFailed:
            qrInstallFailedFile.write("True")
        else:
            qrInstallFailedFile.write("False")
    with open("/opt/xray/hostname", "w") as hostnameFile:
        hostnameFile.write(hostname)
    print("Downloading latest Xray release..")
    latestReleaseJsonUrl = "https://api.github.com/repos/XTLS/Xray-core/releases/latest"
    latestReleaseJson = requests.get(latestReleaseJsonUrl, allow_redirects=True).text
    latestReleaseJsonAssets = json.loads(latestReleaseJson)['assets']
    latestReleaseUrl = ""
    noLink = True
    while noLink:
        for asset in latestReleaseJsonAssets:
            if asset['name'] == "Xray-linux-64.zip":
                noLink = False
                latestReleaseUrl = asset['browser_download_url']
    if latestReleaseUrl == "":
        failureDuringScript("downloadlink_not_found")
    latestReleaseFileInMemory = requests.get(latestReleaseUrl, allow_redirects=True)
    latestReleaseFile = open("/opt/xray-linux-64.zip", 'wb').write(latestReleaseFileInMemory.content)
    print("Extracting zip to /opt/xray..")
    with zipfile.ZipFile("xray-linux-64.zip","r") as xrayZip:
        xrayZip.extractall("/opt/xray")
    print("Removing downloaded zip..")
    os.remove("/opt/xray-linux-64.zip")
    print("Setting permissions..")
    os.chmod("/opt/xray/xray", 0o755)
    print("Creating systemd unit..")
    with open("/etc/systemd/system/xray.service", "w") as unitFile:
        print("[Unit]", file=unitFile)
        print("Description=Xray Service", file=unitFile)
        print("Documentation=https://github.com/xtls", file=unitFile)
        print("After=network.target nss-lookup.target", file=unitFile)
        print("", file=unitFile)
        print("[Service]", file=unitFile)
        print("User=nobody", file=unitFile)
        print("CapabilityBoundingSet=CAP_NET_ADMIN CAP_NET_BIND_SERVICE", file=unitFile)
        print("AmbientCapabilities=CAP_NET_ADMIN CAP_NET_BIND_SERVICE", file=unitFile)
        print("NoNewPrivileges=true", file=unitFile)
        print("ExecStart=/opt/xray/xray run -config /opt/xray/config.json", file=unitFile)
        print("Restart=on-failure", file=unitFile)
        print("RestartPreventExitStatus=23", file=unitFile)
        print("LimitNPROC=10000", file=unitFile)
        print("LimitNOFILE=1000000", file=unitFile)
        print("", file=unitFile)
        print("[Install]", file=unitFile)
        print("WantedBy=multi-user.target", file=unitFile)
    print("Generating Xray keys..")
    keyGenerator = subprocess.Popen(["/opt/xray/xray", "x25519"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    keyGeneratorOutputEncoded, keyGeneratorErrorEncoded = keyGenerator.communicate()
    keyGeneratorOutput = keyGeneratorOutputEncoded.decode("ascii")
    keyGeneratorOutputSplit = (keyGeneratorOutput.partition("\n"))
    privateKey = keyGeneratorOutputSplit[0].split(": ")[1]
    publicKey = keyGeneratorOutputSplit[2][0:len(keyGeneratorOutputSplit[2])-1].split(": ")[1]
    with open("/opt/xray/public.key", "w") as publicKeyFile:
        publicKeyFile.write(publicKey)
    print("Generating Xray ShortID for default user..")
    shortIdGenerator = subprocess.Popen(["openssl", "rand", "-hex", "8"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    shortIdGeneratorOutputEncoded, shortIdGeneratorErrorEncoded = shortIdGenerator.communicate()
    shortId = shortIdGeneratorOutputEncoded.decode("ascii").strip()
    with open("/opt/xray/short-id", "w") as shortIdFile:
        shortIdFile.write(shortId)
    print("Generating Xray UUID for default user..")
    uuidGenerator = subprocess.Popen(["/opt/xray/xray", "uuid"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    uuidGeneratorOutputEncoded, uuidGeneratorErrorEncoded = uuidGenerator.communicate()
    uuid = uuidGeneratorOutputEncoded.decode("ascii").strip()    
    print("Generating Xray config..")
    jsonXrayConfig = {}
    jsonXrayConfig["log"] = {}
    jsonXrayConfig["log"]["loglevel"] = "error"
    jsonXrayConfig["routing"] = {}
    jsonXrayConfig["routing"]["rules"] = []
    jsonXrayConfig["routing"]["domainStrategy"] = "AsIs"
    jsonXrayConfig["inbounds"] = []
    jsonXrayConfig["inbounds"].append({})
    jsonXrayConfig["inbounds"][0]["port"] = "443"
    jsonXrayConfig["inbounds"][0]["protocol"] = "vless"
    jsonXrayConfig["inbounds"][0]["tag"] = "vless_tls"
    jsonXrayConfig["inbounds"][0]["settings"] = {}
    jsonXrayConfig["inbounds"][0]["settings"]["clients"] = []
    jsonXrayConfig["inbounds"][0]["settings"]["clients"].append({})
    jsonXrayConfig["inbounds"][0]["settings"]["clients"][0]["id"] = uuid
    jsonXrayConfig["inbounds"][0]["settings"]["clients"][0]["email"] = "default@user.xray"
    jsonXrayConfig["inbounds"][0]["settings"]["clients"][0]["flow"] = "xtls-rprx-vision"
    jsonXrayConfig["inbounds"][0]["settings"]["decryption"] = "none"
    jsonXrayConfig["inbounds"][0]["streamSettings"] = {}
    jsonXrayConfig["inbounds"][0]["streamSettings"]["network"] = "tcp"
    jsonXrayConfig["inbounds"][0]["streamSettings"]["security"] = "reality"
    jsonXrayConfig["inbounds"][0]["streamSettings"]["realitySettings"] = {}
    jsonXrayConfig["inbounds"][0]["streamSettings"]["realitySettings"]["show"] = False
    jsonXrayConfig["inbounds"][0]["streamSettings"]["realitySettings"]["dest"] = "twitch.tv:443"
    jsonXrayConfig["inbounds"][0]["streamSettings"]["realitySettings"]["xver"] = 0
    jsonXrayConfig["inbounds"][0]["streamSettings"]["realitySettings"]["serverNames"] = []
    jsonXrayConfig["inbounds"][0]["streamSettings"]["realitySettings"]["serverNames"].append("twitch.tv")
    jsonXrayConfig["inbounds"][0]["streamSettings"]["realitySettings"]["privateKey"] = privateKey
    jsonXrayConfig["inbounds"][0]["streamSettings"]["realitySettings"]["minClientVer"] = ""
    jsonXrayConfig["inbounds"][0]["streamSettings"]["realitySettings"]["maxClientVer"] = ""
    jsonXrayConfig["inbounds"][0]["streamSettings"]["realitySettings"]["maxTimeDiff"] = 0
    jsonXrayConfig["inbounds"][0]["streamSettings"]["realitySettings"]["shortIds"] = []
    jsonXrayConfig["inbounds"][0]["streamSettings"]["realitySettings"]["shortIds"].append(shortId)
    jsonXrayConfig["inbounds"][0]["sniffing"] = {}
    jsonXrayConfig["inbounds"][0]["sniffing"]["enabled"] = True
    jsonXrayConfig["inbounds"][0]["sniffing"]["destOverride"] = []
    jsonXrayConfig["inbounds"][0]["sniffing"]["destOverride"].append("http")
    jsonXrayConfig["inbounds"][0]["sniffing"]["destOverride"].append("tls")
    jsonXrayConfig["outbounds"] = []
    jsonXrayConfig["outbounds"].append({})
    jsonXrayConfig["outbounds"][0]["protocol"] = "freedom"
    jsonXrayConfig["outbounds"][0]["tag"] = "direct"
    jsonXrayConfig["outbounds"].append({})
    jsonXrayConfig["outbounds"][1]["protocol"] = "blackhole"
    jsonXrayConfig["outbounds"][1]["tag"] = "block"
    with open("/opt/xray/config.json", 'w', encoding='utf-8') as jsonXrayConfigFile:
        json.dump(jsonXrayConfig, jsonXrayConfigFile, ensure_ascii=False, indent=4)
    print("Reloading systemd units..")
    daemonReloadProcess = subprocess.Popen(["systemctl", "daemon-reload"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    daemonReloadProcess.wait()
    print("Tuning network stack..")
    with open("/etc/sysctl.d/10-xray.conf", "w") as sysctlConf:
        print("net.core.rmem_max = 67108864", file=sysctlConf)
        print("net.core.wmem_max = 67108864", file=sysctlConf)
        print("net.core.netdev_max_backlog = 10000", file=sysctlConf)
        print("net.core.somaxconn = 4096", file=sysctlConf)
        print("net.ipv4.tcp_syncookies = 1", file=sysctlConf)
        print("net.ipv4.tcp_tw_reuse = 1", file=sysctlConf)
        print("net.ipv4.tcp_fin_timeout = 30", file=sysctlConf)
        print("net.ipv4.tcp_keepalive_time = 1200", file=sysctlConf)
        print("net.ipv4.tcp_keepalive_probes = 5", file=sysctlConf)
        print("net.ipv4.tcp_keepalive_intvl = 30", file=sysctlConf)
        print("net.ipv4.tcp_max_syn_backlog = 8192", file=sysctlConf)
        print("net.ipv4.tcp_max_tw_buckets = 5000", file=sysctlConf)
        print("net.ipv4.tcp_fastopen = 3", file=sysctlConf)
        print("net.ipv4.tcp_mem = 25600 51200 102400", file=sysctlConf)
        print("net.ipv4.udp_mem = 25600 51200 102400", file=sysctlConf)
        print("net.ipv4.tcp_rmem = 4096 87380 67108864", file=sysctlConf)
        print("net.ipv4.tcp_wmem = 4096 65536 67108864", file=sysctlConf)
        print("net.ipv4.tcp_mtu_probing = 1", file=sysctlConf)
        print("net.ipv4.tcp_slow_start_after_idle=0", file=sysctlConf)
    sysctlReloadProcess = subprocess.Popen(["sysctl", "-p", "/etc/sysctl.d/10-xray.conf"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    sysctlReloadProcess.wait()
    print("Starting Xray server..")
    xrayRestartProcess = subprocess.Popen(["systemctl", "restart", "xray"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    xrayRestartProcess.wait()
    print("")
    print("Your default account is:")
    print("UUID:", uuid)
    print("e-Mail: default@user.xray")
    print("Reality Short ID:", shortId)
    print("")
    connectionString = "vless://" + uuid + "@" + hostname + ":443?security=tls&packetEncoding=xudp&sni=twitch.tv&alpn=h2&fp=chrome&pbk=" + publicKey + "&sid=" + shortId + "&type=tcp&flow=xtls-rprx-vision&encryption=none#default@user.xray on " + hostname
    print("Your connection string for Nekobox is:", connectionString)
    print("")
    if not qrInstallFailed:
        qrRequired = input("Would you also like to get a QR-code (y/N)? ")
        match qrRequired:
            case "Y":
                print("")
                qrGenerationProcess = subprocess.Popen(["qrencode", "-t", "ansiutf8", connectionString], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                qrGenerationProcessOutputEncoded, qrGenerationProcessErrorEncoded = qrGenerationProcess.communicate()
                qrCode = qrGenerationProcessOutputEncoded.decode("utf-8").strip()
                print(qrCode)
                print("")
            case "y":
                print("")
                qrGenerationProcess = subprocess.Popen(["qrencode", "-t", "ansiutf8", connectionString], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                qrGenerationProcessOutputEncoded, qrGenerationProcessErrorEncoded = qrGenerationProcess.communicate()
                qrCode = qrGenerationProcessOutputEncoded.decode("utf-8").strip()
                print(qrCode)
                print("")
            case _:
                print("")

def removeXrayServer():
    print("Stopping Xray server..")
    xrayStopProcess = subprocess.Popen(["systemctl", "stop", "xray"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    xrayStopProcess.wait()
    print("Removing /opt/xray contents..")
    os.remove("/opt/xray/config.json")
    os.remove("/opt/xray/geoip.dat")
    os.remove("/opt/xray/geosite.dat")
    os.remove("/opt/xray/hostname")
    os.remove("/opt/xray/LICENSE")
    os.remove("/opt/xray/no-qr")
    os.remove("/opt/xray/public.key")
    os.remove("/opt/xray/README.md")
    os.remove("/opt/xray/short-id")
    os.remove("/opt/xray/xray")
    os.removedirs("/opt/xray")
    print("Removing Xray systemd unit..")
    os.remove("/etc/systemd/system/xray.service")
    print("Removing additional network configs..")
    os.remove("/etc/sysctl.d/10-xray.conf")
    print("Updating systemd..")
    daemonReloadProcess = subprocess.Popen(["systemctl", "daemon-reload"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    daemonReloadProcess.wait()
    print("")

def backupXrayServerConfig():
    print("Backing up Xray server configuration..")
    date = str(datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))
    with zipfile.ZipFile("backup-" + str(date) + ".zip","w") as xrayConfigZip:
        xrayConfigZip.write("/opt/xray/config.json", arcname="config.json")
        xrayConfigZip.write("/opt/xray/hostname", arcname="hostname")
        xrayConfigZip.write("/opt/xray/no-qr", arcname="no-qr")
        xrayConfigZip.write("/opt/xray/public.key", arcname="public.key")
        xrayConfigZip.write("/opt/xray/short-id", arcname="short-id")
    print("Backed up to " + str(os.getcwd()) + "/backup-" + str(date) + ".zip")
    print("")

def restoreXrayServerConfig():
    allBackups = glob.glob("backup-*.zip")
    counter = 0
    for backup in allBackups:
        print(str(counter) + ": " + backup)
        counter += 1
    print("")
    idToEdit = input("Which backup to restore? ")
    try:
        idToEdit = int(idToEdit)
    except:
        print("No changes were made.")
        failureDuringScript("incorrect_id")
    print("Restoring backup..")
    with zipfile.ZipFile(allBackups[idToEdit],"r") as xrayBackupZip:
        xrayBackupZip.extractall("/opt/xray")
    print("")

def failureDuringScript(message):
    print("Failed, reason:", message)
    sys.exit()

workingDirectory = os.getcwd()
if not workingDirectory.startswith("/opt"):
    print("This script will not work until you put it to /opt directory or any of it's subdirectories.")
    sys.exit()
print("")
print("==== Welcome to Xray Manager by CrPO4 ====")
print("Make your choice:")
print("1. Add Xray user")
print("2. Remove Xray user")
print("3. Edit Xray user")
print("4. Show Xray user")
print("5. Install Xray server")
print("6. Remove Xray server")
print("7. Backup Xray server configuration")
print("8. Restore Xray server configuration from backup")
print("")
menuChoice = input("Your choice: ")
try:
    menuChoice = int(menuChoice)
except:
    failureDuringScript("nonIntable_menuChoice")
print("")
match menuChoice:
    case 1:
        addXrayUser()
    case 2:
        removeXrayUser()
    case 3:
        editXrayUser()
    case 4:
        showXrayUser()
    case 5:
        installXrayServer()
    case 6:
        removeXrayServer()
    case 7:
        backupXrayServerConfig()
    case 8:
        restoreXrayServerConfig()
    case _:
        failureDuringScript("wrong_menuChoice")
