# Corpora collector

alias: IIITHDBC APP

**Setup:**

**Server:**

Install Python3 and redis

To start the server

```shell
./start-server.sh
```

On other linux systems check the command for launching a terminal and see if it can take arguments
and make a copy of the shell script with the new terminal emualtor command


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

```
flutter install
```

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


To inspect redis db (This is optional)

```shell
# install snap and install redis-desktop-manager (size 400MB)
snap run redis-desktop-manager.rdm
```

## TODO

- [ ] Change the DB to postgres or something else
- [ ] Deploy on heroku
- [ ] Admin console
  - [ ] Admin account
    - [ ] One admin account
      - [ ] Admin credentials are stored in code
      - [ ] Only those with the access to the code can view the admin password.
  - [ ] Batch functions
    - [ ] Delete user and user's files
    - [x] Download files by a user
    - [x] Files Multi select download and delete
- [ ] Filebrowser integration
