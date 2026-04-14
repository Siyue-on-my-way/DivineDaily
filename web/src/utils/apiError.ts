export function extractApiErrorMessage(error: any): string {
  const data = error?.response?.data;

  if (!data) {
    return error?.message || '请求失败';
  }

  if (typeof data === 'string') {
    return data;
  }

  const candidates = [
    data.detail,
    data.error_message,
    data.error,
    data.message,
  ];

  for (const item of candidates) {
    if (typeof item === 'string' && item.trim()) {
      return item.trim();
    }
    if (item && typeof item === 'object') {
      if (typeof item.message === 'string' && item.message.trim()) {
        return item.message.trim();
      }
      if (typeof item.detail === 'string' && item.detail.trim()) {
        return item.detail.trim();
      }
    }
  }

  return error?.message || '请求失败';
}

export function formatApiErrorMessage(error: any, fallback = '请求失败'): string {
  const status = error?.response?.status;
  const message = extractApiErrorMessage(error) || fallback;
  if (status) {
    return `[${status}] ${message}`;
  }
  return message || fallback;
}
