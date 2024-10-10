import os
print(os.name)
import subprocess

#os.chdir(os.path.dirname(os.path.abspath(__file__))) #カレントディレクトリを固定
def get_acrobat_reader_path():
    import winreg
    key_path = r"Software\Microsoft\Windows\CurrentVersion\App Paths\Acrobat.exe"
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
            path, _ = winreg.QueryValueEx(key, None)
            return path
    except FileNotFoundError:
        return None

def send_printer(pdffile, printer_name):

    if os.name =="posix":
        #OSがmac系であればこの操作
        cmd = ['lpr','-o media=A4','-o fit-to-page', '-P', printer_name, pdffile]
        print(' '.join(cmd))

    elif os.name =="nt":
        #osがwindows系であればこれ
        # acroread = r'C:\Program Files (x86)\Adobe\Reader 11.0\Reader\AcroRd32.exe'
        #acrobat = r'C:\Program Files\Adobe\Acrobat DC\Acrobat\Acrobat.exe'
        acrobat = get_acrobat_reader_path()

        cmd = '"{}" /n /t "{}" "{}"'.format(acrobat, pdffile, printer_name)
        # cmd = '"{}" /p /h "{}""'.format(acrobat, pdffile)

    print(cmd)

    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate()

    if stderr:
        print(f"Error: {stderr.decode()}")
    #exit_code = proc.wait()

    # とりあえずこれでよさそう
    proc.kill()


if __name__ == '__main__':
    path = os.getcwd()
    print(path)
    print(os.listdir())
    pdffile = "./PDFcreator/sample.pdf"
    #printer_name = "Brother MFC-L2750DW E302"
    # printer_name = "EPSON_EP_883A_Series"
    
    #printer_name = "Brother_MFC_L2750DW_series__b42200a0521e_"
    printer_name = "EPSON_EW_M973A3T_Series"
    # printer_name = "Brother MFC-L2750DW_kanemoto" 
    send_printer(pdffile, printer_name)
