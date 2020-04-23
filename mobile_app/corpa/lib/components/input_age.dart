import 'package:corpora/provider/authentication.dart';
import 'package:corpora/utils/date.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

class DatePicker extends StatefulWidget {
  DatePicker({Key key}) : super(key: key);

  @override
  _DatePickerState createState() => _DatePickerState();
}

class _DatePickerState extends State<DatePicker> {
  bool _selectedOnce = false;

  Future<Null> _selectDate(BuildContext context) async {
    // print(context.owner.debugBuilding);

    final _now = DateTime.now();
    final DateTime picked = await showDatePicker(
      context: context,
      initialDate: Provider.of<AuthStore>(context, listen: false).selectedDate,
      firstDate: DateTime(1900),
      lastDate: _now,
    );
    if (picked != null &&
        picked != Provider.of<AuthStore>(context, listen: false).selectedDate)
      setState(() {
        Provider.of<AuthStore>(context, listen: false).storeDate(picked);
        _selectedOnce = true;
      });
  }

  @override
  Widget build(BuildContext context) {
    return Stack(
      children: <Widget>[
        Center(
          child: Padding(
            padding: const EdgeInsets.only(top: 20, left: 50, right: 50),
            child: Container(
              height: 60,
              width: MediaQuery.of(context).orientation == Orientation.portrait
                  ? MediaQuery.of(context).size.width
                  : MediaQuery.of(context).size.height,
              child: Column(
                children: <Widget>[
                  // TODO replace all this with a simple underline
                  // This is just to show the underline
                ],
              ),
            ),
          ),
        ),
        Center(
          child: Padding(
            padding: const EdgeInsets.only(top: 20, left: 50, right: 50),
            child: Container(
              width: MediaQuery.of(context).orientation == Orientation.portrait
                  ? MediaQuery.of(context).size.width
                  : MediaQuery.of(context).size.height,
              height: 60,
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.center,
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: <Widget>[
                  RichText(
                    text: TextSpan(
                      text: (_selectedOnce
                              ? _getDateandAge[0]
                              : "year of birth") +
                          " " * 4,
                      style: DefaultTextStyle.of(context).style,
                      children: <TextSpan>[
                        TextSpan(
                            text: _selectedOnce
                                ? "Age: " + _getDateandAge[1]
                                : "",
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
        ),
        Center(
          child: Padding(
            padding: EdgeInsets.only(
              top: 20,
              // TODO replace it with meaningful code
              // This padding-left is hacked in landscape mode
              // left: 72,
              left: (MediaQuery.of(context).orientation == Orientation.portrait)
                  ? 50
                  : 72,
            ),
            child: Row(
              children: <Widget>[
                // Date picker will open on tap
                GestureDetector(
                  onTap: () => _selectDate(context),
                  child: Container(
                    width: (MediaQuery.of(context).orientation ==
                            Orientation.portrait
                        ? MediaQuery.of(context).size.width - 100
                        : MediaQuery.of(context).size.height),
                    height: 60,
                    color: Colors.transparent,
                    // the following is to debug the date picker onclick gestureDetector tap region
                    // color: Colors.black12,
                  ),
                ),
                //
                IconButton(
                  icon: Icon(Icons.info_outline),
                  onPressed: _showDisclaimer,
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }

  void _showDisclaimer() {
    // Show Snackbar message
    // That the date of birth is used only to compute the Age
    // And age is stored
    final snackBar = SnackBar(
      duration: Duration(seconds: 2, milliseconds: 500),
      backgroundColor: Colors.black,
      content: Text(
        'Disclaimer! The [date of birth] is used only to determine the [Age]',
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
  }

  List<String> get _getDateandAge {
    final selectedDate =
        Provider.of<AuthStore>(context, listen: false).selectedDate;
    final date = DateUtils.getDate(selectedDate);
    final ageStr = DateUtils.getAge(selectedDate);
    return [date, "$ageStr"];
  }
}
