import { Button, InputNumber, Space, Table, Tag } from 'antd';
import type { TableColumnsType } from 'antd';
import { useEffect, useState } from 'react';
import { getRecentEvents } from '../api/securityAnalytics';
import PageState from '../components/PageState';
import type { FaceEvent } from '../types/api';
import { formatDateTime, formatPercent } from '../utils/format';

const columns: TableColumnsType<FaceEvent> = [
  { title: '事件时间', dataIndex: 'event_time', render: formatDateTime, width: 190 },
  {
    title: '类型',
    dataIndex: 'event_type',
    width: 110,
    render: (value: FaceEvent['event_type']) => (
      <Tag color={value === 'unknown' ? 'orange' : 'blue'}>
        {value === 'unknown' ? '陌生人' : '已知人员'}
      </Tag>
    ),
  },
  { title: '人员', dataIndex: 'person_name', render: (value) => value ?? '-' },
  { title: '摄像头', dataIndex: 'camera_name' },
  {
    title: '置信度',
    dataIndex: 'confidence_score',
    render: formatPercent,
    width: 110,
  },
  { title: '抓拍路径', dataIndex: 'snapshot_path', render: (value) => value ?? '-' },
];

export default function RecentEventsPage() {
  const [limit, setLimit] = useState(50);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [rows, setRows] = useState<FaceEvent[]>([]);
  const [total, setTotal] = useState(0);

  const load = () => {
    const controller = new AbortController();
    setLoading(true);
    setError(null);
    getRecentEvents(limit, controller.signal)
      .then((data) => {
        setRows(data.items);
        setTotal(data.total);
      })
      .catch((err: Error) => setError(err.message))
      .finally(() => setLoading(false));
    return () => controller.abort();
  };

  useEffect(load, [limit]);

  return (
    <div className="page-stack">
      <div className="toolbar">
        <Space wrap>
          <span>显示条数</span>
          <InputNumber min={1} max={500} value={limit} onChange={(value) => setLimit(value ?? 50)} />
          <Button onClick={load}>刷新</Button>
        </Space>
        <span className="toolbar-meta">总计 {total} 条</span>
      </div>
      <PageState loading={loading} error={error} onRetry={load} empty={!rows.length} />
      {!loading && !error && rows.length > 0 && (
        <Table<FaceEvent>
          rowKey="event_id"
          columns={columns}
          dataSource={rows}
          pagination={{ pageSize: 10, showSizeChanger: true }}
          scroll={{ x: 980 }}
        />
      )}
    </div>
  );
}
