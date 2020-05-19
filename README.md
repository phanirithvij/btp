# btp
Btp
# Corpora collector

alias: IIITHDBC APP

**Setup:**

**Server:**

Install Python3 and the requirements

```shell
pip install -r server/requirements.txt
```

To start the server

```shell
python start_server.py
```

**App:**

1. Download Android studio or IntelliJ Idea
2. Download flutter following [these instructions](https://flutter.dev/docs/get-started/install)
3. Add flutter to `$PATH` and android studio folder to `$ANDROID_HOME` environment variables

> NOTE: Will not work on android emulator because emulator cannot handle audio recording and also some networking issues

```shell
cd mobile_app/corpa/
flutter pub get
# connect to an android device using usb cable
# enable developer options in the android device and allow USB debugging

flutter run -v # debug mode (use this in development)

# or

flutter run --release -v # release version (faster performance)
```

**Or:**

To build the apk file use this:

```shell
flutter build apk --target-platform android-arm,android-arm64,android-x64 --split-per-abi -v
```

Then install that apk in the android device.

## IMPORTANT

1. If the app is being tested locally, the android device and the pc SHOULD be connected to same wifi.

2. Before running the app locally you must change the server url in the app's `mobile_app/corpa/lib/provider/server.dart` file.

   In line 21 it now says

   ```dart
   static final String server = "http://192.168.43.159:3000";
   ```

   - Need to change it to your local address.
   - You can find your local address
   - On Windows `ipconfig.exe | grep IPv4` on linux `ifconfig`.
   - One of the ipv4 address corresponding to the connected wifi network will be the IP.
   - Change the `server` to `http:/{ipv4}:3000` and NO `/` at the end.

## TODO

- [ ] Change the DB to postgres or something else
- [ ] Deploy on heroku
- [ ] Admin console
  - [ ] Admin account
    - [ ] One admin account
      - [ ] Admin credentials are stored in code
      - [ ] Only those with the access to the code can view the admin password.
    - [ ] Multipe admin accounts by requesting the main admin (via email)
      - [ ] Different levels of permissions
        - [ ] View
        - [ ] Edit
        - [ ] Delete
    - [ ] Manage Admins page
      - [ ] Modify permissions
  - [ ] Batch functions
    - [ ] Delete user
    - [ ] Download files by a user
    - [ ] Files Multi select download and delete
