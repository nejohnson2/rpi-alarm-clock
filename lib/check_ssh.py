'''
Script to monitor ssh running on 
a raspberry pi.  If ssh is not
currently active, then reboot.
'''
import subprocess

def main():
	cmd = subprocess.Popen("service ssh status", shell=True, stdout=subprocess.PIPE)

	for line in cmd.stdout:
		if "Active: " in line:
			if "active" in line.split(' '):
				return
			else:
				subprocess.call(['sudo','service', 'ssh','restart'])
				return


if __name__ == '__main__':
	main()
