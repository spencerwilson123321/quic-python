from os.path import isfile

DB_FILE = "./database.txt"
WRITE = "w"
READ = "r"
APPEND = "a"

class Database:

    def __init__(self, filepath=DB_FILE):
        self.filepath = filepath
        if not isfile(self.filepath):
            # If the file doesn't exist, then create it.
            with open(self.filepath, WRITE) as f:
                pass

    def exists(self, username: str, password: str) -> bool:
        """
            Returns true if the given username and password are found in the database file.
        """
        with open(self.filepath, READ) as database:
            entries = database.readlines()
            for entry in entries:
                entry = entry.strip()
                if not entry:
                    continue
                usr, pwd = entry.split(":")
                if username == usr and password == pwd:
                    return True
        return False


    def add(self, username: str, password: str) -> bool:
        """
            Attempts to add a username and password to the database file.
            Returns true if success, and false for failure.
        """
        if self.exists(username, password):
            return False
        with open(self.filepath, APPEND) as database:
            database.write(f"{username}:{password}")
        return True    


    def remove(self, username: str, password: str) -> bool:
        """
            Attempts to remove a username and password from the database file.
            Returns true if success, false is failure.
        """
        entries = None
        removed = False
        with open(self.filepath, READ) as database:
            entries = database.readlines()
        with open(self.filepath, WRITE) as database:
            for entry in entries:
                if entry.strip() != f"{username}:{password}":
                    database.write(entry)
                else:
                    removed = True
        return removed


    def clear(self) -> None:
        """
            Erases the contents of the database file.
        """
        with open(self.filepath, WRITE) as f:
            pass

