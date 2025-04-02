# PortScanner
![immagine](https://github.com/user-attachments/assets/70463ee9-9151-48ef-89bf-a264bd153e6a)

This Python script is a graphical application that allows you to scan the ports of multiple hosts, display the results in real-time, and save them to a log file. The application is built using the tkinter library, which provides a simple graphical interface for the user.
How the script works:

    File selection: The user selects a text file that contains a list of hosts and the respective ports to scan. Each line of the file should be in the format: host,port1,port2,port3,..., where:

        host: The IP address or domain name of the host you want to scan.

        port1, port2, port3,...: A list of ports to scan for the specified host.

    For example, a valid file might look like this:

    192.168.1.1,80,443,8080
    example.com,22,25,53
    10.0.0.2,3306,443

    Port scanning execution: When the user starts the scan, the script attempts to connect to each host and checks the specified ports. The connections are checked in parallel using threads to improve performance.

    Displaying the results: The scan results (success or failure for each port) are displayed in real-time in the graphical interface. Additionally, a progress bar shows the status of the scan.

    Creating a log file: At the end of the scan, the results are saved to a log file, which contains detailed information about each host and port tested.

Requirements:

To run this script correctly, Python 3.x must be installed. The script uses the following standard Python modules:

    os: for filesystem operations.

    sys: for interacting with system parameters.

    socket: for connecting to ports.

    threading: for running the port scan in parallel.

    queue: for managing communication between threads.

    tkinter: for the graphical interface.

Pre-compiled executable:

For convenience, a pre-compiled version of this application is available as app.exe, which is the Windows executable version of the code. This version allows you to run the application without needing to install Python. Simply run the app.exe file to use the port scanner.

This script is useful for network administrators, security testers, or anyone who needs to check the availability of ports on multiple hosts in a simple and efficient manner.

    concurrent.futures: for running the port scan concurrently.

The application is designed to be user-friendly, with a graphical window that allows the user to select the input file and start the scan with a simple click. After the scan completes, the results are displayed directly in the interface, and a detailed log file is created.This script creates a graphical application for scanning the ports of multiple hosts
