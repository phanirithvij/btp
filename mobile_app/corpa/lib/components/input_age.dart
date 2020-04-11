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
    return Padding(
      padding: const EdgeInsets.only(top: 20, left: 50, right: 50),
      child: Container(
        height: 60,
        width: MediaQuery.of(context).size.width,
        child: Column(
          children: <Widget>[
            Stack(
              children: <Widget>[
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
                Container(
                  height: 60,
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.center,
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: <Widget>[
                      Text(
                        _selectedOnce
                            ? "${selectedDate.toLocal()}".split(' ')[0]
                            : "Select Date",
                        // style: TextStyle(color: Colors.white70),
                      ),
                      Icon(Icons.arrow_drop_down),
                    ],
                  ),
                ),
                GestureDetector(
                  onTap: () {
                    _selectDate(context);
                  },
                  child: Container(
                    width: double.infinity,
                    height: 60,
                    color: Colors.transparent,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
