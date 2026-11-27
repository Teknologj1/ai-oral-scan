import 'package:flutter_test/flutter_test.dart';
import 'package:ai_oral_scan_field/main.dart';
import 'package:flutter/material.dart';

void main() {
  testWidgets('shows the field app safety message', (tester) async {
    await tester.pumpWidget(const OralScanFieldApp());
    expect(find.text('AI Oral Scan · Campo'), findsOneWidget);
    expect(find.textContaining('Não registre dados reais nesta versão.'), findsOneWidget);
  });
}
