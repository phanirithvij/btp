import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

class AuthStore extends ChangeNotifier {
  // Store username, pass, dob, etc..
  final emailController = TextEditingController();
  final passwordController = TextEditingController();

  void tryAuth(String type) {
    if (type == "login") {
    } else {}

    print("Email is ${emailController.text}");
    print("Passwd is ${passwordController.text}");
  }

  @override
  void dispose() {
    emailController.dispose();
    super.dispose();
  }
}
