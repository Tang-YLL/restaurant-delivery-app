import 'package:flutter/foundation.dart';
import 'dart:convert';
import '../../data/models/address.dart';
import '../../services/api_service.dart';
import '../../core/utils/storage_util.dart';

/// AddressProvider - 地址状态管理
class AddressProvider with ChangeNotifier {
  List<Address> _addresses = [];
  bool _isLoading = false;
  String? _errorMessage;
  Address? _selectedAddress;

  List<Address> get addresses => _addresses;
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;
  Address? get selectedAddress => _selectedAddress;

  /// 获取默认地址
  Address? get defaultAddress {
    try {
      return _addresses.firstWhere((address) => address.isDefault);
    } catch (e) {
      return null;
    }
  }

  /// 加载地址列表
  Future<void> loadAddresses() async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      // 从本地存储读取
      final cachedData = await StorageUtil.getString('addressBox', 'addresses');
      if (cachedData != null) {
        final jsonData = jsonDecode(cachedData);
        _addresses = (jsonData as List)
            .map((item) => Address.fromJson(item as Map<String, dynamic>))
            .toList();
        notifyListeners();
      }

      // 尝试从API获取最新数据（如果失败则使用本地缓存）
      try {
        final response = await ApiService.get('/addresses');

        if (response.success && response.data != null) {
          final apiAddresses = (response.data! as List)
              .map((item) => Address.fromJson(item as Map<String, dynamic>))
              .toList();

          // 如果API返回数据，使用API数据
          if (apiAddresses.isNotEmpty) {
            _addresses = apiAddresses;

            // 缓存到本地
            await StorageUtil.setString(
              'addressBox',
              'addresses',
              jsonEncode(_addresses.map((a) => a.toJson()).toList()),
            );
          }
        }
      } catch (apiError) {
        // API调用失败，使用本地缓存数据
        debugPrint('API调用失败，使用本地缓存: $apiError');
      }
    } catch (e) {
      _errorMessage = '加载地址失败: $e';
      debugPrint('加载地址失败: $e');
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  /// 添加地址
  Future<bool> addAddress(Address address) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      // 如果是默认地址,取消其他默认地址
      if (address.isDefault) {
        for (var i = 0; i < _addresses.length; i++) {
          _addresses[i] = _addresses[i].copyWith(isDefault: false);
        }
      }

      // 先保存到本地
      _addresses.add(address);
      await _saveToCache();
      _isLoading = false;
      notifyListeners();

      // 尝试同步到服务器（失败也返回成功，因为本地已保存）
      try {
        final response = await ApiService.post('/addresses', data: address.toJson());
        if (response.success && response.data != null) {
          // 如果服务器返回了新地址（比如生成了ID），更新本地地址
          final serverAddress = Address.fromJson(response.data!);
          final index = _addresses.indexWhere((a) => a.id == address.id);
          if (index >= 0) {
            _addresses[index] = serverAddress;
            await _saveToCache();
          }
        }
      } catch (apiError) {
        debugPrint('同步地址到服务器失败: $apiError');
      }

      return true;
    } catch (e) {
      _errorMessage = '添加地址失败: $e';
      debugPrint('添加地址失败: $e');
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  /// 更新地址
  Future<bool> updateAddress(Address address) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      final index = _addresses.indexWhere((a) => a.id == address.id);

      if (index >= 0) {
        // 如果设置为默认地址,取消其他默认地址
        if (address.isDefault) {
          for (var i = 0; i < _addresses.length; i++) {
            _addresses[i] = _addresses[i].copyWith(isDefault: false);
          }
        }

        // 先更新本地
        _addresses[index] = address;
        await _saveToCache();
        _isLoading = false;
        notifyListeners();

        // 尝试同步到服务器
        try {
          final response = await ApiService.put(
            '/addresses/${address.id}',
            data: address.toJson(),
          );
          if (!response.success) {
            debugPrint('同步地址更新到服务器失败: ${response.message}');
          }
        } catch (apiError) {
          debugPrint('同步地址更新到服务器失败: $apiError');
        }

        return true;
      }

      _errorMessage = '地址不存在';
      _isLoading = false;
      notifyListeners();
      return false;
    } catch (e) {
      _errorMessage = '更新地址失败: $e';
      debugPrint('更新地址失败: $e');
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  /// 删除地址
  Future<bool> deleteAddress(String addressId) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      // 先从本地删除
      _addresses.removeWhere((a) => a.id == addressId);

      // 如果删除的是选中的地址,清除选中状态
      if (_selectedAddress?.id == addressId) {
        _selectedAddress = null;
      }

      await _saveToCache();
      _isLoading = false;
      notifyListeners();

      // 尝试同步到服务器
      try {
        ApiService.delete('/addresses/$addressId');
      } catch (apiError) {
        debugPrint('同步地址删除到服务器失败: $apiError');
      }

      return true;
    } catch (e) {
      _errorMessage = '删除地址失败: $e';
      debugPrint('删除地址失败: $e');
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  /// 设置默认地址
  Future<bool> setDefaultAddress(String addressId) async {
    final index = _addresses.indexWhere((a) => a.id == addressId);
    if (index < 0) return false;

    // 更新本地状态
    for (var i = 0; i < _addresses.length; i++) {
      _addresses[i] = _addresses[i].copyWith(
        isDefault: _addresses[i].id == addressId,
        updatedAt: DateTime.now(),
      );
    }

    await _saveToCache();
    notifyListeners();

    // 同步到服务器
    try {
      final response = await ApiService.put(
        '/addresses/$addressId/set-default',
      );
      return response.success;
    } catch (e) {
      debugPrint('设置默认地址失败: $e');
      return false;
    }
  }

  /// 选择地址(用于下单)
  void selectAddress(Address? address) {
    _selectedAddress = address;
    notifyListeners();
  }

  /// 清除选中地址
  void clearSelectedAddress() {
    _selectedAddress = null;
    notifyListeners();
  }

  /// 保存到缓存
  Future<void> _saveToCache() async {
    await StorageUtil.setString(
      'addressBox',
      'addresses',
      jsonEncode(_addresses.map((a) => a.toJson()).toList()),
    );
  }

  /// 清除错误信息
  void clearError() {
    _errorMessage = null;
    notifyListeners();
  }
}
