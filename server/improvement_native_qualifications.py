"""Reviewed release registrations for exact native-profile qualification evidence.

Keys bind platform, binary/version, SDK and the complete profile source hash.
Values are SHA-256 of actual qualification evidence retained with the release.
This host source is the registration authority, deliberately outside the profile
hash to avoid a self-referential digest. No environment/HTTP/model can register a
profile. Add an entry only after its native black-box qualification has passed;
changing profile source invalidates the entry. Historical receipts stay readable.
"""
from __future__ import annotations

import re

# Reviewed path-independent release closures. Registration is external authority,
# deliberately excluded from its own source/manifest fingerprint. Empty until
# the complete production pipeline has passed actual qualification.
# Key: (platform, CLI version/hash, SDK version, profile version/hash, fingerprint).
# Value: SHA-256 of retained reviewed qualification evidence.
REVIEWED_RELEASES = {}

# Reviewed candidates may be exercised only by the separate local-dummy
# QualificationSession. This is not live profile registration or account
# readiness. Same exact seven-part key; value pins the candidate review evidence.
# Remains empty until a final candidate closure has been independently reviewed.
REVIEWED_QUALIFICATION_CANDIDATES = {}

# Exact dummy-auth/native enforcement evidence; this does not attest account
# readiness, actual call usage, business quality or final eligibility.
# docs/superpowers/evidence/2026-10-23-m2c-native-qualification.json
QUALIFIED_PROFILES = {('win32', '2.1.308',
    'c9796ba22a9221586b36371b36f5b66198d66eb4badf6a4cf4a5f7b07becea53', '0.2.116',
    'claude-isolated-roles-v2', '9dcf718470e70957d07454bb8b50fbde79575a3b23d8c06e24cc9b749051116b'):
    '98ee4e8c406091ee84db2862cbf80b11a5f15cf88f7d4d96188d5e2360822ea7',
    # Exact paired-view/solver/typed-role/native-lifetime enforcement, local dummy providers.
    # docs/superpowers/evidence/2026-10-23-m2d1-native-qualification-final.json
    ('win32', '2.1.309',
    '5441781f2b6bbd07354b4a74560ee88c68c9bf05d6db3c7e24c452c91673dc53', '0.2.116',
    'claude-isolated-roles-v2', '4d346a3ae4f1afa99784fc51307258ad99a8d470ac6a0c46f1d330e6b0e656fa'):
    '3c1966ecc8312a2c1d18f9489f247d012eda055956fa058470df37955aa1beb6',
    # Exact changed semantic-outcome footprint, same native runtime and full enforcement suites.
    # docs/superpowers/evidence/2026-10-23-m2d1-native-qualification-outcome.json
    ('win32', '2.1.309',
    '5441781f2b6bbd07354b4a74560ee88c68c9bf05d6db3c7e24c452c91673dc53', '0.2.116',
    'claude-isolated-roles-v2', '958527ac69c3b5728044b22cf6d3bdebb920da7cbe46a9da261e899568ced1ef'):
    'b3466bb96303935ff4f88d51d4cfa97501353c1ac3c0472ba8e529ae134ce2fc',
    # Exact raw-artifact prompt footprint, same native runtime; all20 enforcement checks.
    # docs/superpowers/evidence/2026-10-24-m2d1-native-qualification-format.json
    ('win32', '2.1.309',
    '5441781f2b6bbd07354b4a74560ee88c68c9bf05d6db3c7e24c452c91673dc53', '0.2.116',
    'claude-isolated-roles-v2', 'e7aaa5bd9902860e440349f0654f2a6ec92271770030f8bfaf6a0d584efb2a60'):
    'be4bcce88332f0098ae597e047789005656314d135785353030c34e465c28004',
    # Exact bounded read-only CLI-observation footprint, all20 native enforcement checks.
    # docs/superpowers/evidence/2026-10-24-m2d1-native-qualification-observation.json
    ('win32', '2.1.309',
    '5441781f2b6bbd07354b4a74560ee88c68c9bf05d6db3c7e24c452c91673dc53', '0.2.116',
    'claude-isolated-roles-v2', 'be4a5866a411fdcbb68bc7728d6cec9418fac19132ca4a46dce40ac1cb45ca0b'):
    'd76ffab9d7f30708373726cc00fe25201a5c2a79408a240da248ba9511afd34b',
    # Exact preparation-heartbeat footprint; all20 native enforcement checks.
    # docs/superpowers/evidence/2026-10-24-m2d1-native-qualification-preparation-heartbeat.json
    ('win32', '2.1.309',
    '5441781f2b6bbd07354b4a74560ee88c68c9bf05d6db3c7e24c452c91673dc53', '0.2.116',
    'claude-isolated-roles-v2', '972175a29309295afc596902ef711ea51400ba77c2f39e27aab1141f9a0f6a10'):
    '0a128973c5de12cabd5ef78bea8800c40f8f0356dd896564a3b2baa3024d6ed2',
    # Exact83-source versioned skill-read footprint; all20 local native checks.
    # docs/superpowers/evidence/2026-10-24-m2d1-native-qualification-skill-reads.json
    ('win32', '2.1.309',
    '5441781f2b6bbd07354b4a74560ee88c68c9bf05d6db3c7e24c452c91673dc53', '0.2.116',
    'claude-isolated-roles-v2', '04c8c77baec04d04019752bc8abc2f9a5906e094ededfbdd56cfc3c712aef126'):
    'a3de95c08e89dffb3479bd2bd3975db0469198ba44384e5be3b33573af63e7e9',
    # Final 0.314.0 source (M2D1 integrated, M2E activation schema), CLI 2.1.310; all20 native enforcement checks.
    # docs/superpowers/evidence/2026-10-25-m2-native-qualification-cli310.json
    ('win32', '2.1.310',
    'f9a3920634ae3b961ee92c2eb58d0051f5f8852b120983d0a4f57b6a5efeba61', '0.2.116',
    'claude-isolated-roles-v2', 'ee73f81305f01f7c1b43ed72744c9c2abf22ceff04b1661f60e48fd058273acd'):
    'b8631de1eee7bb43e0e4382f3514070d7aa4b10edc2d366c329d79c0e8059a71',
    # M3 source (canary schema 12 in the store footprint), CLI 2.1.310; all20 native enforcement checks.
    # docs/superpowers/evidence/2026-10-25-m3-native-qualification-cli310.json
    ('win32', '2.1.310',
    'f9a3920634ae3b961ee92c2eb58d0051f5f8852b120983d0a4f57b6a5efeba61', '0.2.116',
    'claude-isolated-roles-v2', '7849768b28e6793a033d7126f8780256f66bb6ce2e98b864e71eeffc9820f837'):
    'f18e2605276cd25898ab256919df30ec2a6042358094843e45fed75023ff1766',
    # M4 source (routing schema 13 in the store footprint), CLI 2.1.310; all20 native enforcement checks.
    # docs/superpowers/evidence/2026-10-25-m4-native-qualification-cli310.json
    ('win32', '2.1.310',
    'f9a3920634ae3b961ee92c2eb58d0051f5f8852b120983d0a4f57b6a5efeba61', '0.2.116',
    'claude-isolated-roles-v2', '1a8a08a07394d0ab31ecab33eeed216b8b971c0d0ed0d8a5a42b131c72f3f0c1'):
    '8a5d81b1c632dc5f4390611b380c399cf0039faa783c83149266c3ccfe6ef22b',
    # M5 source (agent procedure schema 14 in the store footprint), CLI 2.1.310; all20 native enforcement checks.
    # docs/superpowers/evidence/2026-10-25-m5-native-qualification-cli310.json
    ('win32', '2.1.310',
    'f9a3920634ae3b961ee92c2eb58d0051f5f8852b120983d0a4f57b6a5efeba61', '0.2.116',
    'claude-isolated-roles-v2', 'c509f9a1560d3c93631c38ad1a461d5a5430f3149cf20ab51724fab6bfd6ed19'):
    'a8dbed022802e0ebc1480efa181c91930244462eda1632f88357a7c622ba9292',
    # M6 source (bundle schema 15 in the store footprint), CLI 2.1.310; all20 native enforcement checks.
    # docs/superpowers/evidence/2026-10-26-m6-native-qualification-cli310.json
    ('win32', '2.1.310',
    'f9a3920634ae3b961ee92c2eb58d0051f5f8852b120983d0a4f57b6a5efeba61', '0.2.116',
    'claude-isolated-roles-v2', 'b609a52ac28ea3d8837b74b7738ee3fd5c45b9d16169bb8564ed3b7f423da403'):
    '62f8ffcdf753a12a4625035fb81c84ef0245bbe5f879c4c7520dc2ac6ef8e135',
    # M7 source (team schema 16 in the store footprint), CLI 2.1.310; all20 native enforcement checks.
    # docs/superpowers/evidence/2026-10-26-m7-native-qualification-cli310.json
    ('win32', '2.1.310',
    'f9a3920634ae3b961ee92c2eb58d0051f5f8852b120983d0a4f57b6a5efeba61', '0.2.116',
    'claude-isolated-roles-v2', '3c5543a3c14634b3736b51eb278b7c7f805554e3ab59ac8a908772230151d1f5'):
    'e7fe98f83e62310e7f73bdad00e44337713d3ed142d891c19588f6e156f27199',
    # M8 source (library schema 17 in the store footprint), CLI 2.1.310; all20 native enforcement checks.
    # docs/superpowers/evidence/2026-10-26-m8-native-qualification-cli310.json
    ('win32', '2.1.310',
    'f9a3920634ae3b961ee92c2eb58d0051f5f8852b120983d0a4f57b6a5efeba61', '0.2.116',
    'claude-isolated-roles-v2', '36295da57bd958b6cfc85d44ebcbf66538f0b04e5a9f61dd05a313c2155bc3eb'):
    '6a3b397a8c806c1347b27ac21e7dc5445cc2dfb664d7e53fe64e95eb3460091e'}


def profile_qualification(pin, platform):
    key = (platform, pin["cli_version"], pin["cli_hash"], pin["sdk_version"],
           pin["profile_version"], pin["profile_hash"])
    evidence = QUALIFIED_PROFILES.get(key)
    return evidence if type(evidence) is str and re.fullmatch(r"[0-9a-f]{64}", evidence) else None
