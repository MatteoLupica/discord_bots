import os
import json
from config.config import USERS_FILE
class Users:
    def __init__(self, file_path=USERS_FILE):
        """
        Initialize the Users class.
        
        Parameters:
            file_path (str): The path to the JSON file storing user data.
        """
        self.file_path = file_path
        self.users = {}
        self.load_users()

    def load_users(self):
        """
        Load users from the JSON file. If the file doesn't exist, start with an empty dictionary.
        """
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    self.users = json.load(f)
            except Exception as e:
                raise Exception(f"Error loading users file: {e}")
        else:
            self.users = {}

    def save_users(self):
        """
        Save the current users dictionary to the JSON file.
        """
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(self.users, f, indent=4)
        except Exception as e:
            raise Exception(f"Error saving users file: {e}")

    def register_user(self, discord_id, game_name, tag, role):
        """
        Register a new user or update an existing user profile.
        
        Parameters:
            discord_id (str): The Discord user ID.
            game_name (str): The in-game name.
            tag (str): The in-game tag.
            role (str): The player's role.
        
        Returns:
            dict: The updated user profile.
        """
        self.users[discord_id] = {
            "game_name": game_name,
            "tag": tag,
            "role": role
        }
        self.save_users()
        return self.users[discord_id]

    def get_user(self, discord_id):
        """
        Retrieve a user profile by Discord ID.
        
        Parameters:
            discord_id (str): The Discord user ID.
        
        Returns:
            dict or None: The user profile if found, or None if not registered.
        """
        return self.users.get(discord_id)

    def get_all_users(self):
        """
        Return all registered users.
        
        Returns:
            dict: A dictionary of all user profiles.
        """
        return self.users

    def update_user(self, discord_id, game_name=None, tag=None, role=None):
        """
        Update an existing user's profile fields.
        
        Parameters:
            discord_id (str): The Discord user ID.
            game_name (str, optional): A new game name.
            tag (str, optional): A new tag.
            role (str, optional): A new role.
        
        Returns:
            dict: The updated user profile.
        
        Raises:
            Exception: If the user does not exist.
        """
        if discord_id not in self.users:
            raise Exception("User not found.")
        
        if game_name:
            self.users[discord_id]["game_name"] = game_name
        if tag:
            self.users[discord_id]["tag"] = tag
        if role:
            self.users[discord_id]["role"] = role
        
        self.save_users()
        return self.users[discord_id]
    
    def to_string(self, discord_id):
        return self.users[discord_id]["game_name"] + "#" + self.users[discord_id]["tag"]
