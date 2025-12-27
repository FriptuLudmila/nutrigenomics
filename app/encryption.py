"""
Encryption Module
=================
Handles encryption/decryption of sensitive genetic data.
Uses Fernet symmetric encryption (AES-128-CBC).
"""

import os
import json
import base64
from cryptography.fernet import Fernet
from typing import Union, Dict, Any


class GeneticDataEncryption:
    """
    Encryption handler for genetic data.
    
    Usage:
        encryptor = GeneticDataEncryption()
        
        # Encrypt genetic findings before storing in database
        encrypted = encryptor.encrypt_data(genetic_findings)
        
        # Decrypt when retrieving
        decrypted = encryptor.decrypt_data(encrypted)
    """
    
    def __init__(self, key: str = None):
        """
        Initialize encryptor with key.
        
        Args:
            key: Fernet key as string. If not provided, 
                 uses ENCRYPTION_KEY env variable or generates new one.
        """
        if key:
            self.key = key.encode() if isinstance(key, str) else key
        else:
            # Try to get from environment
            env_key = os.environ.get('ENCRYPTION_KEY')
            if env_key:
                self.key = env_key.encode()
            else:
                # Generate new key (ONLY for development!)
                print("[WARNING] No ENCRYPTION_KEY found. Generating temporary key.")
                print("          Set ENCRYPTION_KEY env variable for production!")
                self.key = Fernet.generate_key()
                print(f"          Generated key: {self.key.decode()}")
        
        self.cipher = Fernet(self.key)
    
    def encrypt_data(self, data: Union[str, Dict, list]) -> str:
        """
        Encrypt data (string, dict, or list).
        
        Args:
            data: Data to encrypt
            
        Returns:
            Base64-encoded encrypted string
        """
        # Convert to JSON string if needed
        if isinstance(data, (dict, list)):
            data_str = json.dumps(data)
        else:
            data_str = str(data)
        
        # Encrypt
        encrypted = self.cipher.encrypt(data_str.encode())
        
        # Return as string for easy storage
        return encrypted.decode()
    
    def decrypt_data(self, encrypted_data: str) -> Union[Dict, list, str]:
        """
        Decrypt data.
        
        Args:
            encrypted_data: Encrypted string from encrypt_data()
            
        Returns:
            Original data (dict, list, or string)
        """
        # Decrypt
        decrypted = self.cipher.decrypt(encrypted_data.encode())
        decrypted_str = decrypted.decode()
        
        # Try to parse as JSON
        try:
            return json.loads(decrypted_str)
        except json.JSONDecodeError:
            return decrypted_str
    
    def encrypt_genotype(self, genotype: str) -> str:
        """Encrypt a single genotype (e.g., 'CT', 'AA')"""
        return self.encrypt_data(genotype)
    
    def decrypt_genotype(self, encrypted: str) -> str:
        """Decrypt a single genotype"""
        return self.decrypt_data(encrypted)
    
    @staticmethod
    def generate_key() -> str:
        """
        Generate a new Fernet encryption key.
        
        Returns:
            Key as string (save this securely!)
        """
        return Fernet.generate_key().decode()


# Global encryptor instance
_encryptor = None


def get_encryptor() -> GeneticDataEncryption:
    """Get or create the global encryptor instance"""
    global _encryptor
    if _encryptor is None:
        _encryptor = GeneticDataEncryption()
    return _encryptor


def encrypt_genetic_findings(findings: list) -> list:
    """
    Encrypt sensitive fields in genetic findings.
    
    Encrypts: genotype, interpretation, recommendation
    Keeps plain: rsid, gene, condition, risk_level (needed for filtering)
    
    Args:
        findings: List of genetic finding dicts
        
    Returns:
        List with sensitive fields encrypted
    """
    encryptor = get_encryptor()
    encrypted_findings = []
    
    for finding in findings:
        encrypted_finding = {
            # Keep these plain for querying
            'rsid': finding['rsid'],
            'gene': finding['gene'],
            'condition': finding['condition'],
            'risk_level': finding['risk_level'],
            
            # Encrypt sensitive data
            'genotype_encrypted': encryptor.encrypt_data(finding.get('genotype', '')),
            'interpretation_encrypted': encryptor.encrypt_data(finding.get('interpretation', '')),
            'recommendation_encrypted': encryptor.encrypt_data(finding.get('recommendation', '')),
            'source': finding.get('source', '')
        }
        encrypted_findings.append(encrypted_finding)
    
    return encrypted_findings


def decrypt_genetic_findings(encrypted_findings: list) -> list:
    """
    Decrypt genetic findings for display.
    
    Args:
        encrypted_findings: List with encrypted fields
        
    Returns:
        List with decrypted data
    """
    encryptor = get_encryptor()
    decrypted_findings = []
    
    for finding in encrypted_findings:
        decrypted_finding = {
            'rsid': finding['rsid'],
            'gene': finding['gene'],
            'condition': finding['condition'],
            'risk_level': finding['risk_level'],
            'source': finding.get('source', ''),
            
            # Decrypt sensitive fields
            'genotype': encryptor.decrypt_data(finding['genotype_encrypted']),
            'interpretation': encryptor.decrypt_data(finding['interpretation_encrypted']),
            'recommendation': encryptor.decrypt_data(finding['recommendation_encrypted'])
        }
        decrypted_findings.append(decrypted_finding)
    
    return decrypted_findings


# Helper to generate a key (run once and save!)
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("   ENCRYPTION KEY GENERATOR")
    print("=" * 60)
    print("\nGenerating a new encryption key...\n")
    
    key = GeneticDataEncryption.generate_key()
    
    print(f"Your new encryption key:\n")
    print(f"   {key}")
    print(f"\n" + "-" * 60)
    print("IMPORTANT: Save this key securely!")
    print("Add it to your .env file as:")
    print(f"   ENCRYPTION_KEY={key}")
    print("-" * 60)
    
    # Test encryption/decryption
    print("\nTesting encryption...")
    enc = GeneticDataEncryption(key)
    
    test_data = {"genotype": "CT", "risk": "high"}
    encrypted = enc.encrypt_data(test_data)
    decrypted = enc.decrypt_data(encrypted)
    
    print(f"Original:  {test_data}")
    print(f"Encrypted: {encrypted[:50]}...")
    print(f"Decrypted: {decrypted}")
    print(f"\n[OK] Encryption working correctly!")
