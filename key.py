from getpass import getpass
from web3.eth import Account
import json

class InvalidInputError(Exception):
    '''Class for invalid user input'''
    pass

def import_new_privatekey(to_filepath):
    '''Import a new private key and store it locally at filepath'''
    private_key = request_private_key()
    keystore_password = request_new_password()
    store_private_key(private_key, keystore_password, filepath = to_filepath)
    print("Your private key has been imported with success !\n")

def request_private_key(max_attempts = 3):
    print("Please paste your private key here :")
    valid_private_key = False
    attempts = 0
    while not valid_private_key and attempts < max_attempts:
        private_key = getpass("")
        valid_private_key = is_valid_private_key(private_key)
        if not valid_private_key:
            print("Invalid private key, please try again:")
            attempts = attempts + 1
    
    if not valid_private_key:
        raise InvalidInputError("Too many attempts")
    
    print("This private key is correct\n")
    return private_key

def request_new_password(max_attempts = 3):
    valid_pwd = False
    attempts = 0
    while not valid_pwd and attempts < max_attempts:
        print("Please type a new password to encrypt that private key on your hard drive - CAREFUL DON'T FORGET THIS PASSWORD")
        pwd1 = getpass("")
        print("Please type your new password again")
        pwd2 = getpass("")
        valid_pwd = pwd1 == pwd2
        if not valid_pwd:
            attempts = attempts + 1
            print("Doesn't match, let's do it again")
    
    if not valid_pwd:
        raise InvalidInputError("Too many attempts")
    print("Password set\n")
    return pwd1

def is_valid_private_key(private_key):
    try:
        Account.from_key(private_key)
        return True
    except:
        return False

def store_private_key(private_key, password, filepath):
    '''Encrypt key with password and store it at filepath'''
    keystore_dict = Account.encrypt(private_key, password)
    with open(filepath, "x") as f:
        json.dump(keystore_dict, f)

def load_private_key(filepath, password):
    '''Load encrypted private key from file. May raise InvalidInputError.'''
    try:
        with open(filepath) as keyfile:
            encrypted_key = json.load(keyfile)
            private_key = Account.decrypt(encrypted_key, password)
    except FileNotFoundError as e:
        raise InvalidInputError("Invalid path to private key file")
    except ValueError:
        raise InvalidInputError("Invalid password provided")
    return private_key


def unlock_private_key(filepath):
    '''
    Prompts the user for the keyfile password and return the decrypted private_key.
    Raises InvalidInputError if the file or the entered password is invalid.
    '''
    print("Please enter you password to continue :")
    password = getpass("")
    private_key = load_private_key(filepath, password)
    return private_key

def load_address(filepath):
    '''Load address from keyfile (no need to decrypt)'''
    with open(filepath) as keyfile:
        json_dump = json.load(keyfile)
        owner_address = "0x" + json_dump['address']
    return owner_address

