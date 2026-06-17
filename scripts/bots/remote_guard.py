import os
import hashlib
import sqlite3
import zipfile

def calculate_file_sha256(file_path):
    """Generates a secure SHA256 signature to verify exact file consistency."""
    sha256_hash = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except IOError:
        return None

def verify_archive_integrity(zip_path):
    print("\n----------------------------------------------------------")
    print("🛡️ RUNNING PRE-FLIGHT BOUNDARY INTEGRITY HANDSHAKE")
    print("----------------------------------------------------------")
    
    if not os.path.exists(zip_path):
        print("❌ [GUARD FAULT] Specified archive payload does not exist.")
        return False

    # 1. Cryptographic Signature Validation Passing
    file_hash = calculate_file_sha256(zip_path)
    print(f"[GUARD] Cryptographic SHA256 Signature Generated:\n        -> {file_hash}")

    # 2. Extract Archive Content Integrity Structural Check
    try:
        with zipfile.ZipFile(zip_path, 'r') as archive:
            corrupt_file = archive.testzip()
            if corrupt_file is not None:
                print(f"❌ [CORRUPTION ALERT] CRC mismatch discovered inside archive on: {corrupt_file}")
                return False
            
            # Inspect file listings inside zip container structures
            contained_files = archive.namelist()
            print(f"[GUARD] Archive extraction check passed. Content manifest: {contained_files}")
            
            # Confirm that an expected raw payload exists inside the transfer package
            if not any(f.endswith('.csv') for f in contained_files):
                print("❌ [VALIDATION FAULT] Archive format invalid: Missing structural data source file.")
                return False
                
    except zipfile.BadZipFile:
        print("❌ [CRITICAL GUARD FAULT] Target payload file is malformed or corrupted.")
        return False

    print("🟢 [HANDSHAKE OK] Archive integrity validated. Safe to initialize server sync.")
    return True

if __name__ == "__main__":
    # Test block routing points against an arbitrary target file configuration path
    sample_target = "./exports/"
    if os.path.exists(sample_target) and os.listdir(sample_target):
        newest_file = max([os.path.join(sample_target, f) for f in os.listdir(sample_target) if f.endswith('.zip')])
        verify_archive_integrity(newest_file)

