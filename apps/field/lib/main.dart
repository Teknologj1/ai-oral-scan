import 'package:flutter/material.dart';

void main() => runApp(const OralScanFieldApp());

class OralScanFieldApp extends StatelessWidget {
  const OralScanFieldApp({super.key});

  @override
  Widget build(BuildContext context) => MaterialApp(
        title: 'AI Oral Scan',
        theme: ThemeData(colorSchemeSeed: const Color(0xFF0F766E), useMaterial3: true),
        home: const FieldHomePage(),
      );
}

class FieldHomePage extends StatelessWidget {
  const FieldHomePage({super.key});

  @override
  Widget build(BuildContext context) => Scaffold(
        appBar: AppBar(title: const Text('AI Oral Scan · Campo')),
        body: const Center(
          child: Padding(
            padding: EdgeInsets.all(24),
            child: Text(
              'Aplicativo de campo em preparação.\n\nNão registre dados reais nesta versão. A IA clínica está desativada.',
              textAlign: TextAlign.center,
            ),
          ),
        ),
      );
}
