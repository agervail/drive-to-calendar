drive-to-calendar
=================

Simple python script to get the android chrono times and put them in your google calendar

You'll need the api-python-client
```
pip --upgrade google-api-python-client
or
easy_install --upgrade google-api-python-client
```

First get the files out of the drive
```
python import_drive_to_csv.py
```

Then a df_seance.csv is generated and you launch to put the trainings into the calendat
```
python export_csv_to_calendar.py
```
