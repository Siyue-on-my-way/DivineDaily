import React from 'react';
import './DataTable.css';

interface Column<T> {
  key: string;
  title: string;
  width?: string;
  render?: (value: any, record: T, index: number) => React.ReactNode;
  align?: 'left' | 'center' | 'right';
}

interface DataTableProps<T> {
  columns: Column<T>[];
  data: T[];
  rowKey: string | ((record: T) => string);
  loading?: boolean;
  empty?: React.ReactNode;
  onRowClick?: (record: T, index: number) => void;
  className?: string;
}

export function DataTable<T extends Record<string, any>>({
  columns,
  data,
  rowKey,
  loading = false,
  empty,
  onRowClick,
  className = '',
}: DataTableProps<T>) {
  const getRowKey = (record: T, index: number): string => {
    if (typeof rowKey === 'function') {
      return rowKey(record);
    }
    return record[rowKey] || String(index);
  };

  if (loading) {
    return (
      <div className="data-table-loading">
        <div className="data-table-loading__spinner" />
        <div className="data-table-loading__text">加载中...</div>
      </div>
    );
  }

  if (data.length === 0) {
    return (
      <div className="data-table-empty">
        {empty || (
          <>
            <div className="data-table-empty__icon">📋</div>
            <div className="data-table-empty__text">暂无数据</div>
          </>
        )}
      </div>
    );
  }

  return (
    <div className={`data-table-wrapper ${className}`}>
      <table className="data-table">
        <thead className="data-table__head">
          <tr>
            {columns.map((column) => (
              <th
                key={column.key}
                className={`data-table__th data-table__th--${column.align || 'left'}`}
                style={{ width: column.width }}
              >
                {column.title}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="data-table__body">
          {data.map((record, index) => (
            <tr
              key={getRowKey(record, index)}
              className={`data-table__row ${onRowClick ? 'data-table__row--clickable' : ''}`}
              onClick={() => onRowClick?.(record, index)}
            >
              {columns.map((column) => (
                <td
                  key={column.key}
                  className={`data-table__td data-table__td--${column.align || 'left'}`}
                >
                  {column.render
                    ? column.render(record[column.key], record, index)
                    : record[column.key]}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

