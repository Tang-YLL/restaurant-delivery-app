import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/address_provider.dart';
import '../../data/models/address.dart';
import 'address_edit_page.dart';
import '../widgets/empty_state_widget.dart';

/// 地址列表页面
class AddressListPage extends StatefulWidget {
  final bool isSelectMode; // 是否是选择地址模式

  const AddressListPage({
    super.key,
    this.isSelectMode = false,
  });

  @override
  State<AddressListPage> createState() => _AddressListPageState();
}

class _AddressListPageState extends State<AddressListPage> {
  @override
  void initState() {
    super.initState();
    Future.microtask(() {
      context.read<AddressProvider>().loadAddresses();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('收货地址'),
        actions: [
          if (widget.isSelectMode)
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('取消'),
            ),
        ],
      ),
      body: Consumer<AddressProvider>(
        builder: (context, provider, child) {
          if (provider.isLoading && provider.addresses.isEmpty) {
            return const Center(child: CircularProgressIndicator());
          }

          if (provider.addresses.isEmpty) {
            return RefreshIndicator(
              onRefresh: () => provider.loadAddresses(),
              child: SingleChildScrollView(
                physics: const AlwaysScrollableScrollPhysics(),
                child: EmptyStates.addresses(
                  onAdd: () => _addAddress(),
                ),
              ),
            );
          }

          return RefreshIndicator(
            onRefresh: () => provider.loadAddresses(),
            child: ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: provider.addresses.length,
              itemBuilder: (context, index) {
                final address = provider.addresses[index];
                return _buildAddressCard(address, provider);
              },
            ),
          );
        },
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: _addAddress,
        child: const Icon(Icons.add),
      ),
    );
  }

  Widget _buildAddressCard(Address address, AddressProvider provider) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: InkWell(
        onTap: widget.isSelectMode
            ? () {
                provider.selectAddress(address);
                Navigator.pop(context, address);
              }
            : null,
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // 顶部: 联系人和标签
              Row(
                children: [
                  Text(
                    address.contactName,
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                  ),
                  const SizedBox(width: 12),
                  Text(
                    address.contactPhone,
                    style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                          color: Colors.grey[700],
                        ),
                  ),
                  const Spacer(),
                  if (address.isDefault)
                    Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 8,
                        vertical: 4,
                      ),
                      decoration: BoxDecoration(
                        color: Theme.of(context).colorScheme.primary,
                        borderRadius: BorderRadius.circular(4),
                      ),
                      child: Text(
                        '默认',
                        style: TextStyle(
                          color: Theme.of(context).colorScheme.onPrimary,
                          fontSize: 12,
                        ),
                      ),
                    ),
                ],
              ),

              const SizedBox(height: 12),

              // 地址
              Text(
                address.fullAddress,
                style: Theme.of(context).textTheme.bodyMedium,
              ),

              const SizedBox(height: 12),

              // 底部操作按钮
              if (!widget.isSelectMode)
                Row(
                  children: [
                    if (!address.isDefault)
                      TextButton.icon(
                        onPressed: () => _setDefault(address, provider),
                        icon: const Icon(Icons.radio_button_unchecked, size: 18),
                        label: const Text('设为默认'),
                        style: TextButton.styleFrom(
                          foregroundColor: Theme.of(context).colorScheme.primary,
                        ),
                      ),
                    const Spacer(),
                    TextButton.icon(
                      onPressed: () => _editAddress(address),
                      icon: const Icon(Icons.edit, size: 18),
                      label: const Text('编辑'),
                    ),
                    TextButton.icon(
                      onPressed: () => _deleteAddress(address, provider),
                      icon: const Icon(Icons.delete, size: 18),
                      label: const Text('删除'),
                      style: TextButton.styleFrom(
                        foregroundColor: Colors.red,
                      ),
                    ),
                  ],
                ),
            ],
          ),
        ),
      ),
    );
  }

  Future<void> _addAddress() async {
    final result = await Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => const AddressEditPage(),
      ),
    );

    if (result == true) {
      // 刷新列表
      context.read<AddressProvider>().loadAddresses();
    }
  }

  Future<void> _editAddress(Address address) async {
    final result = await Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => AddressEditPage(address: address),
      ),
    );

    if (result == true) {
      // 刷新列表
      context.read<AddressProvider>().loadAddresses();
    }
  }

  Future<void> _setDefault(Address address, AddressProvider provider) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('设置默认地址'),
        content: const Text('确定要将此地址设置为默认地址吗?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('取消'),
          ),
          TextButton(
            onPressed: () => Navigator.pop(context, true),
            child: const Text('确定'),
          ),
        ],
      ),
    );

    if (confirmed == true) {
      await provider.setDefaultAddress(address.id);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('已设置为默认地址')),
        );
      }
    }
  }

  Future<void> _deleteAddress(Address address, AddressProvider provider) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('删除地址'),
        content: const Text('确定要删除此地址吗?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('取消'),
          ),
          TextButton(
            onPressed: () => Navigator.pop(context, true),
            style: TextButton.styleFrom(foregroundColor: Colors.red),
            child: const Text('删除'),
          ),
        ],
      ),
    );

    if (confirmed == true) {
      final success = await provider.deleteAddress(address.id);
      if (mounted) {
        if (success) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('删除成功')),
          );
        } else {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text(provider.errorMessage ?? '删除失败')),
          );
        }
      }
    }
  }
}
