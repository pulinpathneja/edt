import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, FlatList, Pressable, Image, Alert } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useWishlistStore } from '@/stores/wishlistStore';
import { resetDemo } from '@/services/demoSeed';
import { Colors, Typography, Spacing, Radius } from '@/theme';
import type { WishlistItemData } from '@/services/wishlistApi';

export default function ProfileScreen() {
  const insets = useSafeAreaInsets();
  const router = useRouter();
  const { items, isLoading, loadWishlist, removeItem } = useWishlistStore();
  const [resetting, setResetting] = useState(false);

  useEffect(() => {
    loadWishlist();
  }, []);

  const handleResetDemo = () => {
    Alert.alert(
      'Reset Demo',
      'This will clear all drafts and wishlist items. Continue?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Reset',
          style: 'destructive',
          onPress: async () => {
            setResetting(true);
            try {
              await resetDemo();
              await loadWishlist();
              router.replace('/');
            } catch {
              setResetting(false);
            }
          },
        },
      ],
    );
  };

  const renderItem = ({ item }: { item: WishlistItemData }) => (
    <View style={styles.wishlistCard}>
      {item.image_url ? (
        <Image source={{ uri: item.image_url }} style={styles.thumbnail} />
      ) : (
        <View style={[styles.thumbnail, styles.thumbnailPlaceholder]}>
          <Ionicons name="image-outline" size={24} color={Colors.textTertiary} />
        </View>
      )}
      <View style={styles.wishlistInfo}>
        <Text style={Typography.labelLarge} numberOfLines={1}>{item.poi_name}</Text>
        {item.city && (
          <Text style={[Typography.caption, { color: Colors.textSecondary }]}>
            {item.city}{item.country ? `, ${item.country}` : ''}
          </Text>
        )}
        {item.category && (
          <Text style={[Typography.caption, { color: Colors.textTertiary }]}>
            {item.category}
          </Text>
        )}
      </View>
      <Pressable onPress={() => removeItem(item.id)} hitSlop={8}>
        <Ionicons name="close-circle-outline" size={22} color={Colors.textTertiary} />
      </Pressable>
    </View>
  );

  return (
    <View style={[styles.container, { paddingTop: insets.top }]}>
      <View style={styles.header}>
        <Ionicons name="heart" size={24} color="#EF4444" />
        <Text style={Typography.titleLarge}>Wishlist</Text>
      </View>

      {items.length === 0 ? (
        <View style={styles.empty}>
          <Ionicons name="heart-outline" size={48} color={Colors.textTertiary} />
          <Text style={[Typography.titleSmall, { marginTop: Spacing.md }]}>
            No saved places yet
          </Text>
          <Text style={[Typography.bodySmall, { textAlign: 'center', marginTop: Spacing.xs, color: Colors.textSecondary }]}>
            Tap the heart icon on any activity to save it here
          </Text>
        </View>
      ) : (
        <FlatList
          data={items}
          keyExtractor={(item) => item.id}
          renderItem={renderItem}
          contentContainerStyle={styles.list}
          showsVerticalScrollIndicator={false}
        />
      )}

      {/* Reset Demo */}
      <Pressable onPress={handleResetDemo} disabled={resetting} style={styles.resetBtn}>
        <Ionicons name="refresh-outline" size={16} color={Colors.textTertiary} />
        <Text style={[Typography.caption, { color: Colors.textTertiary }]}>
          {resetting ? 'Resetting...' : 'Reset Demo'}
        </Text>
      </Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.background,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: Spacing.sm,
    paddingHorizontal: Spacing.lg,
    paddingVertical: Spacing.md,
  },
  empty: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: Spacing.xl,
  },
  list: {
    padding: Spacing.md,
    gap: Spacing.sm,
  },
  wishlistCard: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: Spacing.sm,
    backgroundColor: Colors.surface,
    borderRadius: Radius.lg,
    padding: Spacing.sm,
    borderWidth: 1,
    borderColor: Colors.border,
  },
  thumbnail: {
    width: 56,
    height: 56,
    borderRadius: Radius.md,
  },
  thumbnailPlaceholder: {
    backgroundColor: Colors.surfaceVariant,
    alignItems: 'center',
    justifyContent: 'center',
  },
  wishlistInfo: {
    flex: 1,
    gap: 2,
  },
  resetBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 6,
    paddingVertical: Spacing.md,
    marginBottom: Spacing.lg,
  },
});
