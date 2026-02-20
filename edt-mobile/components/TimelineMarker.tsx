import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { Colors, Typography } from '@/theme';

interface Props {
  time: string;
  status?: 'completed' | 'current' | 'upcoming';
  isFirst?: boolean;
  isLast?: boolean;
}

export function TimelineMarker({ time, status = 'upcoming', isFirst, isLast }: Props) {
  // Format time compactly: "08:00" → "0800"
  const compactTime = time.replace(':', '');

  return (
    <View style={styles.container}>
      {/* Time column */}
      <View style={styles.timeCol}>
        <Text style={styles.timeText}>{compactTime}</Text>
      </View>

      {/* Dot + line column */}
      <View style={styles.dotCol}>
        {/* Top line */}
        <View
          style={[
            styles.line,
            isFirst && { backgroundColor: 'transparent' },
            status === 'completed' && { backgroundColor: Colors.primary + '4D' },
          ]}
        />

        {/* Dot */}
        {status === 'completed' ? (
          <View style={[styles.dot, styles.dotCompleted]}>
            <Ionicons name="checkmark" size={10} color={Colors.white} />
          </View>
        ) : status === 'current' ? (
          <View style={[styles.dot, styles.dotCurrent]}>
            <View style={styles.dotCurrentInner} />
          </View>
        ) : (
          <View style={[styles.dot, styles.dotUpcoming]} />
        )}

        {/* Bottom line */}
        <View
          style={[
            styles.line,
            isLast && { backgroundColor: 'transparent' },
          ]}
        />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    position: 'absolute',
    left: 0,
    top: 0,
    bottom: 0,
    width: 48,
    flexDirection: 'row',
  },
  timeCol: {
    width: 28,
    alignItems: 'center',
    justifyContent: 'center',
  },
  timeText: {
    fontSize: 9,
    fontFamily: 'PlusJakartaSans_600SemiBold',
    color: Colors.textTertiary,
    letterSpacing: 0.5,
  },
  dotCol: {
    width: 20,
    alignItems: 'center',
  },
  line: {
    flex: 1,
    width: 2,
    backgroundColor: Colors.timelineLine,
  },
  dot: {
    width: 14,
    height: 14,
    borderRadius: 7,
    alignItems: 'center',
    justifyContent: 'center',
  },
  dotCompleted: {
    backgroundColor: Colors.primary,
  },
  dotCurrent: {
    borderWidth: 2,
    borderColor: Colors.primary,
    backgroundColor: Colors.surface,
  },
  dotCurrentInner: {
    width: 6,
    height: 6,
    borderRadius: 3,
    backgroundColor: Colors.primary,
  },
  dotUpcoming: {
    borderWidth: 2,
    borderColor: Colors.timelineDotMuted,
    backgroundColor: Colors.surface,
  },
});
