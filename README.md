# Fun API Project

A RESTful web application using the Python framework Flask and third-party OAuth authentication to allow users to post, edit, and delete their own APIs in a fun API catalog with a variety of categories. The web application appropriately maps HTTP methods to CRUD operations.

The `api` database includes three tables:

- The `user` table includes information (name, email, picture) about the users of the application.
- The `api_category` table includes the categories Trivia, Games, Lyrics,and Humor.
- The `api` table includes API entries (title, description, url) in each category.

The application allows for the following user operations:

1. Add an API to one of the categories
2. Edit an API's values and category (if user is authorized)
3. Delete an API (if user is authorized)

## Requirements

- [Vagrant](https://www.vagrantup.com/downloads.html)
- [VirtualBox](https://www.virtualbox.org/wiki/Download_Old_Builds_5_1)

### VirtualBox

VirtualBox is the software that actually runs the VM. [You can download it from virtualbox.org, here.](https://www.virtualbox.org/wiki/Downloads)  Install the *platform package* for your operating system.  You do not need the extension pack or the SDK. You do not need to launch VirtualBox after installing it.

**Ubuntu 14.04 Note:** If you are running Ubuntu 14.04, install VirtualBox using the Ubuntu Software Center, not the virtualbox.org web site. Due to a [reported bug](http://ubuntuforums.org/showthread.php?t=2227131), installing VirtualBox from the site may uninstall other software you need.

### Vagrant

Vagrant is the software that configures the VM and lets you share files between your host computer and the VM's filesystem.  [You can download it from vagrantup.com.](https://www.vagrantup.com/downloads) Install the version for your operating system.

**Windows Note:** The Installer may ask you to grant network permissions to Vagrant or make a firewall exception. Be sure to allow this.

### Run the virtual machine!

Using the terminal, clone this project and change directory to catalog (**cd catalog**), then type **vagrant up** to launch your virtual machine.

## Running the Fun API Application

Once your virtual machine is up and running, type **vagrant ssh**. This will log your terminal into the VM, and you'll get a Linux shell prompt. When you want to log out, type **exit** at the shell prompt.  To turn the virtual machine off (without deleting anything), type **vagrant halt**. If you do this, you'll need to run **vagrant up** again before you can log into it.

Now that you have Vagrant up and running type **vagrant ssh** to log into your VM. Change to the /vagrant directory by typing **cd /vagrant**. This will take you to the shared folder between your virtual machine and host machine.

Type **ls** to ensure that you are inside the directory that contains application.py, database_setup.py, and two directories named 'templates' and 'static'.

Now type **python database_setup.py** to initialize the database.

Type **python lotsofapis.py** to populate the database with the API categories and respective APIs.

Type **python application.py** to run the Flask web server. In your browser visit **http://localhost:5000** to view the API app.  You should be able to view, add, edit, and delete APIs to any of the four categories.

### API Endpoint

The app's API endpoint can be accessed at /catalog.json.

### Authentication

This application handles authentication through Google OAuth 2.0. Replace the credentials in client_secrets.json with your own.

## Contributing

Pull requests will not be accepted, as this project was created for the FSND Udacity program.

For details, check out [CONTRIBUTING.md](CONTRIBUTING.md).