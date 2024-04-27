# LNKGenerator
Simple script program to generate LNKs that execute custom commands. Includes possibility to attach files into the LNK that will be extracted and executed upon execution.

## Installation
LNKGenerator uses **python3**, all dependencies can be installed with:
```
pip install -r requirements.txt
```

## Usage
```
python3 LNKGenerator.py <LNK_PATH> [arguments]
```

| Parameter | Long Option | Required| Default Value | Description |
|-----------|-----------|-----------|-----------|-----------|
| lnk_file | | Yes | | Name of the LNK to generate |
| -r | --interpreter | No | cmd | Interpreter to use cmd or powershell |              
| -c | --command | No |  | Command arguments to execute                                       |
| -i | --icon    | No | 0 | Icon index in C:\Windows\System32\shell32.dll                      |
| -a | --attachments | No |  | Path to files to append to LNK, files will be extracted and opened on LNK execution. Repeat argument for more files. If attachments are used the generated LNK will use powershell. |

## Usage Example
Generate an LNK that executes a custom command
```
python3 LNKGenerator.py file.lnk -c 'echo 4278278 > %temp%\\password.txt & start %temp%\\password.txt && calc.exe'
```

Generate a LNK with two files attached that will be extracted and executed. Files previously exist.
```
python3 LNKGenerator.py -a DummyFiles\FILE.pdf -a DummyFiles\script.bat
```

## Remarks
For some reason, the generation of LNKs is failing on some machines if we don't have support for UTF8 Characters on the system. In order to enable this go to: `Region & language` -> `Language` -> `Administrative language settings` -> `Change system locale` -> check `Use Unicode UTF-8 for worldwide language support`

If attachments are used the generated LNK will use powershell.

## Limitations
Powershell cannot be used as the parent interpreter for the attachment option

# TODO
- [ ] Check how command + Attachments interact...
- [ ] Fix attachment execution With Powershell (Command cannot be executed due to errors during scaping...)
- [ ] Allow to define path to extract attached files
- [ ] Add option to encrypt attached items
- [ ] Add option to generate some default files 
- [ ] Allow to define WindowStyle of LNK 
- [ ] USe configuration files instead of commandline parameters (Easier to add more options for attachment files like output dir, encription, and others)
- [ ] Improve loop efficiency
- [ ] Rethink how command and extractions are combined.