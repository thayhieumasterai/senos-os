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
    '537a5a9955b0d0b429f1f4a04c2ddbea74205c259d91e9c1d45e44029a9ac76a',
    # Exact changed semantic-outcome footprint, same native runtime and full enforcement suites.
    # docs/superpowers/evidence/2026-10-23-m2d1-native-qualification-outcome.json
    ('win32', '2.1.309',
    '5441781f2b6bbd07354b4a74560ee88c68c9bf05d6db3c7e24c452c91673dc53', '0.2.116',
    'claude-isolated-roles-v2', '958527ac69c3b5728044b22cf6d3bdebb920da7cbe46a9da261e899568ced1ef'):
    '6532d0e0cacfb2230233d577a04d73d9293f77a3a324eb037e6f93ca7c187526',
    # Exact raw-artifact prompt footprint, same native runtime; all20 enforcement checks.
    # docs/superpowers/evidence/2026-10-24-m2d1-native-qualification-format.json
    ('win32', '2.1.309',
    '5441781f2b6bbd07354b4a74560ee88c68c9bf05d6db3c7e24c452c91673dc53', '0.2.116',
    'claude-isolated-roles-v2', 'e7aaa5bd9902860e440349f0654f2a6ec92271770030f8bfaf6a0d584efb2a60'):
    'c076af3628b8f1548528521ae38d93bd46da63cb2469c66c4850f607a03c8621',
    # Exact bounded read-only CLI-observation footprint, all20 native enforcement checks.
    # docs/superpowers/evidence/2026-10-24-m2d1-native-qualification-observation.json
    ('win32', '2.1.309',
    '5441781f2b6bbd07354b4a74560ee88c68c9bf05d6db3c7e24c452c91673dc53', '0.2.116',
    'claude-isolated-roles-v2', 'be4a5866a411fdcbb68bc7728d6cec9418fac19132ca4a46dce40ac1cb45ca0b'):
    'd739408c7ab13d8af13a511c64b59d65c30f9764bfc0b8035da4901c5117bde8',
    # Exact preparation-heartbeat footprint; all20 native enforcement checks.
    # docs/superpowers/evidence/2026-10-24-m2d1-native-qualification-preparation-heartbeat.json
    ('win32', '2.1.309',
    '5441781f2b6bbd07354b4a74560ee88c68c9bf05d6db3c7e24c452c91673dc53', '0.2.116',
    'claude-isolated-roles-v2', '972175a29309295afc596902ef711ea51400ba77c2f39e27aab1141f9a0f6a10'):
    'ed2fc6480939077408e52ed4ca3482a37043565e5e9055c98a66fbca635b7fb6',
    # Exact83-source versioned skill-read footprint; all20 local native checks.
    # docs/superpowers/evidence/2026-10-24-m2d1-native-qualification-skill-reads.json
    ('win32', '2.1.309',
    '5441781f2b6bbd07354b4a74560ee88c68c9bf05d6db3c7e24c452c91673dc53', '0.2.116',
    'claude-isolated-roles-v2', '04c8c77baec04d04019752bc8abc2f9a5906e094ededfbdd56cfc3c712aef126'):
    '815d39e538f86eb531fc97a0330f436a722ff00d13946d6525a0800109786919',
    # Final 0.314.0 source (M2D1 integrated, M2E activation schema), CLI 2.1.310; all20 native enforcement checks.
    # docs/superpowers/evidence/2026-10-25-m2-native-qualification-cli310.json
    ('win32', '2.1.310',
    'f9a3920634ae3b961ee92c2eb58d0051f5f8852b120983d0a4f57b6a5efeba61', '0.2.116',
    'claude-isolated-roles-v2', 'ee73f81305f01f7c1b43ed72744c9c2abf22ceff04b1661f60e48fd058273acd'):
    '969ac08c620516cc2bf1d5419592ecc83c093b372300d28aae191f4b28a4773f',
    # M3 source (canary schema 12 in the store footprint), CLI 2.1.310; all20 native enforcement checks.
    # docs/superpowers/evidence/2026-10-25-m3-native-qualification-cli310.json
    ('win32', '2.1.310',
    'f9a3920634ae3b961ee92c2eb58d0051f5f8852b120983d0a4f57b6a5efeba61', '0.2.116',
    'claude-isolated-roles-v2', '7849768b28e6793a033d7126f8780256f66bb6ce2e98b864e71eeffc9820f837'):
    '0c60c890713927e12621bffcf8e23ecce982927900a20c75d9fe214e6219ed29',
    # M4 source (routing schema 13 in the store footprint), CLI 2.1.310; all20 native enforcement checks.
    # docs/superpowers/evidence/2026-10-25-m4-native-qualification-cli310.json
    ('win32', '2.1.310',
    'f9a3920634ae3b961ee92c2eb58d0051f5f8852b120983d0a4f57b6a5efeba61', '0.2.116',
    'claude-isolated-roles-v2', '1a8a08a07394d0ab31ecab33eeed216b8b971c0d0ed0d8a5a42b131c72f3f0c1'):
    '95d7f8c534dc5e4af6e0fbba2e1f12432dc5414fa91ee24c8b0e53c64b449110',
    # M5 source (agent procedure schema 14 in the store footprint), CLI 2.1.310; all20 native enforcement checks.
    # docs/superpowers/evidence/2026-10-25-m5-native-qualification-cli310.json
    ('win32', '2.1.310',
    'f9a3920634ae3b961ee92c2eb58d0051f5f8852b120983d0a4f57b6a5efeba61', '0.2.116',
    'claude-isolated-roles-v2', 'c509f9a1560d3c93631c38ad1a461d5a5430f3149cf20ab51724fab6bfd6ed19'):
    '5f4d1737a2fd91786d174963afc44c5101fcce3618f07e5882bd7f20bed5d203',
    # M6 source (bundle schema 15 in the store footprint), CLI 2.1.310; all20 native enforcement checks.
    # docs/superpowers/evidence/2026-10-26-m6-native-qualification-cli310.json
    ('win32', '2.1.310',
    'f9a3920634ae3b961ee92c2eb58d0051f5f8852b120983d0a4f57b6a5efeba61', '0.2.116',
    'claude-isolated-roles-v2', 'b609a52ac28ea3d8837b74b7738ee3fd5c45b9d16169bb8564ed3b7f423da403'):
    'd130f68ca8f4e84a1a6b3cd9332c5e099e49c80481ee26c0a249dc5679a11348',
    # M7 source (team schema 16 in the store footprint), CLI 2.1.310; all20 native enforcement checks.
    # docs/superpowers/evidence/2026-10-26-m7-native-qualification-cli310.json
    ('win32', '2.1.310',
    'f9a3920634ae3b961ee92c2eb58d0051f5f8852b120983d0a4f57b6a5efeba61', '0.2.116',
    'claude-isolated-roles-v2', '3c5543a3c14634b3736b51eb278b7c7f805554e3ab59ac8a908772230151d1f5'):
    '2f8ef469a15ce6120ab2f19a7e280adbd6e67f8d161dc5bda1f6e525843b23c4',
    # M8 source (library schema 17 in the store footprint), CLI 2.1.310; all20 native enforcement checks.
    # docs/superpowers/evidence/2026-10-26-m8-native-qualification-cli310.json
    ('win32', '2.1.310',
    'f9a3920634ae3b961ee92c2eb58d0051f5f8852b120983d0a4f57b6a5efeba61', '0.2.116',
    'claude-isolated-roles-v2', '36295da57bd958b6cfc85d44ebcbf66538f0b04e5a9f61dd05a313c2155bc3eb'):
    'd5cf5803cacda514a51804c3bd0ed03fb7f151ce0eb587a1eae088aa50b52d87'}


def profile_qualification(pin, platform):
    key = (platform, pin["cli_version"], pin["cli_hash"], pin["sdk_version"],
           pin["profile_version"], pin["profile_hash"])
    evidence = QUALIFIED_PROFILES.get(key)
    return evidence if type(evidence) is str and re.fullmatch(r"[0-9a-f]{64}", evidence) else None
