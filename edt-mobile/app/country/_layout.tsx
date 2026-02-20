import { Stack } from 'expo-router';

export default function CountryLayout() {
  return (
    <Stack screenOptions={{ headerShown: false }}>
      <Stack.Screen name="select" />
      <Stack.Screen name="preferences" />
      <Stack.Screen name="allocations" />
      <Stack.Screen name="itinerary" />
    </Stack>
  );
}
