import subprocess
import time
import os

VM_NAME     = "AUG-NB1"
SHARE_PATH  = os.path.expanduser("~/Schreibtisch/Share/VM")
VBOXMANAGE  = "/usr/bin/VBoxManage"
SCRIPT_NAME = "auto_fehler.ps1"
TRIGGER_NAME = "run_trigger.txt"

def run(cmd, check=True, timeout=30):
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        if check and result.returncode != 0:
            raise Exception(result.stderr.strip() or result.stdout.strip())
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        raise Exception(f"Timeout nach {timeout}s")

def vm_status():
    out = run([VBOXMANAGE, "showvminfo", VM_NAME, "--machinereadable"], check=False)
    for line in out.splitlines():
        if line.startswith("VMState="):
            return line.split("=")[1].strip('"')
    return "unknown"

def vm_start():
    status = vm_status()
    if status == "running":
        print("[OK] VM läuft bereits")
        return False  # war schon an
    print(f"[>>] VM starten...")
    run([VBOXMANAGE, "startvm", VM_NAME, "--type", "gui"], timeout=30)
    print("[>>] Warte 60s bis Windows hochgefahren ist...")
    time.sleep(60)
    print("[OK] VM gestartet")
    return True  # wurde neu gestartet

def vm_snapshot_restore(snapshot_name="Sauber"):
    status = vm_status()
    if status == "running":
        print("[>>] VM stoppen...")
        run([VBOXMANAGE, "controlvm", VM_NAME, "poweroff"], timeout=15)
        time.sleep(3)
    print(f"[>>] Snapshot '{snapshot_name}' wiederherstellen...")
    run([VBOXMANAGE, "snapshot", VM_NAME, "restore", snapshot_name], timeout=30)
    print("[OK] Snapshot wiederhergestellt")

def write_script(powershell_code: str):
    """
    Schreibt zwei Dateien in den Shared Folder:
    1. Das eigentliche PS1-Skript
    2. Eine Launcher-BAT die das Skript beim Windows-Start ausführt
    """
    os.makedirs(SHARE_PATH, exist_ok=True)

    # PS1-Skript schreiben
    ps_path = os.path.join(SHARE_PATH, SCRIPT_NAME)
    with open(ps_path, "w", encoding="utf-8") as f:
        f.write("Set-ExecutionPolicy Bypass -Scope Process -Force\n")
        f.write(powershell_code)
        # Nach Ausführung Trigger-Datei löschen
        f.write(f'\nRemove-Item "\\\\VBOXSVR\\VMShare\\{TRIGGER_NAME}" -Force -ErrorAction SilentlyContinue\n')
    print(f"[OK] Skript gespeichert: {ps_path}")

    # Trigger-Datei schreiben (signalisiert dass Skript ausgeführt werden soll)
    trigger_path = os.path.join(SHARE_PATH, TRIGGER_NAME)
    with open(trigger_path, "w") as f:
        f.write("run")
    print(f"[OK] Trigger gespeichert: {trigger_path}")

    # BAT-Launcher schreiben (wird per Autostart in Windows aufgerufen)
    bat_path = os.path.join(SHARE_PATH, "launcher.bat")
    with open(bat_path, "w") as f:
        f.write(f'@echo off\n')
        f.write(f'if exist "\\\\VBOXSVR\\VMShare\\{TRIGGER_NAME}" (\n')
        f.write(f'    powershell.exe -ExecutionPolicy Bypass -File "\\\\VBOXSVR\\VMShare\\{SCRIPT_NAME}"\n')
        f.write(f')\n')
    print(f"[OK] Launcher gespeichert: {bat_path}")

def prepare_vm(powershell_code: str, restore_snapshot=False, snapshot_name="Sauber"):
    try:
        if restore_snapshot:
            vm_snapshot_restore(snapshot_name)

        # Skripte in Shared Folder schreiben
        write_script(powershell_code)

        # VM starten
        was_off = not (vm_status() == "running")
        vm_start()

        return {
            "ok": True,
            "message": "VM gestartet. Führe jetzt in der VM einmalig den Autostart ein (siehe Anleitung) oder starte das Skript manuell.",
            "manual_command": f'powershell.exe -ExecutionPolicy Bypass -File "\\\\VBOXSVR\\VMShare\\{SCRIPT_NAME}"',
            "share_path": f"\\\\VBOXSVR\\VMShare\\{SCRIPT_NAME}"
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}
