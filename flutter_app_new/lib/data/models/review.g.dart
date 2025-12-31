// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'review.dart';

// **************************************************************************
// TypeAdapterGenerator
// **************************************************************************

class ReviewAdapter extends TypeAdapter<Review> {
  @override
  final int typeId = 7;

  @override
  Review read(BinaryReader reader) {
    final numOfFields = reader.readByte();
    final fields = <int, dynamic>{
      for (int i = 0; i < numOfFields; i++) reader.readByte(): reader.read(),
    };
    return Review(
      id: fields[0] as String,
      orderId: fields[1] as String,
      productId: fields[2] as String,
      productName: fields[3] as String,
      productImage: fields[4] as String?,
      rating: fields[5] as int,
      content: fields[6] as String,
      images: (fields[7] as List).cast<String>(),
      userId: fields[8] as String,
      userName: fields[9] as String,
      userAvatar: fields[10] as String?,
      createdAt: fields[11] as DateTime,
    );
  }

  @override
  void write(BinaryWriter writer, Review obj) {
    writer
      ..writeByte(12)
      ..writeByte(0)
      ..write(obj.id)
      ..writeByte(1)
      ..write(obj.orderId)
      ..writeByte(2)
      ..write(obj.productId)
      ..writeByte(3)
      ..write(obj.productName)
      ..writeByte(4)
      ..write(obj.productImage)
      ..writeByte(5)
      ..write(obj.rating)
      ..writeByte(6)
      ..write(obj.content)
      ..writeByte(7)
      ..write(obj.images)
      ..writeByte(8)
      ..write(obj.userId)
      ..writeByte(9)
      ..write(obj.userName)
      ..writeByte(10)
      ..write(obj.userAvatar)
      ..writeByte(11)
      ..write(obj.createdAt);
  }

  @override
  int get hashCode => typeId.hashCode;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is ReviewAdapter &&
          runtimeType == other.runtimeType &&
          typeId == other.typeId;
}
