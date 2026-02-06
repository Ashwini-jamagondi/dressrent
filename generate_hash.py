import bcrypt

# Generate a new hash for "password123"
password = "password123"
salt = bcrypt.gensalt()
hashed = bcrypt.hashpw(password.encode('utf-8'), salt)

print("New password hash generated:")
print(hashed.decode('utf-8'))

# Test verification
is_valid = bcrypt.checkpw(password.encode('utf-8'), hashed)
print(f"\nVerification test: {'✅ WORKS' if is_valid else '❌ FAILED'}")