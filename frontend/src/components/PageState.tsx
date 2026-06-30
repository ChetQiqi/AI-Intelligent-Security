import { Alert, Button, Empty, Spin } from 'antd';

interface PageStateProps {
  loading?: boolean;
  error?: string | null;
  empty?: boolean;
  emptyText?: string;
  onRetry?: () => void;
}

export default function PageState({
  loading,
  error,
  empty,
  emptyText = '暂无数据',
  onRetry,
}: PageStateProps) {
  if (loading) {
    return (
      <div className="state-box">
        <Spin size="large" />
      </div>
    );
  }

  if (error) {
    return (
      <Alert
        type="error"
        showIcon
        message="请求失败"
        description={error}
        action={
          onRetry ? (
            <Button size="small" danger onClick={onRetry}>
              重试
            </Button>
          ) : undefined
        }
      />
    );
  }

  if (empty) {
    return (
      <div className="state-box">
        <Empty description={emptyText} />
      </div>
    );
  }

  return null;
}
