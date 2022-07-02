import subprocess

vspscriptfname = "wing.vspscript"

subprocess.run(["vsp", "-script", vspscriptfname])
