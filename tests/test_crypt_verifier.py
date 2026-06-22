from passlib.hash import md5_crypt, sha512_crypt

from modules import crypt_verifier as cv


def test_verify_crypt_password_correct():
    hash_value = sha512_crypt.using(rounds=5000).hash("hunter2")
    assert cv.verify_crypt_password("hunter2", hash_value, "SHA-512")


def test_verify_crypt_password_incorrect():
    hash_value = sha512_crypt.using(rounds=5000).hash("hunter2")
    assert not cv.verify_crypt_password("wrongpass", hash_value, "SHA-512")


def test_dictionary_attack_crypt_finds_match():
    hash_value = md5_crypt.hash("admin")
    result = cv.dictionary_attack_crypt(hash_value, "MD5", ["nope", "admin", "also-nope"])
    assert result.cracked
    assert result.matched_word == "admin"
