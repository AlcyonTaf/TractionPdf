import subprocess


def run(script):
    completed = subprocess.run(["powershell", "C:\\Users\\CRMC\\PycharmProjects\\TractionPdf\\test.ps1"],
                               capture_output=True)
    print(completed)
    return completed


if __name__ == '__main__':
    #script_path = "C:\Users\CRMC\PycharmProjects\TractionPdf\test.ps1"
    hello_info = run('test')
    print(hello_info.stderr)
    if hello_info.returncode != 0:
        print("An error occured: %s", hello_info.stderr)
    else:
        print("Hello command executed successfully!")

    print("-------------------------")
