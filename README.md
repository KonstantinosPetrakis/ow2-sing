# OW2-Sing

This is a funny/silly project I put together in a few hours to cover any song using OW2's voice lines. It doesn't work well but it was fun to make.

Here's a (carefully selected, most of the project's output is really bad) cover of "Bring Me To Life" by Evanescence using OW2's voice lines:


https://github.com/user-attachments/assets/e9b6ecd5-e873-46d9-8e67-c6dc4ec7c8e0


```
Symmetra: a lie @2000
Winston: there's nothing @2580
Mei: inside @6201
Reinhardt: bring me @7741
Widowmaker: to life @9181
Mei: frozen @14061
Lifeweaver: inside @15881
Zenyatta: without @17321
Roadhog: your touch @18221
Sigma: without @19761
Sigma: your @20681
Mei: love @21781
Junkrat: darling @22601
Mercy: only @23381
Winston: you are the @23741
Lifeweaver: life @25841
Orisa: among @26361
Hanzo: the dead @27141
Doomfist: all @34421
Reaper: this time @34781
Brigitte: i can't believe i @35401
Mauga: couldn't see @36161
Widowmaker: kept @36941
Mei: in the dark @37161
Moira: but @37861
Reinhardt: you were @38122
Zenyatta: there @38402
Roadhog: in front @38522
Ashe: of me @38861
Genji: i've been @39622
Doomfist: sleeping @39902
Venture: a thousand years @40422
Moira: it seems @41382
Freja: got @42022
Mercy: to open @42322
Sojourn: my eyes @42962
Mei: to @43462
Pharah: everything @43682
Mauga: without a @44262
Reinhardt: thought @44702
Mauga: without a @45062
Brigitte: voice @45522
Zenyatta: without a @45842
Pharah: soul @47082
Tracer: don't @47302
Sigma: let me @47462
Lifeweaver: die @47782
Sigma: here there @48202
Moira: must be @48762
Moira: something more @49302
Reinhardt: bring me @53302
Sigma: to life @54442
Mei: wake @54822
D.Va: me up @55162
Kiriko: wake @55602
Brigitte: me up @55922
D.Va: inside @56662
Kiriko: i can't @57082
Mei: wake up @57362
Genji: wake @58122
Venture: me up @58442
Ramattra: inside @59182
Mei: save @59362
Moira: me @59662
Ana: call @60182
Lifeweaver: my name @61002
Moira: and save @61822
Mauga: me @62902
Kiriko: from @63182
Hanzo: the dark @64422
Kiriko: wake @64942
Lifeweaver: me up @65142
```

# How it works:

- `beautifulsoup4` and `requests` to scrape the OW2 voice lines from the OW2's wiki.
- `genius` API for song searching and lyrics retrieval.
- `yt-dlp` to download the audio of the song from YouTube.
- `spleeter` to separate the vocals from the music.
- `forcealign` to take timestamps of lyrics from songs and words in OW2's voice lines.
- `pydub` and `librosa` to process the audio files.

# How to install

ffmpeg, libsndfile and sox are required for this project. On ubuntu you can install them with:

```bash
sudo apt install ffmpeg libsndfile-dev sox
```

Then you can clone the repository and install the required Python packages:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env # create API token from official site of Genius
```

Finally, you have to download the `data.zip` file which contains all quote audio files, from the repository's releases and extract it to the root of the project.

# How to run

Just run the following command:

```bash
python __main__.py
```

You'll be asked to input a song name, and then select a song via numbers [1-9].
After some time the output will be in `data/output.mp3`.
