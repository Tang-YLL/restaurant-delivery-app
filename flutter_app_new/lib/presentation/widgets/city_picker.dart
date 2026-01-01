import 'package:flutter/material.dart';
import '../../data/constants/china_cities.dart';

/// 省市区三级联动选择器
class CityPicker extends StatefulWidget {
  final String? initialProvince;
  final String? initialCity;
  final String? initialDistrict;
  final Function(String province, String city, String district) onConfirm;

  const CityPicker({
    super.key,
    this.initialProvince,
    this.initialCity,
    this.initialDistrict,
    required this.onConfirm,
  });

  @override
  State<CityPicker> createState() => _CityPickerState();
}

class _CityPickerState extends State<CityPicker> {
  String? _selectedProvince;
  String? _selectedCity;
  String? _selectedDistrict;

  @override
  void initState() {
    super.initState();
    _selectedProvince = widget.initialProvince;
    _selectedCity = widget.initialCity;
    _selectedDistrict = widget.initialDistrict;
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        // 省份选择
        _buildPicker(
          label: '省份',
          value: _selectedProvince,
          items: chinaCities.keys.toList(),
          onChanged: (value) {
            setState(() {
              _selectedProvince = value;
              _selectedCity = null;
              _selectedDistrict = null;
            });
          },
        ),
        if (_selectedProvince != null) ...[
          const SizedBox(height: 16),
          // 城市选择
          _buildPicker(
            label: '城市',
            value: _selectedCity,
            items: chinaCities[_selectedProvince!]!.keys.toList(),
            onChanged: (value) {
              setState(() {
                _selectedCity = value;
                _selectedDistrict = null;
              });
            },
          ),
        ],
        if (_selectedCity != null) ...[
          const SizedBox(height: 16),
          // 区县选择
          _buildPicker(
            label: '区县',
            value: _selectedDistrict,
            items: chinaCities[_selectedProvince!]![_selectedCity!]!,
            onChanged: (value) {
              setState(() {
                _selectedDistrict = value;
              });
            },
          ),
        ],
        const SizedBox(height: 24),
        // 确认按钮
        Row(
          children: [
            Expanded(
              child: OutlinedButton(
                onPressed: () => Navigator.pop(context),
                child: const Text('取消'),
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: ElevatedButton(
                onPressed: _selectedProvince != null &&
                        _selectedCity != null &&
                        _selectedDistrict != null
                    ? () {
                        widget.onConfirm(
                          _selectedProvince!,
                          _selectedCity!,
                          _selectedDistrict!,
                        );
                        Navigator.pop(context);
                      }
                    : null,
                child: const Text('确定'),
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildPicker({
    required String label,
    required String? value,
    required List<String> items,
    required void Function(String?) onChanged,
  }) {
    return InputDecorator(
      decoration: InputDecoration(
        labelText: label,
        border: const OutlineInputBorder(),
        contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 16),
      ),
      child: DropdownButtonHideUnderline(
        child: DropdownButton<String>(
          value: value,
          isExpanded: true,
          hint: Text('请选择$label'),
          items: items.map((String item) {
            return DropdownMenuItem<String>(
              value: item,
              child: Text(item),
            );
          }).toList(),
          onChanged: onChanged,
        ),
      ),
    );
  }
}

/// 显示省市区选择器对话框
Future<Map<String, String>?> showCityPicker(
  BuildContext context, {
  String? initialProvince,
  String? initialCity,
  String? initialDistrict,
}) async {
  return await showModalBottomSheet<Map<String, String>>(
    context: context,
    isScrollControlled: true,
    backgroundColor: Colors.transparent,
    builder: (context) {
      return Container(
        decoration: const BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
        ),
        padding: const EdgeInsets.all(24),
        child: CityPicker(
          initialProvince: initialProvince,
          initialCity: initialCity,
          initialDistrict: initialDistrict,
          onConfirm: (province, city, district) {
            Navigator.of(context).pop({
              'province': province,
              'city': city,
              'district': district,
            });
          },
        ),
      );
    },
  );
}
