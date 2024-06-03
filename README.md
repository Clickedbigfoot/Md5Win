# Md5Win
Convenient md5sum support on windows for linux enjoyers

Tired of typing out long Get-FileHash commands in powershell? Wistful for the days of linux where you could just type "md5 tab"? Envious of being able to use glob in your md5sum calculations? This small code composition helps solve that.

Simply download both md5sum.py and md5sum.bat and place them both in a directory that is in your PATH. Then, you can easily use the linux md5sum command as you remember it by running "md5sum.bat" in powershell.

Unfortunately, this does not yet have -c checking support for md5, but this is still a great start.
