import { UserDetail } from '../../types/user';
import './UserInfoCard.css';

interface UserInfoCardProps {
  user: UserDetail;
}

export default function UserInfoCard({ user }: UserInfoCardProps) {
  // 计算生肖
  const getZodiacAnimal = (birthDate?: string) => {
    if (!birthDate) return '-';
    const year = new Date(birthDate).getFullYear();
    const animals = ['鼠', '牛', '虎', '兔', '龙', '蛇', '马', '羊', '猴', '鸡', '狗', '猪'];
    return animals[(year - 4) % 12];
  };

  // 计算星座
  const getZodiacSign = (birthDate?: string) => {
    if (!birthDate) return '-';
    const date = new Date(birthDate);
    const month = date.getMonth() + 1;
    const day = date.getDate();
    
    const signs = [
      { name: '水瓶座', start: [1, 20], end: [2, 18] },
      { name: '双鱼座', start: [2, 19], end: [3, 20] },
      { name: '白羊座', start: [3, 21], end: [4, 19] },
      { name: '金牛座', start: [4, 20], end: [5, 20] },
      { name: '双子座', start: [5, 21], end: [6, 21] },
      { name: '巨蟹座', start: [6, 22], end: [7, 22] },
      { name: '狮子座', start: [7, 23], end: [8, 22] },
      { name: '处女座', start: [8, 23], end: [9, 22] },
      { name: '天秤座', start: [9, 23], end: [10, 23] },
      { name: '天蝎座', start: [10, 24], end: [11, 22] },
      { name: '射手座', start: [11, 23], end: [12, 21] },
      { name: '摩羯座', start: [12, 22], end: [1, 19] },
    ];

    for (const sign of signs) {
      const [startMonth, startDay] = sign.start;
      const [endMonth, endDay] = sign.end;
      
      if (
        (month === startMonth && day >= startDay) ||
        (month === endMonth && day <= endDay)
      ) {
        return sign.name;
      }
    }
    
    return '摩羯座';
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return '-';
    return new Date(dateString).toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const formatBirthDate = (dateString?: string) => {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return `${date.getFullYear()}年${date.getMonth() + 1}月${date.getDate()}日`;
  };

  return (
    <div className="user-info-card">
      <div className="card-header">
        <h2>用户基本信息</h2>
      </div>
      <div className="card-body">
        <div className="user-avatar-section">
          <div className="avatar">
            {user.avatar ? (
              <img src={user.avatar} alt={user.username} />
            ) : (
              <div className="avatar-placeholder">
                {user.username.charAt(0).toUpperCase()}
              </div>
            )}
          </div>
        </div>
        <div className="user-info-section">
          <div className="info-row">
            <label>用户名:</label>
            <span>{user.username}</span>
          </div>
          <div className="info-row">
            <label>邮箱:</label>
            <span>{user.email || '-'}</span>
          </div>
          <div className="info-row">
            <label>手机:</label>
            <span>{user.phone || '-'}</span>
          </div>
          <div className="info-row">
            <label>昵称:</label>
            <span>{user.nickname || '-'}</span>
          </div>
          <div className="info-row">
            <label>出生日期:</label>
            <span>{formatBirthDate(user.birth_date)}</span>
          </div>
          <div className="info-row">
            <label>生肖:</label>
            <span>{user.animal || getZodiacAnimal(user.birth_date)}</span>
          </div>
          <div className="info-row">
            <label>星座:</label>
            <span>{user.zodiac_sign || getZodiacSign(user.birth_date)}</span>
          </div>
          <div className="info-row">
            <label>角色:</label>
            <span className={`role-badge ${user.role}`}>
              {user.role === 'admin' ? '管理员' : '普通用户'}
            </span>
          </div>
          <div className="info-row">
            <label>状态:</label>
            <span className={`status-badge ${user.status === 1 ? 'active' : 'inactive'}`}>
              {user.status === 1 ? '正常' : '禁用'}
            </span>
          </div>
          <div className="info-row">
            <label>注册时间:</label>
            <span>{formatDate(user.created_at)}</span>
          </div>
          <div className="info-row">
            <label>最后登录:</label>
            <span>{formatDate(user.last_login_at)}</span>
          </div>
        </div>
      </div>
    </div>
  );
}

