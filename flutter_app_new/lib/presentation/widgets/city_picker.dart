import 'package:flutter/material.dart';
import '../../data/constants/china_cities.dart';

/// 省市区三级联动选择器（优化版）
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

class _CityPickerState extends State<CityPicker> with SingleTickerProviderStateMixin {
  String? _selectedProvince;
  String? _selectedCity;
  String? _selectedDistrict;
  TabController? _tabController;

  @override
  void initState() {
    super.initState();
    _selectedProvince = widget.initialProvince;
    _selectedCity = widget.initialCity;
    _selectedDistrict = widget.initialDistrict;
    _tabController = TabController(length: 3, vsync: this);
  }

  @override
  void dispose() {
    _tabController?.dispose();
    super.dispose();
  }

  TabController get _controller {
    _tabController ??= TabController(length: 3, vsync: this);
    return _tabController!;
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        // 标题栏
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            const Text(
              '选择地区',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            IconButton(
              icon: const Icon(Icons.close),
              onPressed: () => Navigator.pop(context),
              padding: EdgeInsets.zero,
              constraints: const BoxConstraints(),
            ),
          ],
        ),
        const Divider(height: 1),
        const SizedBox(height: 16),

        // Tab选项卡
        Container(
          decoration: BoxDecoration(
            color: Colors.grey[100],
            borderRadius: BorderRadius.circular(8),
          ),
          child: TabBar(
            controller: _controller,
            indicatorSize: TabBarIndicatorSize.tab,
            indicator: BoxDecoration(
              color: Colors.orange,
              borderRadius: BorderRadius.circular(8),
            ),
            labelColor: Colors.grey[600],
            unselectedLabelColor: Colors.grey[600],
            tabs: const [
              Tab(text: '省份'),
              Tab(text: '城市'),
              Tab(text: '区县'),
            ],
            onTap: (index) {
              // Tab切换逻辑：只有选择了前面的才能切换到后面
              if (index == 1 && _selectedProvince == null) return;
              if (index == 2 && (_selectedProvince == null || _selectedCity == null)) return;
            },
          ),
        ),
        const SizedBox(height: 16),

        // Tab内容
        SizedBox(
          height: 200,
          child: TabBarView(
            controller: _controller,
            physics: const NeverScrollableScrollPhysics(),
            children: [
              _buildProvinceList(),
              _buildCityList(),
              _buildDistrictList(),
            ],
          ),
        ),

        const SizedBox(height: 16),

        // 确认按钮
        Row(
          children: [
            Expanded(
              child: OutlinedButton(
                onPressed: () => Navigator.pop(context),
                style: OutlinedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(vertical: 12),
                ),
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
                        // 只调用回调，由回调中的sheetContext来pop
                        widget.onConfirm(
                          _selectedProvince!,
                          _selectedCity!,
                          _selectedDistrict!,
                        );
                      }
                    : null,
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.orange,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 12),
                ),
                child: const Text('确定'),
              ),
            ),
          ],
        ),
      ],
    );
  }

  /// 省份列表
  Widget _buildProvinceList() {
    final provinces = chinaCities.keys.toList();

    if (provinces.isEmpty) {
      return const Center(child: Text('暂无数据'));
    }

    return ListView.builder(
      itemCount: provinces.length,
      itemBuilder: (context, index) {
        final province = provinces[index];
        final isSelected = _selectedProvince == province;

        return ListTile(
          title: Text(
            province,
            style: TextStyle(
              color: isSelected ? Colors.orange : Colors.black,
              fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
            ),
          ),
          trailing: isSelected ? const Icon(Icons.check, color: Colors.orange) : null,
          selected: isSelected,
          selectedTileColor: Colors.orange[50],
          onTap: () {
            setState(() {
              _selectedProvince = province;
              _selectedCity = null;
              _selectedDistrict = null;
            });
            _controller.animateTo(1);
          },
        );
      },
    );
  }

  /// 城市列表
  Widget _buildCityList() {
    if (_selectedProvince == null) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.location_city, size: 48, color: Colors.grey[400]),
            const SizedBox(height: 16),
            Text(
              '请先选择省份',
              style: TextStyle(color: Colors.grey[600]),
            ),
          ],
        ),
      );
    }

    final cities = chinaCities[_selectedProvince!]!.keys.toList();

    return ListView.builder(
      itemCount: cities.length,
      itemBuilder: (context, index) {
        final city = cities[index];
        final isSelected = _selectedCity == city;

        return ListTile(
          title: Text(
            city,
            style: TextStyle(
              color: isSelected ? Colors.orange : Colors.black,
              fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
            ),
          ),
          trailing: isSelected ? const Icon(Icons.check, color: Colors.orange) : null,
          selected: isSelected,
          selectedTileColor: Colors.orange[50],
          onTap: () {
            setState(() {
              _selectedCity = city;
              _selectedDistrict = null;
            });
            _controller.animateTo(2);
          },
        );
      },
    );
  }

  /// 区县列表
  Widget _buildDistrictList() {
    if (_selectedProvince == null || _selectedCity == null) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.location_on, size: 48, color: Colors.grey[400]),
            const SizedBox(height: 16),
            Text(
              '请先选择省份和城市',
              style: TextStyle(color: Colors.grey[600]),
            ),
          ],
        ),
      );
    }

    final districts = chinaCities[_selectedProvince!]![_selectedCity!]!;

    return ListView.builder(
      itemCount: districts.length,
      itemBuilder: (context, index) {
        final district = districts[index];
        final isSelected = _selectedDistrict == district;

        return ListTile(
          title: Text(
            district,
            style: TextStyle(
              color: isSelected ? Colors.orange : Colors.black,
              fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
            ),
          ),
          trailing: isSelected ? const Icon(Icons.check, color: Colors.orange) : null,
          selected: isSelected,
          selectedTileColor: Colors.orange[50],
          onTap: () {
            // 只调用回调，由回调中的sheetContext来pop
            print('🔍 District tapped: $_selectedProvince, $_selectedCity, $district');
            widget.onConfirm(
              _selectedProvince!,
              _selectedCity!,
              district,
            );
          },
        );
      },
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
    builder: (sheetContext) {
      return Container(
        height: 400,
        decoration: const BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
        ),
        padding: const EdgeInsets.all(16),
        child: CityPicker(
          initialProvince: initialProvince,
          initialCity: initialCity,
          initialDistrict: initialDistrict,
          onConfirm: (province, city, district) {
            // 使用sheetContext来返回数据
            print('🔍 onConfirm called: $province, $city, $district');
            final result = <String, String>{
              'province': province,
              'city': city,
              'district': district,
            };
            print('🔍 Popping with result: $result');
            Navigator.of(sheetContext).pop(result);
          },
        ),
      );
    },
  );
}
