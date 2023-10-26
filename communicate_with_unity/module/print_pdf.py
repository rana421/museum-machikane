import subprocess, winreg

def get_acrobat_reader_path():
    key_path = r"Software\Microsoft\Windows\CurrentVersion\App Paths\Acrobat.exe"
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
            path, _ = winreg.QueryValueEx(key, None)
            return path
    except FileNotFoundError:
        return None

def send_printer(pdffile, printer_name):
    # acroread = r'C:\Program Files (x86)\Adobe\Reader 11.0\Reader\AcroRd32.exe'
    #acrobat = r'C:\Program Files\Adobe\Acrobat DC\Acrobat\Acrobat.exe'
    acrobat = get_acrobat_reader_path()

    cmd = '"{}" /n /t "{}" "{}"'.format(acrobat, pdffile, printer_name)
    # cmd = '"{}" /p /h "{}""'.format(acrobat, pdffile)
    print(cmd)

    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate()
    #exit_code = proc.wait()

    # とりあえずこれでよさそう
    proc.kill()


if __name__ == '__main__':
    pdffile = "./../PDFcreator/sample.pdf"
    printer_name = "Brother MFC-L2750DW E302"
    # printer_name = "Brother MFC-L2750DW_kanemoto" 
    send_printer(pdffile, printer_name)