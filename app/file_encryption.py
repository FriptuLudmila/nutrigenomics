"""
File Encryption Module
======================
Handles encryption/decryption of uploaded genetic data files.
Uses Fernet symmetric encryption (AES-128-CBC).
"""

import os
from pathlib import Path
from typing import Optional
from .encryption import get_encryptor


def encrypt_file(input_path: str, output_path: Optional[str] = None) -> str:
    """
    Encrypt a file on disk.

    Args:
        input_path: Path to the file to encrypt
        output_path: Optional path for encrypted file. If not provided,
                    adds .encrypted extension to input_path

    Returns:
        Path to the encrypted file
    """
    if output_path is None:
        output_path = f"{input_path}.encrypted"

    # Get encryptor
    encryptor = get_encryptor()

    # Read file in chunks for memory efficiency
    chunk_size = 64 * 1024  # 64KB chunks

    with open(input_path, 'rb') as f_in:
        # Read entire file (genetic data files are typically small)
        file_data = f_in.read()

    # Encrypt the entire file content
    encrypted_data = encryptor.cipher.encrypt(file_data)

    # Write encrypted data
    with open(output_path, 'wb') as f_out:
        f_out.write(encrypted_data)

    return output_path


def decrypt_file(input_path: str, output_path: Optional[str] = None) -> str:
    """
    Decrypt an encrypted file.

    Args:
        input_path: Path to the encrypted file
        output_path: Optional path for decrypted file. If not provided,
                    removes .encrypted extension from input_path

    Returns:
        Path to the decrypted file
    """
    if output_path is None:
        if input_path.endswith('.encrypted'):
            output_path = input_path[:-10]  # Remove .encrypted
        else:
            output_path = f"{input_path}.decrypted"

    # Get encryptor
    encryptor = get_encryptor()

    # Read encrypted file
    with open(input_path, 'rb') as f_in:
        encrypted_data = f_in.read()

    # Decrypt
    decrypted_data = encryptor.cipher.decrypt(encrypted_data)

    # Write decrypted data
    with open(output_path, 'wb') as f_out:
        f_out.write(decrypted_data)

    return output_path


def encrypt_and_replace(file_path: str, keep_original: bool = False) -> str:
    """
    Encrypt a file and optionally replace the original.

    Args:
        file_path: Path to the file to encrypt
        keep_original: If False, deletes the original file after encryption

    Returns:
        Path to the encrypted file
    """
    encrypted_path = encrypt_file(file_path)

    if not keep_original:
        try:
            os.remove(file_path)
            print(f"[SECURITY] Original file deleted: {file_path}")
        except Exception as e:
            print(f"[WARNING] Failed to delete original file: {e}")

    return encrypted_path


def decrypt_and_replace(encrypted_path: str, keep_encrypted: bool = False) -> str:
    """
    Decrypt a file and optionally remove the encrypted version.

    Args:
        encrypted_path: Path to the encrypted file
        keep_encrypted: If False, deletes the encrypted file after decryption

    Returns:
        Path to the decrypted file
    """
    decrypted_path = decrypt_file(encrypted_path)

    if not keep_encrypted:
        try:
            os.remove(encrypted_path)
            print(f"[SECURITY] Encrypted file deleted: {encrypted_path}")
        except Exception as e:
            print(f"[WARNING] Failed to delete encrypted file: {e}")

    return decrypted_path


def secure_delete_file(file_path: str, overwrite_passes: int = 3) -> bool:
    """
    Securely delete a file by overwriting it before deletion.

    Args:
        file_path: Path to the file to delete
        overwrite_passes: Number of times to overwrite with random data

    Returns:
        True if successful, False otherwise
    """
    try:
        if not os.path.exists(file_path):
            return True

        file_size = os.path.getsize(file_path)

        # Overwrite file with random data multiple times
        with open(file_path, 'wb') as f:
            for _ in range(overwrite_passes):
                f.seek(0)
                f.write(os.urandom(file_size))
                f.flush()
                os.fsync(f.fileno())

        # Finally delete the file
        os.remove(file_path)
        print(f"[SECURITY] File securely deleted: {file_path}")
        return True

    except Exception as e:
        print(f"[ERROR] Failed to securely delete file: {e}")
        return False


def cleanup_session_files(session_filepath: str, secure: bool = True) -> bool:
    """
    Clean up files associated with a session.

    Args:
        session_filepath: Path to the session's file
        secure: If True, uses secure deletion (slower but more secure)

    Returns:
        True if successful, False otherwise
    """
    try:
        # Handle encrypted files
        encrypted_path = f"{session_filepath}.encrypted"

        # Delete encrypted file if it exists
        if os.path.exists(encrypted_path):
            if secure:
                secure_delete_file(encrypted_path)
            else:
                os.remove(encrypted_path)
                print(f"[SECURITY] Encrypted file deleted: {encrypted_path}")

        # Delete original file if it still exists
        if os.path.exists(session_filepath):
            if secure:
                secure_delete_file(session_filepath)
            else:
                os.remove(session_filepath)
                print(f"[SECURITY] Original file deleted: {session_filepath}")

        return True

    except Exception as e:
        print(f"[ERROR] Failed to cleanup session files: {e}")
        return False
