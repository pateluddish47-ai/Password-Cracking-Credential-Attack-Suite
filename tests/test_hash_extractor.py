from modules import hash_extractor as he


def test_identify_shadow_algorithm_sha512():
    assert he.identify_shadow_algorithm("$6$salt$hash") == "SHA-512"


def test_identify_shadow_algorithm_md5():
    assert he.identify_shadow_algorithm("$1$salt$hash") == "MD5"


def test_identify_shadow_algorithm_locked_account():
    assert "locked" in he.identify_shadow_algorithm("*")
    assert "locked" in he.identify_shadow_algorithm("!!")


def test_identify_shadow_algorithm_legacy_des():
    assert he.identify_shadow_algorithm("abLegacyDesHash1") == "DES (legacy crypt)"


def test_parse_shadow_file(tmp_path):
    shadow = tmp_path / "shadow.txt"
    shadow.write_text(
        "root:$6$abcd$hash:19500:0:99999:7:::\ncarol:*:19500:0:99999:7:::\n",
        encoding="utf-8",
    )
    creds = he.parse_shadow_file(shadow)
    assert len(creds) == 2
    assert creds[0].username == "root"
    assert creds[0].algorithm == "SHA-512"
    assert creds[1].algorithm == "locked/disabled account"


def test_parse_sam_dump_skips_empty_hashes(tmp_path):
    sam = tmp_path / "sam.txt"
    sam.write_text(
        "Guest:501:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::\n"
        "jsmith:1001:aad3b435b51404eeaad3b435b51404ee:8846f7eaee8fb117ad06bdd830b7586c:::\n",
        encoding="utf-8",
    )
    creds = he.parse_sam_dump(sam)
    usernames = {c.username for c in creds}
    assert "jsmith" in usernames
    assert "Guest" not in usernames
