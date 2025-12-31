import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/address_provider.dart';
import '../../data/models/address.dart';

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
  late TextEditingController _provinceController;
  late TextEditingController _cityController;
  late TextEditingController _districtController;
  late TextEditingController _detailController;
  late String _addressType;
  bool _isDefault = false;

  @override
  void initState() {
    super.initState();
    _nameController = TextEditingController(text: widget.address?.contactName ?? '');
    _phoneController = TextEditingController(text: widget.address?.contactPhone ?? '');
    _provinceController = TextEditingController(text: widget.address?.province ?? '');
    _cityController = TextEditingController(text: widget.address?.city ?? '');
    _districtController = TextEditingController(text: widget.address?.district ?? '');
    _detailController = TextEditingController(text: widget.address?.detailAddress ?? '');
    _addressType = widget.address?.addressType ?? 'other';
    _isDefault = widget.address?.isDefault ?? false;
  }

  @override
  void dispose() {
    _nameController.dispose();
    _phoneController.dispose();
    _provinceController.dispose();
    _cityController.dispose();
    _districtController.dispose();
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
          padding: const EdgeInsets.all(16),
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
            Row(
              children: [
                Expanded(
                  child: TextFormField(
                    controller: _provinceController,
                    decoration: const InputDecoration(
                      labelText: '省份',
                      hintText: '省',
                      border: OutlineInputBorder(),
                    ),
                    validator: (value) {
                      if (value == null || value.trim().isEmpty) {
                        return '请选择省份';
                      }
                      return null;
                    },
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: TextFormField(
                    controller: _cityController,
                    decoration: const InputDecoration(
                      labelText: '城市',
                      hintText: '市',
                      border: OutlineInputBorder(),
                    ),
                    validator: (value) {
                      if (value == null || value.trim().isEmpty) {
                        return '请选择城市';
                      }
                      return null;
                    },
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: TextFormField(
                    controller: _districtController,
                    decoration: const InputDecoration(
                      labelText: '区县',
                      hintText: '区',
                      border: OutlineInputBorder(),
                    ),
                    validator: (value) {
                      if (value == null || value.trim().isEmpty) {
                        return '请选择区县';
                      }
                      return null;
                    },
                  ),
                ),
              ],
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
    if (!_formKey.currentState!.validate()) {
      return;
    }

    final provider = context.read<AddressProvider>();
    final isEdit = widget.address != null;

    final address = Address(
      id: widget.address?.id ?? 'address_${DateTime.now().millisecondsSinceEpoch}',
      userId: 'current_user_id', // 从AuthProvider获取
      contactName: _nameController.text.trim(),
      contactPhone: _phoneController.text.trim(),
      province: _provinceController.text.trim(),
      city: _cityController.text.trim(),
      district: _districtController.text.trim(),
      detailAddress: _detailController.text.trim(),
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
