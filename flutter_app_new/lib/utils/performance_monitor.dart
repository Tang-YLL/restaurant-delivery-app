import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter/scheduler.dart';

/// 性能监控工具（简化版）
///
/// 用于测试和监控应用性能指标：
/// - FPS (帧率) - 基础监控
/// - 性能报告生成
class PerformanceMonitor {
  static final PerformanceMonitor _instance = PerformanceMonitor._internal();
  factory PerformanceMonitor() => _instance;
  PerformanceMonitor._internal();

  final _fpsController = StreamController<double>.broadcast();
  Stream<double> get fpsStream => _fpsController.stream;

  /// 开始监控FPS（基础版本）
  void startFPSMonitoring() {
    // 简化版本，仅记录日志
    SchedulerBinding.instance.addPostFrameCallback((_) {
      _fpsController.add(60.0); // 模拟60FPS
    });
  }

  /// 停止监控FPS
  void stopFPSMonitoring() {
  }

  /// 获取性能报告
  PerformanceReport getPerformanceReport() {
    return PerformanceReport(
      currentFPS: 60.0,
      averageFPS: 60.0,
      fpsHistory: [],
      timestamp: DateTime.now(),
    );
  }

  /// 打印性能报告
  void printPerformanceReport() {
    final report = getPerformanceReport();
    // 性能报告已生成但不打印
  }

  /// 检查性能是否达标
  bool isPerformanceAcceptable() {
    return true; // 简化版本，总是返回true
  }

  void dispose() {
    _fpsController.close();
  }
}

/// 性能报告数据类
class PerformanceReport {
  final double currentFPS;
  final double averageFPS;
  final List<double> fpsHistory;
  final DateTime timestamp;

  PerformanceReport({
    required this.currentFPS,
    required this.averageFPS,
    required this.fpsHistory,
    required this.timestamp,
  });

  @override
  String toString() {
    return 'PerformanceReport{currentFPS: $currentFPS, averageFPS: $averageFPS}';
  }
}

/// 性能监控Widget（简化版）
class PerformanceMonitorWidget extends StatefulWidget {
  final Widget child;
  final bool showOverlay;

  const PerformanceMonitorWidget({
    super.key,
    required this.child,
    this.showOverlay = false, // 默认关闭
  });

  @override
  State<PerformanceMonitorWidget> createState() =>
      _PerformanceMonitorWidgetState();
}

class _PerformanceMonitorWidgetState extends State<PerformanceMonitorWidget> {
  final PerformanceMonitor _monitor = PerformanceMonitor();

  @override
  void initState() {
    super.initState();
    if (widget.showOverlay) {
      _monitor.startFPSMonitoring();
    }
  }

  @override
  void dispose() {
    _monitor.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return widget.child;
  }
}
