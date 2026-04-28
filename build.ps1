pyinstaller --noconfirm .\depo-reformat.spec
compress-archive -force -path .\dist\depo-reformat.exe -destinationpath .\depo-reformat.zip
