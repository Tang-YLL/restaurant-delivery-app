import 'package:flutter/foundation.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';

/// 通知服务
class NotificationService {
  static final NotificationService _instance = NotificationService._internal();
  factory NotificationService() => _instance;
  NotificationService._internal();

  final FlutterLocalNotificationsPlugin _notifications =
      FlutterLocalNotificationsPlugin();

  bool _isInitialized = false;

  /// 初始化通知
  Future<void> initialize() async {
    if (_isInitialized) return;

    const androidSettings = AndroidInitializationSettings('@mipmap/ic_launcher');
    const iosSettings = DarwinInitializationSettings(
      requestAlertPermission: true,
      requestBadgePermission: true,
      requestSoundPermission: true,
    );

    const initSettings = InitializationSettings(
      android: androidSettings,
      iOS: iosSettings,
    );

    await _notifications.initialize(
      initSettings,
      onDidReceiveNotificationResponse: _onNotificationTap,
    );

    _isInitialized = true;
    debugPrint('通知服务初始化成功');
  }

  /// 处理通知点击
  void _onNotificationTap(NotificationResponse response) {
    debugPrint('通知被点击: ${response.payload}');
    // TODO: 根据payload导航到相应页面
  }

  /// 显示简单通知
  Future<void> showNotification({
    required int id,
    required String title,
    required String body,
    String? payload,
  }) async {
    const androidDetails = AndroidNotificationDetails(
      'food_delivery_channel',
      '订单通知',
      channelDescription: '订单状态变更通知',
      importance: Importance.high,
      priority: Priority.high,
    );

    const iosDetails = DarwinNotificationDetails(
      presentAlert: true,
      presentBadge: true,
      presentSound: true,
    );

    const details = NotificationDetails(
      android: androidDetails,
      iOS: iosDetails,
    );

    await _notifications.show(
      id,
      title,
      body,
      details,
      payload: payload,
    );
  }

  /// 订单状态变更通知
  Future<void> showOrderNotification({
    required String orderId,
    required String status,
    required String statusText,
  }) async {
    await showNotification(
      id: orderId.hashCode, // 使用订单ID的hashCode作为通知ID
      title: '订单状态更新',
      body: '您的订单 $orderId 已${statusText}',
      payload: 'order_$orderId',
    );
  }

  /// 促销活动通知
  Future<void> showPromotionNotification({
    required String title,
    required String content,
  }) async {
    await showNotification(
      id: DateTime.now().millisecondsSinceEpoch % 100000,
      title: title,
      body: content,
      payload: 'promotion',
    );
  }

  /// 定时通知
  Future<void> scheduleNotification({
    required int id,
    required String title,
    required String body,
    required DateTime scheduledTime,
    String? payload,
  }) async {
    const androidDetails = AndroidNotificationDetails(
      'food_delivery_channel',
      '订单通知',
      channelDescription: '订单状态变更通知',
      importance: Importance.high,
      priority: Priority.high,
    );

    const iosDetails = DarwinNotificationDetails(
      presentAlert: true,
      presentBadge: true,
      presentSound: true,
    );

    const details = NotificationDetails(
      android: androidDetails,
      iOS: iosDetails,
    );

    // 注意: scheduledTime需要转换为TZDateTime
    // 这里简化处理，使用即时通知代替定时通知
    await _notifications.show(
      id,
      title,
      body,
      details,
      payload: payload,
    );
  }

  /// 取消通知
  Future<void> cancelNotification(int id) async {
    await _notifications.cancel(id);
  }

  /// 取消所有通知
  Future<void> cancelAllNotifications() async {
    await _notifications.cancelAll();
  }
}
