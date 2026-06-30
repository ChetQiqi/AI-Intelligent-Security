import {
  BarChartOutlined,
  DashboardOutlined,
  DatabaseOutlined,
  SearchOutlined,
  TeamOutlined,
} from '@ant-design/icons';
import { Layout, Menu, Typography } from 'antd';
import type { MenuProps } from 'antd';
import type { ReactNode } from 'react';

export type AppRoute = 'dashboard' | 'recent' | 'unknown' | 'nl2sql';

const { Header, Sider, Content } = Layout;

const menuItems: MenuProps['items'] = [
  { key: 'dashboard', icon: <DashboardOutlined />, label: '系统总览' },
  { key: 'recent', icon: <DatabaseOutlined />, label: '最近事件' },
  { key: 'unknown', icon: <TeamOutlined />, label: '陌生人事件' },
  { key: 'nl2sql', icon: <SearchOutlined />, label: 'NL2SQL 查数' },
];

const routeTitle: Record<AppRoute, string> = {
  dashboard: '系统总览 Dashboard',
  recent: '最近事件',
  unknown: '陌生人事件',
  nl2sql: 'NL2SQL 查数助手',
};

interface AppLayoutProps {
  activeRoute: AppRoute;
  onRouteChange: (route: AppRoute) => void;
  children: ReactNode;
}

export default function AppLayout({
  activeRoute,
  onRouteChange,
  children,
}: AppLayoutProps) {
  return (
    <Layout className="app-shell">
      <Sider breakpoint="lg" collapsedWidth={72} width={248} className="app-sider">
        <div className="brand">
          <div className="brand-mark">
            <BarChartOutlined />
          </div>
          <div className="brand-copy">
            <span className="brand-title">AI 安防分析平台</span>
            <span className="brand-subtitle">Security Event Center</span>
          </div>
        </div>
        <Menu
          mode="inline"
          selectedKeys={[activeRoute]}
          items={menuItems}
          onClick={({ key }) => onRouteChange(key as AppRoute)}
          className="app-menu"
        />
      </Sider>
      <Layout>
        <Header className="app-header">
          <div>
            <Typography.Text className="header-kicker">实时事件分析工作台</Typography.Text>
            <Typography.Title level={3} className="header-title">
              {routeTitle[activeRoute]}
            </Typography.Title>
          </div>
          <div className="header-status">
            <span className="status-dot" />
            后端 API: {import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8001/api/v1'}
          </div>
        </Header>
        <Content className="app-content">{children}</Content>
      </Layout>
    </Layout>
  );
}
