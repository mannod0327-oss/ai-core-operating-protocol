$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
python "$ScriptDir/install.py" @args
exit $LASTEXITCODE
