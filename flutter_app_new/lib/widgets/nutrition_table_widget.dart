import 'package:flutter/material.dart';

class NutritionTableWidget extends StatelessWidget {
  final Map<String, dynamic> nutritionData;

  const NutritionTableWidget({
    super.key,
    required this.nutritionData,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.all(16),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '营养成分表',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 16),
            if (nutritionData['serving_size'] != null)
              Text('份量: ${nutritionData['serving_size']}'),
            const SizedBox(height: 16),
            _buildNutritionTable(),
          ],
        ),
      ),
    );
  }

  Widget _buildNutritionTable() {
    final nutrients = [
      {'name': '热量', 'value': nutritionData['calories'], 'unit': 'kcal'},
      {'name': '蛋白质', 'value': nutritionData['protein'], 'unit': 'g'},
      {'name': '脂肪', 'value': nutritionData['fat'], 'unit': 'g'},
      {'name': '碳水化合物', 'value': nutritionData['carbohydrates'], 'unit': 'g'},
      {'name': '钠', 'value': nutritionData['sodium'], 'unit': 'mg'},
    ];

    return Table(
      border: TableBorder.all(color: Colors.grey[300]!),
      columnWidths: const {
        0: FlexColumnWidth(2),
        1: FlexColumnWidth(1),
        2: FlexColumnWidth(1),
      },
      children: [
        TableRow(
          decoration: BoxDecoration(color: Colors.grey[100]),
          children: [
            _buildTableCell('营养成分', isHeader: true),
            _buildTableCell('含量', isHeader: true),
            _buildTableCell('单位', isHeader: true),
          ],
        ),
        ...nutrients.map((nutrient) {
          return TableRow(
            children: [
              _buildTableCell(nutrient['name'] as String),
              _buildTableCell((nutrient['value'] ?? '-').toString()),
              _buildTableCell(nutrient['unit'] as String),
            ],
          );
        }),
      ],
    );
  }

  Widget _buildTableCell(String text, {bool isHeader = false}) {
    return Padding(
      padding: const EdgeInsets.all(8),
      child: Text(
        text,
        style: TextStyle(
          fontWeight: isHeader ? FontWeight.bold : FontWeight.normal,
        ),
      ),
    );
  }
}
