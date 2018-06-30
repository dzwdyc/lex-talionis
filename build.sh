# Build Script for the_lion_throne
# In Data/config.ini, turn cheat to 0
# In Data/config.ini, turn Screen Size to 3 and temp_ScreenSize to 3
pyinstaller main.spec
rm -rf ../cosmic_demo
mv dist/cosmic_demo ../cosmic_demo
cp ../lex-talionis-utilities/audio_dlls/* ../cosmic_demo/
echo Done