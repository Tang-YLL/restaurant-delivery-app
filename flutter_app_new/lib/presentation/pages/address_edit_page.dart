import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/address_provider.dart';
import '../../data/models/address.dart';
import '../widgets/city_picker.dart';

/// 地址编辑页面
class AddressEditPage extends StatefulWidget {
  final Address? address; // 如果为null,则为添加新地址

  const AddressEditPage({
    super.key,
    this.address,
  });

  @override
  State<AddressEditPage> createState() => _AddressEditPageState();
}

class _AddressEditPageState extends State<AddressEditPage> {
  final _formKey = GlobalKey<FormState>();
  late TextEditingController _nameController;
  late TextEditingController _phoneController;
  String? _province;
  String? _city;
  String? _district;
  late TextEditingController _detailController;
  late String _addressType;
  bool _isDefault = false;
  bool _hasTriedSave = false; // 是否尝试过保存

  @override
  void initState() {
    super.initState();
    _nameController = TextEditingController(text: widget.address?.contactName ?? '');
    _phoneController = TextEditingController(text: widget.address?.contactPhone ?? '');
    _province = widget.address?.province;
    _city = widget.address?.city;
    _district = widget.address?.district;
    _detailController = TextEditingController(text: widget.address?.detailAddress ?? '');
    _addressType = widget.address?.addressType ?? 'other';
    _isDefault = widget.address?.isDefault ?? false;
  }

  @override
  void dispose() {
    _nameController.dispose();
    _phoneController.dispose();
    _detailController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final isEdit = widget.address != null;

    return Scaffold(
      appBar: AppBar(
        title: Text(isEdit ? '编辑地址' : '添加地址'),
      ),
      body: Form(
        key: _formKey,
        child: ListView(
          padding: const EdgeInsets.all(16).copyWith(bottom: 32),
          children: [
            // 联系人
            TextFormField(
              controller: _nameController,
              decoration: const InputDecoration(
                labelText: '联系人',
                hintText: '请输入联系人姓名',
                border: OutlineInputBorder(),
                prefixIcon: Icon(Icons.person),
              ),
              validator: (value) {
                if (value == null || value.trim().isEmpty) {
                  return '请输入联系人姓名';
                }
                return null;
              },
            ),

            const SizedBox(height: 16),

            // 联系电话
            TextFormField(
              controller: _phoneController,
              keyboardType: TextInputType.phone,
              decoration: const InputDecoration(
                labelText: '联系电话',
                hintText: '请输入联系电话',
                border: OutlineInputBorder(),
                prefixIcon: Icon(Icons.phone),
              ),
              validator: (value) {
                if (value == null || value.trim().isEmpty) {
                  return '请输入联系电话';
                }
                if (!RegExp(r'^1[3-9]\d{9}$').hasMatch(value.trim())) {
                  return '请输入正确的手机号码';
                }
                return null;
              },
            ),

            const SizedBox(height: 16),

            // 省市区选择
            InkWell(
              onTap: () async {
                print('🔍 Opening city picker, current: $_province, $_city, $_district');
                final result = await showCityPicker(
                  context,
                  initialProvince: _province,
                  initialCity: _city,
                  initialDistrict: _district,
                );
                print('🔍 City picker returned: $result');
                if (result != null) {
                  print('🔍 Updating state with: ${result['province']}, ${result['city']}, ${result['district']}');
                  setState(() {
                    _province = result['province'];
                    _city = result['city'];
                    _district = result['district'];
                  });
                  print('🔍 State updated, new values: $_province, $_city, $_district');
                } else {
                  print('🔍 Result is null, no update');
                }
              },
              child: InputDecorator(
                decoration: InputDecoration(
                  labelText: '省市区',
                  hintText: '请选择省市区',
                  border: const OutlineInputBorder(),
                  prefixIcon: const Icon(Icons.location_city),
                  errorText: _hasTriedSave && (_province == null || _city == null || _district == null)
                      ? '请选择省市区'
                      : null,
                ),
                child: Text(
                  _province != null && _city != null && _district != null
                      ? '$_province $_city $_district'
                      : '请选择省市区',
                  style: TextStyle(
                    color: _province != null ? Colors.black : Colors.grey,
                  ),
                ),
              ),
            ),

            const SizedBox(height: 16),

            // 详细地址
            TextFormField(
              controller: _detailController,
              maxLines: 3,
              decoration: const InputDecoration(
                labelText: '详细地址',
                hintText: '街道、楼牌号等详细信息',
                border: OutlineInputBorder(),
                prefixIcon: Icon(Icons.location_on),
              ),
              validator: (value) {
                if (value == null || value.trim().isEmpty) {
                  return '请输入详细地址';
                }
                return null;
              },
            ),

            const SizedBox(height: 16),

            // 地址类型
            Text(
              '地址类型',
              style: Theme.of(context).textTheme.titleSmall,
            ),
            const SizedBox(height: 8),
            Wrap(
              spacing: 8,
              children: [
                _buildAddressTypeChip('家', 'home', Icons.home),
                _buildAddressTypeChip('公司', 'company', Icons.business),
                _buildAddressTypeChip('其他', 'other', Icons.more_horiz),
              ],
            ),

            const SizedBox(height: 16),

            // 设为默认地址
            SwitchListTile(
              title: const Text('设为默认地址'),
              subtitle: const Text('下单时默认使用此地址'),
              value: _isDefault,
              onChanged: (value) {
                setState(() {
                  _isDefault = value;
                });
              },
            ),

            const SizedBox(height: 24),

            // 保存按钮
            ElevatedButton(
              onPressed: _saveAddress,
              style: ElevatedButton.styleFrom(
                padding: const EdgeInsets.symmetric(vertical: 16),
              ),
              child: Text(isEdit ? '保存' : '添加'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildAddressTypeChip(String label, String value, IconData icon) {
    final isSelected = _addressType == value;
    return FilterChip(
      label: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 16),
          const SizedBox(width: 4),
          Text(label),
        ],
      ),
      selected: isSelected,
      onSelected: (selected) {
        setState(() {
          _addressType = value;
        });
      },
      selectedColor: Theme.of(context).colorScheme.primaryContainer,
    );
  }

  Future<void> _saveAddress() async {
    // 设置尝试保存标志，显示验证错误
    setState(() {
      _hasTriedSave = true;
    });

    // 验证省市区
    if (_province == null || _city == null || _district == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('请选择省市区')),
      );
      return;
    }

    // 验证表单
    if (!_formKey.currentState!.validate()) {
      return;
    }

    // 二次验证：确保所有必填字段都有值
    final name = _nameController.text.trim();
    final phone = _phoneController.text.trim();
    final detail = _detailController.text.trim();

    if (name.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('请输入联系人姓名')),
      );
      return;
    }

    if (phone.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('请输入联系电话')),
      );
      return;
    }

    if (detail.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('请输入详细地址')),
      );
      return;
    }

    final provider = context.read<AddressProvider>();
    final isEdit = widget.address != null;

    final address = Address(
      id: widget.address?.id ?? 'address_${DateTime.now().millisecondsSinceEpoch}',
      userId: 'current_user_id', // TODO: 从AuthProvider获取
      contactName: name,
      contactPhone: phone,
      province: _province!,
      city: _city!,
      district: _district!,
      detailAddress: detail,
      isDefault: _isDefault,
      addressType: _addressType,
      createdAt: widget.address?.createdAt ?? DateTime.now(),
      updatedAt: DateTime.now(),
    );

    bool success;
    if (isEdit) {
      success = await provider.updateAddress(address);
    } else {
      success = await provider.addAddress(address);
    }

    if (mounted) {
      if (success) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(isEdit ? '保存成功' : '添加成功')),
        );
        Navigator.pop(context, true);
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(provider.errorMessage ?? '操作失败')),
        );
      }
    }
  }
}
