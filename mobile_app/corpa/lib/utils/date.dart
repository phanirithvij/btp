class DateUtils {
  static String getDate(DateTime selectedDate) {
    return selectedDate.toLocal().toString().split(' ')[0];
  }

  static int getAge(DateTime selectedDate) {
    final dur = DateTime.now().difference(selectedDate);
    int age = (dur.inDays / 365).floor();

    return age;
  }
}
