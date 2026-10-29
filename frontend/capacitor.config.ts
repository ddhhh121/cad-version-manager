import type { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.cad.manager',
  appName: 'CAD版本管理器',
  webDir: 'dist',
  server: {
    // 允许用户在首次启动时配置服务器地址
    androidScheme: 'https',
  },
  android: {
    allowMixedContent: true,
    backgroundColor: '#1a1a2e',
  },
  plugins: {
    SplashScreen: {
      launchShowDuration: 2000,
      backgroundColor: '#1a1a2e',
      showSpinner: true,
      spinnerColor: '#ffffff',
    },
  },
};

export default config;
