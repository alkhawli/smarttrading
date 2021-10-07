@ECHO OFF
call conda activate smartstocker
python main.py
call conda deactivate
ECHO Finished.
PAUSE


