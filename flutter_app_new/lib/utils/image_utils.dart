import '../core/constants/api_constants.dart';

/// 图片URL工具类
class ImageUtils {
  /// 将图片路径转换为完整URL
  ///
  /// 如果已经是完整URL（http/https开头），则直接返回
  /// 如果是相对路径（/images/...），则拼接基础URL
  static String getImageUrl(String? imagePath) {
    if (imagePath == null || imagePath.isEmpty) {
      return '';
    }

    // 如果已经是完整URL，直接返回
    if (imagePath.startsWith('http://') || imagePath.startsWith('https://')) {
      return imagePath;
    }

    // 如果是相对路径，拼接基础URL
    if (imagePath.startsWith('/')) {
      return '${ApiConstants.baseImageUrl}$imagePath';
    }

    // 其他情况，拼接基础URL和斜杠
    return '${ApiConstants.baseImageUrl}/$imagePath';
  }
}
