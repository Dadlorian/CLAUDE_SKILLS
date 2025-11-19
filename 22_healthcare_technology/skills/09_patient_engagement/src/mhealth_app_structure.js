/**
 * React Native mHealth App Structure
 * Base structure for cross-platform mobile health application
 */

import React, { useState, useEffect } from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import AsyncStorage from '@react-native-async-storage/async-storage';

import LoginScreen from './screens/LoginScreen';
import DashboardScreen from './screens/DashboardScreen';
import MedicationScreen from './screens/MedicationScreen';
import HealthMetricsScreen from './screens/HealthMetricsScreen';
import EducationScreen from './screens/EducationScreen';
import ProfileScreen from './screens/ProfileScreen';

const Stack = createNativeStackNavigator();
const Tab = createBottomTabNavigator();

function AppNavigator() {
  const [isLoggedIn, setIsLoggedIn] = useState(null);
  const [user, setUser] = useState(null);

  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    try {
      const token = await AsyncStorage.getItem('authToken');
      const userData = await AsyncStorage.getItem('userData');

      if (token && userData) {
        setUser(JSON.parse(userData));
        setIsLoggedIn(true);
      } else {
        setIsLoggedIn(false);
      }
    } catch (error) {
      console.error('Error checking auth status:', error);
      setIsLoggedIn(false);
    }
  };

  const handleLogin = async (userData, token) => {
    await AsyncStorage.setItem('authToken', token);
    await AsyncStorage.setItem('userData', JSON.stringify(userData));
    setUser(userData);
    setIsLoggedIn(true);
  };

  const handleLogout = async () => {
    await AsyncStorage.removeItem('authToken');
    await AsyncStorage.removeItem('userData');
    setUser(null);
    setIsLoggedIn(false);
  };

  if (isLoggedIn === null) {
    return <LoadingScreen />;
  }

  return (
    <NavigationContainer>
      {isLoggedIn ? (
        <AuthenticatedNav user={user} onLogout={handleLogout} />
      ) : (
        <Stack.Navigator
          screenOptions={{ headerShown: false }}
        >
          <Stack.Screen name="Login">
            {(props) => <LoginScreen {...props} onLogin={handleLogin} />}
          </Stack.Screen>
        </Stack.Navigator>
      )}
    </NavigationContainer>
  );
}

function AuthenticatedNav({ user, onLogout }) {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          let iconName;
          if (route.name === 'Dashboard') {
            iconName = focused ? 'home' : 'home-outline';
          } else if (route.name === 'Medications') {
            iconName = focused ? 'pill' : 'pill-outline';
          } else if (route.name === 'HealthMetrics') {
            iconName = focused ? 'heart' : 'heart-outline';
          } else if (route.name === 'Education') {
            iconName = focused ? 'book' : 'book-outline';
          } else if (route.name === 'Profile') {
            iconName = focused ? 'person' : 'person-outline';
          }
          return <Icon name={iconName} size={size} color={color} />;
        },
        tabBarActiveTintColor: '#007AFF',
        tabBarInactiveTintColor: '#999',
        headerShown: true
      })}
    >
      <Tab.Screen
        name="Dashboard"
        component={DashboardScreen}
        options={{ title: 'My Health' }}
      />
      <Tab.Screen
        name="Medications"
        component={MedicationScreen}
        options={{ title: 'Medications' }}
      />
      <Tab.Screen
        name="HealthMetrics"
        component={HealthMetricsScreen}
        options={{ title: 'Health Metrics' }}
      />
      <Tab.Screen
        name="Education"
        component={EducationScreen}
        options={{ title: 'Education' }}
      />
      <Tab.Screen
        name="Profile"
        component={ProfileScreen}
        options={{
          title: 'Profile',
          headerRight: () => (
            <LogoutButton onLogout={onLogout} />
          )
        }}
      />
    </Tab.Navigator>
  );
}

function LogoutButton({ onLogout }) {
  return (
    <TouchableOpacity onPress={onLogout} style={{ marginRight: 10 }}>
      <Text style={{ color: '#007AFF' }}>Logout</Text>
    </TouchableOpacity>
  );
}

function LoadingScreen() {
  return (
    <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
      <ActivityIndicator size="large" color="#007AFF" />
    </View>
  );
}

export default AppNavigator;
