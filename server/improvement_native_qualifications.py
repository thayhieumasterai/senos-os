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
    '94bcc73f179d66eef2a9472d9b24604e13c5b88d3cde35731cfa8437fc798b77',
    # Exact changed semantic-outcome footprint, same native runtime and full enforcement suites.
    # docs/superpowers/evidence/2026-10-23-m2d1-native-qualification-outcome.json
    ('win32', '2.1.309',
    '5441781f2b6bbd07354b4a74560ee88c68c9bf05d6db3c7e24c452c91673dc53', '0.2.116',
    'claude-isolated-roles-v2', '958527ac69c3b5728044b22cf6d3bdebb920da7cbe46a9da261e899568ced1ef'):
    'b12c5daa40bd936049201445be20755ebdc6780f515600cbc8efb06c4bcf984b',
    # Exact raw-artifact prompt footprint, same native runtime; all20 enforcement checks.
    # docs/superpowers/evidence/2026-10-24-m2d1-native-qualification-format.json
    ('win32', '2.1.309',
    '5441781f2b6bbd07354b4a74560ee88c68c9bf05d6db3c7e24c452c91673dc53', '0.2.116',
    'claude-isolated-roles-v2', 'e7aaa5bd9902860e440349f0654f2a6ec92271770030f8bfaf6a0d584efb2a60'):
    'c650437d4977e292f5db7fcb1d315473aea2e50338da9d904d2aeb8846db3cda',
    # Exact bounded read-only CLI-observation footprint, all20 native enforcement checks.
    # docs/superpowers/evidence/2026-10-24-m2d1-native-qualification-observation.json
    ('win32', '2.1.309',
    '5441781f2b6bbd07354b4a74560ee88c68c9bf05d6db3c7e24c452c91673dc53', '0.2.116',
    'claude-isolated-roles-v2', 'be4a5866a411fdcbb68bc7728d6cec9418fac19132ca4a46dce40ac1cb45ca0b'):
    'd6bd3fc924e33bee4de397f14a451b2b8aa2906cda5510f82d2b2b01a8279fce',
    # Exact preparation-heartbeat footprint; all20 native enforcement checks.
    # docs/superpowers/evidence/2026-10-24-m2d1-native-qualification-preparation-heartbeat.json
    ('win32', '2.1.309',
    '5441781f2b6bbd07354b4a74560ee88c68c9bf05d6db3c7e24c452c91673dc53', '0.2.116',
    'claude-isolated-roles-v2', '972175a29309295afc596902ef711ea51400ba77c2f39e27aab1141f9a0f6a10'):
    '5fce2bef67729736715313284d300f3cd518b1ffa42929dd8db18205a79e0d19',
    # Exact83-source versioned skill-read footprint; all20 local native checks.
    # docs/superpowers/evidence/2026-10-24-m2d1-native-qualification-skill-reads.json
    ('win32', '2.1.309',
    '5441781f2b6bbd07354b4a74560ee88c68c9bf05d6db3c7e24c452c91673dc53', '0.2.116',
    'claude-isolated-roles-v2', '04c8c77baec04d04019752bc8abc2f9a5906e094ededfbdd56cfc3c712aef126'):
    '99516a424de809d7e6df8d26ec08441f589e99859919754644b1e4b768d62a39',
    # Final 0.314.0 source (M2D1 integrated, M2E activation schema), CLI 2.1.310; all20 native enforcement checks.
    # docs/superpowers/evidence/2026-10-25-m2-native-qualification-cli310.json
    ('win32', '2.1.310',
    'f9a3920634ae3b961ee92c2eb58d0051f5f8852b120983d0a4f57b6a5efeba61', '0.2.116',
    'claude-isolated-roles-v2', 'ee73f81305f01f7c1b43ed72744c9c2abf22ceff04b1661f60e48fd058273acd'):
    'f01379ed295dc87d4a4ffaf29409e7169567f3cce61120f195d1968f44117db1',
    # M3 source (canary schema 12 in the store footprint), CLI 2.1.310; all20 native enforcement checks.
    # docs/superpowers/evidence/2026-10-25-m3-native-qualification-cli310.json
    ('win32', '2.1.310',
    'f9a3920634ae3b961ee92c2eb58d0051f5f8852b120983d0a4f57b6a5efeba61', '0.2.116',
    'claude-isolated-roles-v2', '7849768b28e6793a033d7126f8780256f66bb6ce2e98b864e71eeffc9820f837'):
    '05faab0931442f72c32c3ef27c29c62e3e74cb81263041c079cf9d3024b80383',
    # M4 source (routing schema 13 in the store footprint), CLI 2.1.310; all20 native enforcement checks.
    # docs/superpowers/evidence/2026-10-25-m4-native-qualification-cli310.json
    ('win32', '2.1.310',
    'f9a3920634ae3b961ee92c2eb58d0051f5f8852b120983d0a4f57b6a5efeba61', '0.2.116',
    'claude-isolated-roles-v2', '1a8a08a07394d0ab31ecab33eeed216b8b971c0d0ed0d8a5a42b131c72f3f0c1'):
    'bfcdf27e5e16c8e05061654d32a2cc5fba641455c934f5093a410659377b0b1f',
    # M5 source (agent procedure schema 14 in the store footprint), CLI 2.1.310; all20 native enforcement checks.
    # docs/superpowers/evidence/2026-10-25-m5-native-qualification-cli310.json
    ('win32', '2.1.310',
    'f9a3920634ae3b961ee92c2eb58d0051f5f8852b120983d0a4f57b6a5efeba61', '0.2.116',
    'claude-isolated-roles-v2', 'c509f9a1560d3c93631c38ad1a461d5a5430f3149cf20ab51724fab6bfd6ed19'):
    'ce8d45299306c18f67043f1356a4d3337345c5528a42fd03bae52f794aca4a87',
    # M6 source (bundle schema 15 in the store footprint), CLI 2.1.310; all20 native enforcement checks.
    # docs/superpowers/evidence/2026-10-26-m6-native-qualification-cli310.json
    ('win32', '2.1.310',
    'f9a3920634ae3b961ee92c2eb58d0051f5f8852b120983d0a4f57b6a5efeba61', '0.2.116',
    'claude-isolated-roles-v2', 'b609a52ac28ea3d8837b74b7738ee3fd5c45b9d16169bb8564ed3b7f423da403'):
    '7c27e505c42466a42a3b879dbf22c5378f15f98e8b0eae89b0805b1a44071e4d',
    # M7 source (team schema 16 in the store footprint), CLI 2.1.310; all20 native enforcement checks.
    # docs/superpowers/evidence/2026-10-26-m7-native-qualification-cli310.json
    ('win32', '2.1.310',
    'f9a3920634ae3b961ee92c2eb58d0051f5f8852b120983d0a4f57b6a5efeba61', '0.2.116',
    'claude-isolated-roles-v2', '3c5543a3c14634b3736b51eb278b7c7f805554e3ab59ac8a908772230151d1f5'):
    '24547738307cb0db769a64bbf983e23d0d4d9dd0c8451163fcc73c9e5d9c1d3a',
    # M8 source (library schema 17 in the store footprint), CLI 2.1.310; all20 native enforcement checks.
    # docs/superpowers/evidence/2026-10-26-m8-native-qualification-cli310.json
    ('win32', '2.1.310',
    'f9a3920634ae3b961ee92c2eb58d0051f5f8852b120983d0a4f57b6a5efeba61', '0.2.116',
    'claude-isolated-roles-v2', 'c95dbc8847bf2aff279bffc309abedd06a3f24d81d3c4decd018d19ec9f52fb0'):
    'a1f71a0f5a49f6be570493032f7bc6ff0fb557b96d302e835469db90faa4e549'}


def profile_qualification(pin, platform):
    key = (platform, pin["cli_version"], pin["cli_hash"], pin["sdk_version"],
           pin["profile_version"], pin["profile_hash"])
    evidence = QUALIFIED_PROFILES.get(key)
    return evidence if type(evidence) is str and re.fullmatch(r"[0-9a-f]{64}", evidence) else None
