# Private S0 Fixture Repository Setup

Date: 2026-10-02

## Goal

Keep the 14 S0 source MP3s out of the public DadRock Tabs repository while making Codespaces setup one-command reproducible.

## Public repo behavior

The public repo now contains:

- `scripts/sync_s0_fixtures.sh`
- `scripts/build_s0_fixtures.sh`

and ignores:

- `/s0_sources/`
- `/s0_generated/`
- `/models/bs-roformer/`

## Private fixture repo layout

Create one private repository containing exactly:

```
README.md
manifest.json
freesound_community-clean-electric-guitar-loop-83895(1).mp3
freesound_community-electric-guitar-metal-riff-107087(1).mp3
freesound_community-electric-guitar-strumming-3-97679(1).mp3
freesound_community-electric-guitar-tapping-34546(1).mp3
shidenbeatsmusic-jingle-slide-guitar-22108(1).mp3
sunnyscy-guitar-riff-in-e-minor-95-bpm-dry-475013(1).mp3
freesound_community-electric-bass-guitar-loop-2-bpm-110-43631.mp3
freesound_community-bass-guitar-death-metal-loop-240-bpm-101327.mp3
freesound_community-picked_bassnote_a-100710.mp3
idoberg-funk-rock-slap-bass-riff-em-106bpm-490940.mp3
freesound_community-fretless-bass-open-d-bridge-pickup-100754.mp3
freesound_community-bass60bpm-78680.mp3
dragon-studio-atmospheric-drums-443147(1).mp3
freesound_community-speech-dramatic-female-38105(1).mp3
```

The provided bundle `S0_FIXTURE_SOURCES_V1.zip` contains that exact structure plus the manifest.

Keep this repo private. Do not publish or redistribute the MP3s.

## Codespaces sync

Once the private repo exists, from the public DadRock repo:

```bash
git pull
chmod +x scripts/sync_s0_fixtures.sh scripts/build_s0_fixtures.sh
S0_FIXTURE_REPO=<owner>/<private-fixture-repo> ./scripts/sync_s0_fixtures.sh
./scripts/build_s0_fixtures.sh
```

The sync script:
- shallow-clones the private fixture repo;
- verifies every source SHA-256 against `manifest.json`;
- copies verified files into ignored `s0_sources/`;
- deletes the temporary private-repo clone.

The build script then recreates the 12 frozen S0 synthetic mixtures under ignored `s0_generated/`.

## Why this design

This keeps:
- public Git clean;
- raw audio private;
- Codespaces setup reproducible;
- source hashes verified;
- model and generated WAVs out of source control.

