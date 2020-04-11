import 'package:flutter/material.dart';

class DatePicker extends StatefulWidget {
  DatePicker({Key key}) : super(key: key);

  @override
  _DatePickerState createState() => _DatePickerState();
}

class _DatePickerState extends State<DatePicker> {
  DateTime selectedDate = DateTime.now();
  bool _selectedOnce = false;

  Future<Null> _selectDate(BuildContext context) async {
    final _now = DateTime.now();
    final DateTime picked = await showDatePicker(
      context: context,
      initialDate: selectedDate,
      firstDate: DateTime(1900),
      lastDate: _now,
    );
    if (picked != null && picked != selectedDate)
      setState(() {
        selectedDate = picked;
        _selectedOnce = true;
      });
  }

  @override
  Widget build(BuildContext context) {
    return Stack(
      children: <Widget>[
        Padding(
          padding: const EdgeInsets.only(top: 20, left: 50, right: 50),
          child: Container(
            height: 60,
            width: MediaQuery.of(context).size.width,
            child: Column(
              children: <Widget>[
                // TODO replace all this with a simple underline
                // This is just to show the underline
                TextField(
                  style: TextStyle(
                    color: Colors.white,
                  ),
                  decoration: InputDecoration(
                    // hintText: "Select Date",
                    // helperText: "Input",
                    enabled: false,
                    disabledBorder: UnderlineInputBorder(
                      borderSide: BorderSide(color: Colors.white54),
                    ),
                    fillColor: Colors.lightBlueAccent,
                    // labelText: 'Date',
                    labelStyle: TextStyle(
                      color: Colors.white70,
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
        Padding(
          padding: const EdgeInsets.only(top: 20, left: 50, right: 50),
          child: Container(
            height: 60,
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.center,
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: <Widget>[
                RichText(
                  text: TextSpan(
                    text:
                        (_selectedOnce ? _getDateandAge[0] : "date of birth") +
                            " " * 4,
                    style: DefaultTextStyle.of(context).style,
                    children: <TextSpan>[
                      TextSpan(
                          text:
                              _selectedOnce ? "Age: " + _getDateandAge[1] : "",
                          style: TextStyle(
                            fontWeight: FontWeight.bold,
                            color: Colors.black,
                          )),
                    ],
                  ),
                ),
                Icon(Icons.arrow_drop_down),
              ],
            ),
          ),
        ),
        Padding(
          padding: const EdgeInsets.only(top: 20, left: 50),
          child: Row(
            children: <Widget>[
              // Date picker will open on tap
              GestureDetector(
                onTap: () {
                  _selectDate(context);
                },
                child: Container(
                  width: MediaQuery.of(context).size.width - 100,
                  height: 60,
                  color: Colors.transparent,
                  // the following is to debug the date picker onclick gestureDetector tap region
                  // color: Colors.black12,
                ),
              ),
              //
              IconButton(
                icon: Icon(Icons.info_outline),
                onPressed: () {
                  // Show Snackbar message
                  // That the date of birth is used only to compute the Age
                  // And age is stored
                  final snackBar = SnackBar(
                    duration: Duration(seconds: 2, milliseconds: 500),
                    backgroundColor: Colors.black,
                    content: Text(
                      'Disclaimer! The [date of birth] is used only to compute the [Age]',
                      style: TextStyle(color: Colors.white),
                    ),
                    action: SnackBarAction(
                        textColor: Colors.green,
                        label: "OK",
                        onPressed: () {
                          Scaffold.of(context).removeCurrentSnackBar();
                        }),
                  );
                  Scaffold.of(context).showSnackBar(snackBar);
                },
              ),
            ],
          ),
        ),
      ],
    );
  }

  List<String> get _getDateandAge {
    final date = "${selectedDate.toLocal()}".split(' ')[0];
    final dur = DateTime.now().difference(selectedDate);
    int age = (dur.inDays / 365).floor();

    return [date, "$age"];
  }
}
