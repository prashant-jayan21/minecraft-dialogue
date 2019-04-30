function Check-Error
{
    # generates an exit code depending on error status
    if ($error)
    {
        Start-Sleep 3
        exit 1
    }
    else
    {
        Start-Sleep 3
        exit 0
    }
}

function Get-InstalledApps
{
    # Cribbed from here: http://stackoverflow.com/a/31714410
    $regpath = @(
        'HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*'
        'HKLM:\Software\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*'
    )
    Get-ItemProperty $regpath | .{process{if($_.DisplayName -and $_.UninstallString) { $_ } }} | Select DisplayName, Publisher, InstallDate, DisplayVersion, UninstallString |Sort DisplayName
}

function Append-Path
{
    # This function was cribbed from Peter Hahndorf's work here: https://peter.hahndorf.eu/blog/AddingToPathVariable.html
    # It avoids the common mistake of butchering the registry's path variable.
    Write-Host Adding $args[0] to PATH
    $regPath = "SYSTEM\CurrentControlSet\Control\Session Manager\Environment"
    $hklm = [Microsoft.Win32.Registry]::LocalMachine
    $regKey = $hklm.OpenSubKey($regPath, $FALSE)
    $oldpath = $regKey.GetValue("Path", "", [Microsoft.Win32.RegistryValueOptions]::DoNotExpandEnvironmentNames)
    $newLocation = $args[0]
    # Is location already in the path?
    $parts = $oldPath.split(";")
    If ($parts -contains $newLocation)
    {
        Write-Warning "Not added - already exists."
        Return
    }
    $newPath = $oldPath + ";" + $newLocation
    # Add to the current session:
    $env:path += ";$newLocation"
    # And save into registry:
    $regKey = $hklm.OpenSubKey($regPath, $TRUE)
    $regKey.SetValue("Path", $newPath, [Microsoft.Win32.RegistryValueKind]::ExpandString)
}

function Should-Install
{
    $installedapps = Get-InstalledApps
    $target = $args[0]
    $result = $installedapps | where {$_.DisplayName -match [regex]::escape($target)}
    if ($result)
    {
        return $False
    }
    return $True
}

function Download-File
{
    Write-Host Downloading $args[0] to $args[1] ...
    $client = new-object System.Net.WebClient 
    $client.downloadFile($args[0], $args[1])
    if ($?)
    {
        Write-Host Downloaded.
    }
    else
    {
        Write-Host FAILED TO DOWNLOAD - ABORTING
        Start-Sleep 3
        exit 1
    }
}

function Display-Heading
{
    Write-Host
    Write-Host ("="*($args[0].Length))
    Write-Host $args[0]
    Write-Host ("="*($args[0].Length))
    Write-Host
}

function Install-7Zip
{
    if (Should-Install "7-Zip")
    {
        Display-Heading "Installing 7-Zip"
        Download-File "http://www.7-zip.org/a/7z1604-x64.exe" ($env:HOMEPATH + "\temp\7z_install.exe")
        &.\temp\7z_install.exe /S | Out-Host
        if (-Not $?)
        {
            Write-Host "FAILED TO INSTALL 7-ZIP"
            Start-Sleep 3
            exit 1
        }
    }
    Write-Host "7-Zip already installed."
    return $True
}

function Install-Ffmpeg
{
    if ($env:path -notmatch "ffmpeg")
    {
        Display-Heading "Installing ffmpeg"
        Download-File "http://ffmpeg.zeranoe.com/builds/win64/static/ffmpeg-latest-win64-static.zip" ($env:HOMEPATH + "\temp\ffmpeg.zip")
        & 'C:\Program Files\7-Zip\7z.exe' x .\temp\ffmpeg.zip -oC:\ffmpeg | Out-Host
        if ($?)
        {
            cp -r C:\ffmpeg\ffmpeg-latest-win64-static\* C:\ffmpeg
            rm -r C:\ffmpeg\ffmpeg-latest-win64-static
            if ($?)
            {
                Append-Path "C:\ffmpeg\bin"
                return $True
            }
        }
        Write-Host "FAILED TO INSTALL"
        Start-Sleep 3
        exit 1
    }
    Write-Host "FFMPEG already installed."
    return $True
}

# Install JAVA:
function Install-Java
{
    if (Should-Install "Java SE Development")
    {
        Display-Heading "Installing java"
        $source = "http://download.oracle.com/otn-pub/java/jdk/8u131-b11/d54c1d3a095b4ff2b6607d096fa80163/jdk-8u131-windows-x64.exe"
        $destination = ($env:HOMEPATH + "\temp\jdkinstaller.exe")
        $client = new-object System.Net.WebClient 
        # Need to do some cookie business to sign the oracle licence agreement:
        $cookie = "oraclelicense=accept-securebackup-cookie"
        $client.Headers.Add([System.Net.HttpRequestHeader]::Cookie, $cookie) 
        # Download Java:
        $client.downloadFile($source, $destination)
        if (-Not $?)
        {
            Write-Host "FAILED TO DOWNLOAD JAVA"
            Start-Sleep 3
            exit 1
        }
        # Silently install:
        .\temp\jdkinstaller.exe /s ADDLOCAL="ToolsFeature,SourceFeature,PublicjreFeature" | Out-Host
        if ($?)
        {
            # Add environment variables:
            [Environment]::SetEnvironmentVariable("JAVA_HOME", "C:\Program Files\Java\jdk1.8.0_131", "Machine")
            [Environment]::SetEnvironmentVariable("JAVA_HOME", "C:\Program Files\Java\jdk1.8.0_131", "Process")
            Append-Path "C:\Program Files\Java\jdk1.8.0_131\bin"
            return $True
        }
        Write-Host "FAILED TO INSTALL JAVA"
        Start-Sleep 3
        exit 1
    }
    Write-Host "Java already installed."
    return $True
}

function Install-Python2
{
    if (Should-Install "Python 2.7")
    {
        Display-Heading "Installing python"
        Download-File "https://www.python.org/ftp/python/2.7.12/python-2.7.12.amd64.msi" ($env:HOMEPATH + "\temp\python_install.msi")
        Start-Process .\temp\python_install.msi -ArgumentList "/qn" -Wait
        if ($?)
        {
            Append-Path "C:\Python27"
            return $True
        }
        Write-Host "FAILED TO INSTALL PYTHON 2"
        Start-Sleep 3
        exit 1
    }
    Write-Host "Python2 already installed."
}

function Install-Python3
{
    if (Should-Install "Python 3.6")
    {
        Display-Heading "Installing python"
        Download-File "https://www.python.org/ftp/python/3.6.3/python-3.6.3-amd64.exe" ($env:HOMEPATH + "\temp\python_install.exe")
        Start-Process .\temp\python_install.exe -ArgumentList "/quiet PrependPath=1" -Wait
        if ($?)
        {
            return $True
        }
        Write-Host "FAILED TO INSTALL PYTHON3"
        Start-Sleep 3
        exit 1
    }
    Write-Host "Python3 already installed."
}

function Add-MalmoXSDPathEnv
{
    $malmopath = $args[0]
    [Environment]::SetEnvironmentVariable("MALMO_XSD_PATH", $malmopath + "\Schemas", "User")
    [Environment]::SetEnvironmentVariable("MALMO_XSD_PATH", $malmopath + "\Schemas", "Process")
}

function Install-Mesa
{
    if (-Not (Test-Path ($env:HOMEPATH + "\temp\mesa.7z")))
    {
        Display-Heading "Installing Mesa software renderer"
        Download-File "http://download.qt.io/development_releases/prebuilt/llvmpipe/windows/opengl32sw-64.7z" ($env:HOMEPATH + "\temp\mesa.7z")
        & 'C:\Program Files\7-Zip\7z.exe' x .\temp\mesa.7z '-o.\temp\mesa' | Out-Host
        if (-Not $?)
        {
            Write-Host "FAILED TO INSTALL MESA"
            Start-Sleep 3
            exit 1
        }
        mv .\temp\mesa\opengl32sw.dll .\temp\mesa\opengl32.dll
        cp .\temp\mesa\opengl32.dll "$env:JAVA_HOME\bin"
        if (-Not $?)
        {
            Write-Host "SOFTWARE RENDERER NOT ADDED TO JAVA HOME"
            Start-Sleep 3
            exit 1
        }
    }
    else
    {
        Write-Host "Mesa already installed."
    }
}
